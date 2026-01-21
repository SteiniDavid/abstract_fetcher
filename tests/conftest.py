"""Shared test fixtures and helpers."""

import pytest

from src.search.base import Paper, TopicConfig


def _create_paper(**kwargs) -> Paper:
    """Create a Paper with default values, overriding with kwargs."""
    defaults = {
        "title": "Test Paper Title",
        "authors": ["Author One"],
        "year": 2024,
        "venue": None,
        "doi": None,
        "arxiv_id": None,
        "url": "https://example.com",
        "pdf_url": None,
        "abstract": None,
        "citation_count": None,
        "source": "test",
    }
    defaults.update(kwargs)
    return Paper(**defaults)


def _create_topic(**kwargs) -> TopicConfig:
    """Create a TopicConfig with default values."""
    defaults = {
        "name": "Test Topic",
        "must": ["imitation learning"],
        "should": ["covariate shift", "DAgger"],
        "exclude": ["reinforcement learning"],
        "recency_years": 10,
        "papers_per_day": 10,
        "venue_boost": ["NeurIPS", "ICML"],
    }
    defaults.update(kwargs)
    return TopicConfig(**defaults)


@pytest.fixture
def create_paper():
    """Fixture that returns the create_paper helper function."""
    return _create_paper


@pytest.fixture
def create_topic():
    """Fixture that returns the create_topic helper function."""
    return _create_topic
