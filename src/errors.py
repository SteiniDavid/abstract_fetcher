"""Centralized error tracking for the paper digest pipeline."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ErrorCategory(Enum):
    """Categories of errors in the pipeline."""

    SEARCH = "search"
    DOWNLOAD = "download"
    EXTRACT = "extract"
    CONFIG = "config"


class ErrorSeverity(Enum):
    """Severity levels for errors."""

    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class PipelineError:
    """Structured error record for the pipeline."""

    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    source: str | None = None
    title: str | None = None
    error_type: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }
        if self.source:
            result["source"] = self.source
        if self.title:
            result["title"] = self.title
        if self.error_type:
            result["type"] = self.error_type
        if self.details:
            result["details"] = self.details
        return result

    def to_legacy_dict(self) -> dict[str, Any]:
        """Convert to legacy format for backwards compatibility with failures.json."""
        result: dict[str, Any] = {}
        if self.source:
            result["source"] = self.source
        if self.title:
            result["title"] = self.title
        if self.error_type:
            result["type"] = self.error_type
        result["error"] = self.message
        return result


class ErrorTracker:
    """Collects and summarizes errors throughout pipeline execution."""

    def __init__(self) -> None:
        self._errors: list[PipelineError] = []

    def add(
        self,
        category: ErrorCategory,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        source: str | None = None,
        title: str | None = None,
        error_type: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> PipelineError:
        """Add an error to the tracker.

        Args:
            category: The category of the error.
            message: Human-readable error message.
            severity: The severity level (default: ERROR).
            source: Source identifier (e.g., "semantic_scholar", "arxiv").
            title: Paper title if applicable.
            error_type: Type of error (e.g., "abstract", "timeout").
            details: Additional error details.

        Returns:
            The created PipelineError instance.
        """
        error = PipelineError(
            category=category,
            severity=severity,
            message=message,
            source=source,
            title=title,
            error_type=error_type,
            details=details or {},
        )
        self._errors.append(error)
        return error

    def add_search_error(
        self,
        source: str,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
    ) -> PipelineError:
        """Add a search-related error."""
        return self.add(
            category=ErrorCategory.SEARCH,
            message=message,
            severity=severity,
            source=source,
        )

    def add_download_error(
        self,
        title: str,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
    ) -> PipelineError:
        """Add a download-related error."""
        return self.add(
            category=ErrorCategory.DOWNLOAD,
            message=message,
            severity=severity,
            title=title,
        )

    def add_extract_error(
        self,
        title: str,
        message: str,
        error_type: str = "extract",
        severity: ErrorSeverity = ErrorSeverity.ERROR,
    ) -> PipelineError:
        """Add an extraction-related error."""
        return self.add(
            category=ErrorCategory.EXTRACT,
            message=message,
            severity=severity,
            title=title,
            error_type=error_type,
        )

    def add_config_error(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.CRITICAL,
    ) -> PipelineError:
        """Add a configuration-related error."""
        return self.add(
            category=ErrorCategory.CONFIG,
            message=message,
            severity=severity,
        )

    @property
    def errors(self) -> list[PipelineError]:
        """Get all recorded errors."""
        return self._errors.copy()

    def get_by_category(self, category: ErrorCategory) -> list[PipelineError]:
        """Get errors filtered by category."""
        return [e for e in self._errors if e.category == category]

    def get_by_severity(self, severity: ErrorSeverity) -> list[PipelineError]:
        """Get errors filtered by severity."""
        return [e for e in self._errors if e.severity == severity]

    @property
    def total_count(self) -> int:
        """Get total number of errors."""
        return len(self._errors)

    def has_critical(self) -> bool:
        """Check if any critical errors were recorded."""
        return any(e.severity == ErrorSeverity.CRITICAL for e in self._errors)

    def summary(self) -> dict[str, int]:
        """Get summary counts by category."""
        return {
            cat.value: len(self.get_by_category(cat))
            for cat in ErrorCategory
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert all errors to dictionary format."""
        return {
            "total": self.total_count,
            "summary": self.summary(),
            "errors": [e.to_dict() for e in self._errors],
        }

    def to_legacy_dict(self) -> dict[str, list[dict[str, Any]]]:
        """Convert to legacy failures.json format for backwards compatibility.

        Returns:
            Dictionary with keys "search", "download", "extract" containing
            lists of error dictionaries in the original format.
        """
        result: dict[str, list[dict[str, Any]]] = {
            "search": [],
            "download": [],
            "extract": [],
        }

        for error in self._errors:
            if error.category == ErrorCategory.SEARCH:
                result["search"].append(error.to_legacy_dict())
            elif error.category == ErrorCategory.DOWNLOAD:
                result["download"].append(error.to_legacy_dict())
            elif error.category == ErrorCategory.EXTRACT:
                result["extract"].append(error.to_legacy_dict())
            # CONFIG errors are not in legacy format

        return result

    def clear(self) -> None:
        """Clear all recorded errors."""
        self._errors.clear()
