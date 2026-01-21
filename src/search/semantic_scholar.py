"""Semantic Scholar search adapter."""

import hashlib
import json
import logging
import time
from pathlib import Path

import requests

from .base import Paper, TopicConfig


logger = logging.getLogger(__name__)

# Semantic Scholar API
S2_API_BASE = "https://api.semanticscholar.org/graph/v1"
S2_FIELDS = "paperId,title,authors,year,venue,publicationTypes,externalIds,url,openAccessPdf,abstract,citationCount"

# Rate limiting: 100 requests per 5 minutes without API key
RATE_LIMIT_DELAY = 3.1  # seconds between requests


class SemanticScholarAdapter:
    """Search adapter for Semantic Scholar API."""

    def __init__(self, cache_dir: Path | None = None, api_key: str | None = None):
        self.cache_dir = cache_dir
        self.api_key = api_key
        self._last_request_time = 0.0

        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)

    def _rate_limit(self):
        """Ensure we don't exceed rate limits."""
        elapsed = time.time() - self._last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        self._last_request_time = time.time()

    def _cache_key(self, query: str) -> str:
        """Generate cache key for a query."""
        return hashlib.sha256(query.encode()).hexdigest()[:16]

    def _get_cached(self, query: str) -> dict | None:
        """Get cached response if available."""
        if not self.cache_dir:
            return None

        cache_file = self.cache_dir / f"s2_{self._cache_key(query)}.json"
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    data = json.load(f)
                logger.debug(f"Cache hit for query: {query[:50]}...")
                return data
            except (json.JSONDecodeError, IOError):
                pass
        return None

    def _set_cached(self, query: str, data: dict):
        """Cache response data."""
        if not self.cache_dir:
            return

        cache_file = self.cache_dir / f"s2_{self._cache_key(query)}.json"
        try:
            with open(cache_file, "w") as f:
                json.dump(data, f)
        except IOError as e:
            logger.warning(f"Failed to cache response: {e}")

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

        try:
            response = requests.get(
                f"{S2_API_BASE}/paper/search",
                params=params,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            # Cache the response
            self._set_cached(query, data)

            return data.get("data", [])

        except requests.RequestException as e:
            logger.warning(f"S2 search failed for query '{query[:50]}...': {e}")
            return []

    def _parse_paper(self, item: dict) -> Paper | None:
        """Parse S2 API response item into Paper."""
        try:
            # Extract external IDs
            ext_ids = item.get("externalIds", {}) or {}
            doi = ext_ids.get("DOI")
            arxiv_id = ext_ids.get("ArXiv")

            # Extract authors
            authors = [a.get("name", "Unknown") for a in item.get("authors", []) or []]

            # Extract PDF URL
            pdf_url = None
            oa_pdf = item.get("openAccessPdf")
            if oa_pdf and isinstance(oa_pdf, dict):
                pdf_url = oa_pdf.get("url")

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
                if paper and paper.year >= 2024 - topic.recency_years:
                    # Use paperId or title as dedup key
                    key = item.get("paperId") or paper.title_normalized
                    if key not in all_papers:
                        all_papers[key] = paper

            if len(all_papers) >= max_results:
                break

        return list(all_papers.values())[:max_results]
