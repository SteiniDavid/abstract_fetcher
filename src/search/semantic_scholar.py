"""Semantic Scholar search adapter."""

import json
import logging
from datetime import date
from pathlib import Path

import requests

from .base import CachedSearchAdapter, Paper, TopicConfig
from ..utils.retry import retry_on_http_error, RateLimitError


logger = logging.getLogger(__name__)

# Semantic Scholar API
S2_API_BASE = "https://api.semanticscholar.org/graph/v1"
S2_FIELDS = "paperId,title,authors,year,venue,publicationTypes,externalIds,url,openAccessPdf,abstract,citationCount"


class SemanticScholarAdapter(CachedSearchAdapter):
    """Search adapter for Semantic Scholar API."""

    # Rate limiting: 100 requests per 5 minutes without API key
    RATE_LIMIT_DELAY = 3.1
    CACHE_PREFIX = "s2"
    CACHE_EXTENSION = ".json"

    def __init__(
        self,
        cache_dir: Path | None = None,
        api_key: str | None = None,
        timeout: float | None = None,
    ):
        super().__init__(cache_dir, timeout=timeout)
        self.api_key = api_key

    def _read_cache(self, cache_path: Path) -> dict | None:
        """Read and parse JSON cached data."""
        try:
            with open(cache_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def _write_cache(self, cache_path: Path, data: dict) -> None:
        """Write JSON data to cache file."""
        with open(cache_path, "w") as f:
            json.dump(data, f)

    def _build_queries(self, topic: TopicConfig) -> list[str]:
        """Build search queries from topic configuration."""
        queries = []

        # Primary query: must terms + any should term
        must_part = " ".join(f'"{term}"' for term in topic.must)

        # Query 1: must + distribution shift terms
        shift_terms = [t for t in topic.should if "shift" in t.lower()]
        if shift_terms:
            should_part = " | ".join(f'"{t}"' for t in shift_terms)
            queries.append(f"{must_part} ({should_part})")

        # Query 2: must + method terms
        method_terms = [t for t in topic.should if t.lower() in ("dagger", "behavioral cloning", "offline imitation")]
        if method_terms:
            should_part = " | ".join(f'"{t}"' for t in method_terms)
            queries.append(f"{must_part} ({should_part})")

        # Query 3: broad must terms only
        queries.append(must_part)

        # Query 4: any should term as main query
        for term in topic.should[:3]:  # Limit to avoid too many queries
            queries.append(f'"{term}" {must_part}')

        return queries[:4]  # Limit total queries

    def _search_query(self, query: str, limit: int = 50) -> list[dict]:
        """Execute a single search query."""
        # Check cache first
        cached = self._get_cached(query)
        if cached is not None:
            return cached.get("data", [])

        try:
            data = self._fetch_search_results(query, limit)
            # Cache the response
            self._set_cached(query, data)
            return data.get("data", [])
        except (requests.RequestException, RateLimitError) as e:
            logger.warning(f"S2 search failed for query '{query[:50]}...': {e}")
            return []

    @retry_on_http_error(max_attempts=3, min_wait=1.0, max_wait=30.0)
    def _fetch_search_results(self, query: str, limit: int) -> dict:
        """Fetch search results from API with retry logic."""
        # Rate limit
        self._rate_limit()

        # Build request
        headers = {}
        if self.api_key:
            headers["x-api-key"] = self.api_key

        params = {
            "query": query,
            "limit": limit,
            "fields": S2_FIELDS,
        }

        response = requests.get(
            f"{S2_API_BASE}/paper/search",
            params=params,
            headers=headers,
            timeout=self.timeout,
        )

        # Handle rate limit specially
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                f"Rate limit exceeded for Semantic Scholar API",
                retry_after=int(retry_after) if retry_after else None,
            )

        response.raise_for_status()
        return response.json()

    def _parse_paper(self, item: dict) -> Paper | None:
        """Parse S2 API response item into Paper."""
        try:
            # Extract external IDs
            ext_ids = item.get("externalIds", {}) or {}
            doi = ext_ids.get("DOI")
            arxiv_id = ext_ids.get("ArXiv")

            # Extract authors
            authors = [a.get("name", "Unknown") for a in item.get("authors", []) or []]

            # Extract PDF URL - prefer S2's openAccessPdf, fallback to arXiv
            pdf_url = None
            oa_pdf = item.get("openAccessPdf")
            if oa_pdf and isinstance(oa_pdf, dict):
                pdf_url = oa_pdf.get("url")

            # Fallback: construct arXiv PDF URL if we have an arXiv ID
            if not pdf_url and arxiv_id:
                pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

            # Build URL (prefer S2 URL)
            url = item.get("url", "")
            if not url and item.get("paperId"):
                url = f"https://www.semanticscholar.org/paper/{item['paperId']}"

            return Paper(
                title=item.get("title", "Untitled"),
                authors=authors,
                year=item.get("year") or 0,
                venue=item.get("venue"),
                doi=doi,
                arxiv_id=arxiv_id,
                url=url,
                pdf_url=pdf_url,
                abstract=item.get("abstract"),
                citation_count=item.get("citationCount"),
                source="semantic_scholar",
            )

        except (KeyError, TypeError) as e:
            logger.debug(f"Failed to parse S2 paper: {e}")
            return None

    def search(self, topic: TopicConfig, max_results: int = 100) -> list[Paper]:
        """Search for papers matching the topic configuration."""
        queries = self._build_queries(topic)
        all_papers = {}

        for query in queries:
            logger.debug(f"S2 query: {query}")
            results = self._search_query(query, limit=min(50, max_results))

            for item in results:
                paper = self._parse_paper(item)
                if paper and paper.year >= date.today().year - topic.recency_years:
                    # Use paperId or title as dedup key
                    key = item.get("paperId") or paper.title_normalized
                    if key not in all_papers:
                        all_papers[key] = paper

            if len(all_papers) >= max_results:
                break

        return list(all_papers.values())[:max_results]
