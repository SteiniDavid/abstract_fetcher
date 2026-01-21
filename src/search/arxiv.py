"""arXiv search adapter."""

import logging
import re
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

import requests

from .base import CachedSearchAdapter, Paper, TopicConfig
from ..utils.retry import retry_on_http_error


logger = logging.getLogger(__name__)

# arXiv API
ARXIV_API_BASE = "https://export.arxiv.org/api/query"

# XML namespaces
NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}


class ArxivAdapter(CachedSearchAdapter):
    """Search adapter for arXiv API."""

    # Rate limiting: be polite to arXiv
    RATE_LIMIT_DELAY = 3.0
    CACHE_PREFIX = "arxiv"
    CACHE_EXTENSION = ".xml"

    def _read_cache(self, cache_path: Path) -> str | None:
        """Read cached XML data."""
        try:
            with open(cache_path) as f:
                return f.read()
        except IOError:
            return None

    def _write_cache(self, cache_path: Path, data: str) -> None:
        """Write XML data to cache file."""
        with open(cache_path, "w") as f:
            f.write(data)

    def _build_queries(self, topic: TopicConfig) -> list[str]:
        """Build arXiv search queries from topic configuration.

        arXiv search syntax:
        - ti:term - title contains term
        - abs:term - abstract contains term
        - all:term - all fields
        - AND, OR, ANDNOT for boolean
        - quotes for exact phrases
        """
        queries = []

        # Primary query: must terms in abstract
        must_parts = [f'abs:"{term}"' for term in topic.must]
        must_query = " AND ".join(must_parts)

        # Query 1: must + shift terms
        shift_terms = [t for t in topic.should if "shift" in t.lower()]
        if shift_terms:
            should_part = " OR ".join(f'abs:"{t}"' for t in shift_terms)
            queries.append(f"({must_query}) AND ({should_part})")

        # Query 2: must + method terms
        method_terms = ["DAgger", "behavioral cloning", "offline imitation"]
        method_found = [t for t in topic.should if any(m.lower() in t.lower() for m in method_terms)]
        if method_found:
            should_part = " OR ".join(f'abs:"{t}"' for t in method_found)
            queries.append(f"({must_query}) AND ({should_part})")

        # Query 3: just must terms
        queries.append(must_query)

        # Query 4: title search for key terms
        title_query = " OR ".join(f'ti:"{term}"' for term in topic.must + topic.should[:2])
        queries.append(title_query)

        return queries[:4]

    def _search_query(self, query: str, limit: int = 50) -> str:
        """Execute a single search query."""
        # Check cache first
        cached = self._get_cached(query)
        if cached is not None:
            return cached

        try:
            data = self._fetch_search_results(query, limit)
            # Cache the response
            self._set_cached(query, data)
            return data
        except requests.RequestException as e:
            logger.warning(f"arXiv search failed for query '{query[:50]}...': {e}")
            return ""

    @retry_on_http_error(max_attempts=3, min_wait=1.0, max_wait=30.0)
    def _fetch_search_results(self, query: str, limit: int) -> str:
        """Fetch search results from API with retry logic."""
        # Rate limit
        self._rate_limit()

        params = {
            "search_query": query,
            "start": 0,
            "max_results": limit,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }

        response = requests.get(
            ARXIV_API_BASE,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.text

    def _parse_entry(self, entry: ET.Element) -> Paper | None:
        """Parse arXiv Atom entry into Paper."""
        try:
            # Extract arXiv ID from id URL
            id_url = entry.find("atom:id", NS)
            if id_url is None or id_url.text is None:
                return None

            # Extract arxiv_id (e.g., "2301.12345" from "http://arxiv.org/abs/2301.12345v1")
            arxiv_id_match = re.search(r"arxiv\.org/abs/(.+?)(?:v\d+)?$", id_url.text)
            if not arxiv_id_match:
                return None
            arxiv_id = arxiv_id_match.group(1)

            # Title
            title_elem = entry.find("atom:title", NS)
            title = title_elem.text.strip() if title_elem is not None and title_elem.text else "Untitled"
            # Clean up newlines in title
            title = re.sub(r"\s+", " ", title)

            # Authors
            authors = []
            for author in entry.findall("atom:author", NS):
                name_elem = author.find("atom:name", NS)
                if name_elem is not None and name_elem.text:
                    authors.append(name_elem.text.strip())

            # Abstract
            abstract_elem = entry.find("atom:summary", NS)
            abstract = None
            if abstract_elem is not None and abstract_elem.text:
                abstract = re.sub(r"\s+", " ", abstract_elem.text.strip())

            # Published date (for year)
            published_elem = entry.find("atom:published", NS)
            year = 0
            if published_elem is not None and published_elem.text:
                year_match = re.match(r"(\d{4})", published_elem.text)
                if year_match:
                    year = int(year_match.group(1))

            # Primary category (venue proxy)
            primary_cat = entry.find("arxiv:primary_category", NS)
            venue = None
            if primary_cat is not None:
                venue = f"arXiv:{primary_cat.get('term', '')}"

            # DOI if available
            doi_elem = entry.find("arxiv:doi", NS)
            doi = doi_elem.text.strip() if doi_elem is not None and doi_elem.text else None

            # URLs
            url = f"https://arxiv.org/abs/{arxiv_id}"
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

            return Paper(
                title=title,
                authors=authors,
                year=year,
                venue=venue,
                doi=doi,
                arxiv_id=arxiv_id,
                url=url,
                pdf_url=pdf_url,
                abstract=abstract,
                citation_count=None,  # arXiv doesn't provide this
                source="arxiv",
            )

        except (KeyError, TypeError, AttributeError) as e:
            logger.debug(f"Failed to parse arXiv entry: {e}")
            return None

    def search(self, topic: TopicConfig, max_results: int = 100) -> list[Paper]:
        """Search for papers matching the topic configuration."""
        queries = self._build_queries(topic)
        all_papers = {}

        for query in queries:
            logger.debug(f"arXiv query: {query}")
            xml_response = self._search_query(query, limit=min(50, max_results))

            if not xml_response:
                continue

            try:
                root = ET.fromstring(xml_response)
            except ET.ParseError as e:
                logger.warning(f"Failed to parse arXiv XML: {e}")
                continue

            for entry in root.findall("atom:entry", NS):
                paper = self._parse_entry(entry)
                if paper and paper.year >= date.today().year - topic.recency_years:
                    # Use arxiv_id or title as dedup key
                    key = paper.arxiv_id or paper.title_normalized
                    if key not in all_papers:
                        all_papers[key] = paper

            if len(all_papers) >= max_results:
                break

        return list(all_papers.values())[:max_results]
