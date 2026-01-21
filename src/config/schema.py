"""Configuration validation for topic configurations."""

from typing import Any


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""

    def __init__(self, message: str, field: str | None = None):
        super().__init__(message)
        self.field = field
        self.message = message

    def __str__(self) -> str:
        if self.field:
            return f"Config validation error in '{self.field}': {self.message}"
        return f"Config validation error: {self.message}"


def validate_topic_config(data: dict[str, Any], topic_key: str | None = None) -> None:
    """Validate a topic configuration dictionary.

    Args:
        data: The topic configuration dictionary to validate.
        topic_key: Optional key name for error messages.

    Raises:
        ConfigValidationError: If validation fails.
    """
    prefix = f"topic '{topic_key}'" if topic_key else "topic"

    # Required fields
    if "name" not in data:
        raise ConfigValidationError(
            f"{prefix} is missing required field 'name'",
            field="name",
        )

    if not isinstance(data["name"], str):
        raise ConfigValidationError(
            f"{prefix} 'name' must be a string, got {type(data['name']).__name__}",
            field="name",
        )

    if not data["name"].strip():
        raise ConfigValidationError(
            f"{prefix} 'name' cannot be empty",
            field="name",
        )

    # recency_years validation
    if "recency_years" in data:
        recency = data["recency_years"]
        if not isinstance(recency, int):
            raise ConfigValidationError(
                f"{prefix} 'recency_years' must be an integer, got {type(recency).__name__}",
                field="recency_years",
            )
        if recency < 1 or recency > 50:
            raise ConfigValidationError(
                f"{prefix} 'recency_years' must be between 1 and 50, got {recency}",
                field="recency_years",
            )

    # papers_per_day validation
    if "papers_per_day" in data:
        papers = data["papers_per_day"]
        if not isinstance(papers, int):
            raise ConfigValidationError(
                f"{prefix} 'papers_per_day' must be an integer, got {type(papers).__name__}",
                field="papers_per_day",
            )
        if papers < 1 or papers > 100:
            raise ConfigValidationError(
                f"{prefix} 'papers_per_day' must be between 1 and 100, got {papers}",
                field="papers_per_day",
            )

    # require_pdf validation
    if "require_pdf" in data:
        if not isinstance(data["require_pdf"], bool):
            raise ConfigValidationError(
                f"{prefix} 'require_pdf' must be a boolean, got {type(data['require_pdf']).__name__}",
                field="require_pdf",
            )

    # extract_conclusion validation
    if "extract_conclusion" in data:
        if not isinstance(data["extract_conclusion"], bool):
            raise ConfigValidationError(
                f"{prefix} 'extract_conclusion' must be a boolean, got {type(data['extract_conclusion']).__name__}",
                field="extract_conclusion",
            )

    # query validation
    if "query" in data:
        query = data["query"]
        if not isinstance(query, dict):
            raise ConfigValidationError(
                f"{prefix} 'query' must be a dictionary, got {type(query).__name__}",
                field="query",
            )

        # Validate query lists
        for list_field in ("must", "should", "exclude"):
            if list_field in query:
                if not isinstance(query[list_field], list):
                    raise ConfigValidationError(
                        f"{prefix} 'query.{list_field}' must be a list, got {type(query[list_field]).__name__}",
                        field=f"query.{list_field}",
                    )
                for i, item in enumerate(query[list_field]):
                    if not isinstance(item, str):
                        raise ConfigValidationError(
                            f"{prefix} 'query.{list_field}[{i}]' must be a string, got {type(item).__name__}",
                            field=f"query.{list_field}[{i}]",
                        )

    # venue_boost validation
    if "venue_boost" in data:
        if not isinstance(data["venue_boost"], list):
            raise ConfigValidationError(
                f"{prefix} 'venue_boost' must be a list, got {type(data['venue_boost']).__name__}",
                field="venue_boost",
            )
        for i, item in enumerate(data["venue_boost"]):
            if not isinstance(item, str):
                raise ConfigValidationError(
                    f"{prefix} 'venue_boost[{i}]' must be a string, got {type(item).__name__}",
                    field=f"venue_boost[{i}]",
                )

    # diversity_keywords validation
    if "diversity_keywords" in data:
        if not isinstance(data["diversity_keywords"], list):
            raise ConfigValidationError(
                f"{prefix} 'diversity_keywords' must be a list, got {type(data['diversity_keywords']).__name__}",
                field="diversity_keywords",
            )
        for i, item in enumerate(data["diversity_keywords"]):
            if not isinstance(item, str):
                raise ConfigValidationError(
                    f"{prefix} 'diversity_keywords[{i}]' must be a string, got {type(item).__name__}",
                    field=f"diversity_keywords[{i}]",
                )
