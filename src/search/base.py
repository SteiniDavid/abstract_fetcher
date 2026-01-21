"""Base classes and types for paper search."""

import hashlib
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol
import re

from ..config.schema import ConfigValidationError, validate_topic_config


logger = logging.getLogger(__name__)


@dataclass
class Paper:
    """Unified paper representation from any source."""

    title: str
    authors: list[str]
    year: int
    venue: str | None
    doi: str | None
    arxiv_id: str | None
    url: str
    pdf_url: str | None
    abstract: str | None
    citation_count: int | None
    source: str

    # Computed during ranking
    score: float = 0.0
    selected_reason: str = ""

    def __post_init__(self):
        # Normalize arxiv_id (remove version suffix for dedup)
        if self.arxiv_id:
            self.arxiv_id = re.sub(r"v\d+$", "", self.arxiv_id)

    @property
    def title_normalized(self) -> str:
        """Normalize title for deduplication."""
        # Lowercase, remove punctuation, collapse whitespace
        title = self.title.lower()
        title = re.sub(r"[^\w\s]", " ", title)
        title = re.sub(r"\s+", " ", title).strip()
        return title

    def safe_filename(self, max_length: int = 50) -> str:
        """Generate a safe filename from the paper title."""
        # Take first N chars of title, make safe
        safe = re.sub(r"[^\w\s-]", "", self.title)[:max_length]
        safe = re.sub(r"\s+", "_", safe).strip("_")

        # Add year and short ID
        short_id = ""
        if self.arxiv_id:
            short_id = self.arxiv_id.replace("/", "_").replace(".", "_")[:15]
        elif self.doi:
            short_id = self.doi.split("/")[-1][:15]
        else:
            short_id = str(hash(self.title))[:8]

        return f"{safe}_{self.year}_{short_id}"

    def to_dict(self, include_abstract: bool = False) -> dict:
        """Serialize paper to dictionary for JSON export."""
        data = {
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "venue": self.venue,
            "doi": self.doi,
            "arxiv_id": self.arxiv_id,
            "url": self.url,
            "pdf_url": self.pdf_url,
            "citation_count": self.citation_count,
            "source": self.source,
            "score": round(self.score, 2),
            "selected_reason": self.selected_reason,
        }
        if include_abstract:
            data["abstract"] = self.abstract
        return data


@dataclass
class TopicConfig:
    """Configuration for a search topic."""

    name: str
    must: list[str] = field(default_factory=list)
    should: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)
    recency_years: int = 10
    papers_per_day: int = 10
    require_pdf: bool = False
    extract_conclusion: bool = True
    venue_boost: list[str] = field(default_factory=list)
    diversity_keywords: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict, topic_key: str | None = None) -> "TopicConfig":
        """Create TopicConfig from YAML dict.

        Args:
            data: Dictionary containing topic configuration.
            topic_key: Optional key name for error messages.

        Returns:
            TopicConfig instance.

        Raises:
            ConfigValidationError: If validation fails.
        """
        # Validate input data
        validate_topic_config(data, topic_key)

        query = data.get("query", {})
        return cls(
            name=data["name"],
            must=query.get("must", []),
            should=query.get("should", []),
            exclude=query.get("exclude", []),
            recency_years=data.get("recency_years", 10),
            papers_per_day=data.get("papers_per_day", 10),
            require_pdf=data.get("require_pdf", False),
            extract_conclusion=data.get("extract_conclusion", True),
            venue_boost=data.get("venue_boost", []),
            diversity_keywords=data.get("diversity_keywords", []),
        )


class SearchAdapter(Protocol):
    """Protocol for search adapters."""

    def search(self, topic: TopicConfig, max_results: int = 50) -> list[Paper]:
        """Search for papers matching the topic configuration."""
        ...


class CachedSearchAdapter(ABC):
    """Base class for search adapters with caching and rate limiting.

    Provides common functionality:
    - Rate limiting between requests
    - Response caching with configurable file extension
    - Configurable request timeout
    """

    # Subclasses should set these
    RATE_LIMIT_DELAY: float = 3.0  # seconds between requests
    CACHE_PREFIX: str = "cache"  # prefix for cache files
    CACHE_EXTENSION: str = ".json"  # file extension for cache
    REQUEST_TIMEOUT: float = 30.0  # seconds to wait for response

    def __init__(self, cache_dir: Path | None = None, timeout: float | None = None):
        self.cache_dir = cache_dir
        self._last_request_time = 0.0
        self.timeout = timeout if timeout is not None else self.REQUEST_TIMEOUT

        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)

    def _rate_limit(self) -> None:
        """Ensure we don't exceed rate limits."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - elapsed)
        self._last_request_time = time.time()

    def _cache_key(self, query: str) -> str:
        """Generate cache key for a query."""
        return hashlib.sha256(query.encode()).hexdigest()[:16]

    def _cache_path(self, query: str) -> Path | None:
        """Get cache file path for a query."""
        if not self.cache_dir:
            return None
        return self.cache_dir / f"{self.CACHE_PREFIX}_{self._cache_key(query)}{self.CACHE_EXTENSION}"

    @abstractmethod
    def _read_cache(self, cache_path: Path) -> str | dict | None:
        """Read and parse cached data. Returns None if cache miss or error."""
        ...

    @abstractmethod
    def _write_cache(self, cache_path: Path, data: str | dict) -> None:
        """Write data to cache file."""
        ...

    def _get_cached(self, query: str) -> str | dict | None:
        """Get cached response if available."""
        cache_path = self._cache_path(query)
        if cache_path is None or not cache_path.exists():
            return None

        result = self._read_cache(cache_path)
        if result is not None:
            logger.debug(f"Cache hit for query: {query[:50]}...")
        return result

    def _set_cached(self, query: str, data: str | dict) -> None:
        """Cache response data."""
        cache_path = self._cache_path(query)
        if cache_path is None:
            return

        try:
            self._write_cache(cache_path, data)
        except IOError as e:
            logger.warning(f"Failed to cache response: {e}")

    @abstractmethod
    def search(self, topic: TopicConfig, max_results: int = 100) -> list[Paper]:
        """Search for papers matching the topic configuration."""
        ...
