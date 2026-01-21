"""Configuration loading and validation for the paper digest pipeline."""

from .schema import ConfigValidationError, validate_topic_config

__all__ = ["ConfigValidationError", "validate_topic_config"]
