"""Base classes and types for paper search."""

from dataclasses import dataclass, field
from typing import Protocol
import re


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

    @classmethod
    def from_dict(cls, data: dict) -> "TopicConfig":
        """Create TopicConfig from YAML dict."""
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
        )


class SearchAdapter(Protocol):
    """Protocol for search adapters."""

    def search(self, topic: TopicConfig, max_results: int = 50) -> list[Paper]:
        """Search for papers matching the topic configuration."""
        ...
