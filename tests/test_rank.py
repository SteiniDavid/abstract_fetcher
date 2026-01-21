"""Tests for the ranking module."""

import pytest

from src.search.base import Paper, TopicConfig
from src.rank import (
    get_paper_text,
    compute_keyword_score,
    compute_citation_score,
    compute_venue_score,
    compute_recency_score,
    score_paper,
    extract_key_phrases,
    select_with_diversity,
    select_papers,
)


def create_paper(**kwargs) -> Paper:
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


def create_topic(**kwargs) -> TopicConfig:
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


class TestGetPaperText:
    """Tests for the get_paper_text helper."""

    def test_combines_title_and_abstract(self):
        paper = create_paper(title="My Title", abstract="My abstract")
        text = get_paper_text(paper)
        assert "my title" in text
        assert "my abstract" in text

    def test_handles_none_abstract(self):
        paper = create_paper(title="My Title", abstract=None)
        text = get_paper_text(paper)
        assert "my title" in text
        assert text == "my title "

    def test_returns_lowercase(self):
        paper = create_paper(title="UPPERCASE", abstract="ABSTRACT")
        text = get_paper_text(paper)
        assert text == "uppercase abstract"


class TestComputeKeywordScore:
    """Tests for keyword scoring."""

    def test_must_terms_give_high_score(self):
        paper = create_paper(
            title="Imitation learning with shift",
            abstract="This paper is about imitation learning."
        )
        topic = create_topic(must=["imitation learning"])
        score, terms = compute_keyword_score(paper, topic)
        assert score >= 2.0
        assert "imitation learning" in terms

    def test_should_terms_add_to_score(self):
        paper = create_paper(
            title="Imitation learning",
            abstract="We use DAgger for covariate shift."
        )
        topic = create_topic(
            must=["imitation learning"],
            should=["DAgger", "covariate shift"]
        )
        score, terms = compute_keyword_score(paper, topic)
        assert score > 2.0  # Must term + should terms
        assert "DAgger" in terms or "covariate shift" in terms

    def test_title_match_gives_bonus(self):
        paper_title = create_paper(title="DAgger method", abstract="Some text")
        paper_abstract = create_paper(title="Some title", abstract="DAgger method")
        topic = create_topic(must=[], should=["DAgger"])

        score_title, _ = compute_keyword_score(paper_title, topic)
        score_abstract, _ = compute_keyword_score(paper_abstract, topic)

        assert score_title > score_abstract  # Title match gets bonus

    def test_exclude_terms_reduce_score(self):
        paper_clean = create_paper(
            title="Imitation learning",
            abstract="Uses behavioral cloning."
        )
        paper_exclude = create_paper(
            title="Imitation learning",
            abstract="Uses reinforcement learning primarily."
        )
        topic = create_topic(
            must=["imitation learning"],
            exclude=["reinforcement learning"]
        )

        score_clean, _ = compute_keyword_score(paper_clean, topic)
        score_exclude, _ = compute_keyword_score(paper_exclude, topic)

        assert score_clean > score_exclude


class TestComputeCitationScore:
    """Tests for citation scoring."""

    def test_zero_citations_gives_zero_score(self):
        paper = create_paper(citation_count=0)
        assert compute_citation_score(paper) == 0.0

    def test_none_citations_gives_zero_score(self):
        paper = create_paper(citation_count=None)
        assert compute_citation_score(paper) == 0.0

    def test_more_citations_give_higher_score(self):
        paper_low = create_paper(citation_count=10)
        paper_high = create_paper(citation_count=100)

        score_low = compute_citation_score(paper_low)
        score_high = compute_citation_score(paper_high)

        assert score_high > score_low

    def test_log_scaling_prevents_domination(self):
        # 1000 citations should not be 100x the score of 10 citations
        paper_10 = create_paper(citation_count=10)
        paper_1000 = create_paper(citation_count=1000)

        score_10 = compute_citation_score(paper_10)
        score_1000 = compute_citation_score(paper_1000)

        # With log scaling, ratio should be much less than 100
        assert score_1000 / score_10 < 5


class TestComputeVenueScore:
    """Tests for venue scoring."""

    def test_boosted_venue_gets_score(self):
        paper = create_paper(venue="NeurIPS 2024")
        topic = create_topic(venue_boost=["NeurIPS"])
        assert compute_venue_score(paper, topic) > 0

    def test_non_boosted_venue_gets_zero(self):
        paper = create_paper(venue="Random Workshop")
        topic = create_topic(venue_boost=["NeurIPS", "ICML"])
        assert compute_venue_score(paper, topic) == 0.0

    def test_none_venue_gets_zero(self):
        paper = create_paper(venue=None)
        topic = create_topic(venue_boost=["NeurIPS"])
        assert compute_venue_score(paper, topic) == 0.0


class TestComputeRecencyScore:
    """Tests for recency scoring."""

    def test_current_year_gets_highest_score(self):
        from datetime import date
        paper = create_paper(year=date.today().year)
        topic = create_topic()
        score = compute_recency_score(paper, topic)
        assert score == 1.5

    def test_older_papers_get_lower_score(self):
        from datetime import date
        current_year = date.today().year
        paper_new = create_paper(year=current_year)
        paper_old = create_paper(year=current_year - 5)
        topic = create_topic()

        score_new = compute_recency_score(paper_new, topic)
        score_old = compute_recency_score(paper_old, topic)

        assert score_new > score_old


class TestExtractKeyPhrases:
    """Tests for key phrase extraction."""

    def test_extracts_known_keywords(self):
        paper = create_paper(
            title="DAgger for Imitation Learning",
            abstract="Uses behavioral cloning with covariate shift."
        )
        phrases = extract_key_phrases(paper)
        assert "dagger" in phrases
        assert "imitation learning" in phrases
        assert "covariate shift" in phrases

    def test_returns_empty_for_unrelated_paper(self):
        paper = create_paper(
            title="Quantum Computing Overview",
            abstract="This paper discusses qubit entanglement."
        )
        phrases = extract_key_phrases(paper)
        # Should have few or no matching phrases
        assert len(phrases) <= 2


class TestSelectWithDiversity:
    """Tests for diversity selection."""

    def test_limits_papers_per_phrase(self):
        # Create papers all about "dagger"
        papers = []
        for i in range(5):
            paper = create_paper(
                title=f"DAgger Paper {i}",
                abstract="This is about DAgger method."
            )
            paper.score = 10 - i  # Decreasing scores
            papers.append(paper)

        selected = select_with_diversity(papers, n=5, max_per_phrase=2)

        # Should have selected papers (may not be all 5 due to diversity)
        assert len(selected) >= 2
        assert len(selected) <= 5

    def test_selects_top_when_diverse(self):
        papers = []
        topics = ["dagger", "behavioral cloning", "inverse reinforcement"]
        for i, topic in enumerate(topics):
            paper = create_paper(
                title=f"{topic.title()} Paper",
                abstract=f"This is about {topic}."
            )
            paper.score = 10 - i
            papers.append(paper)

        selected = select_with_diversity(papers, n=3)
        assert len(selected) == 3


class TestSelectPapers:
    """Tests for the main selection function."""

    def test_selects_requested_number(self):
        papers = [create_paper(title=f"Paper {i}") for i in range(20)]
        topic = create_topic(must=[])  # No must terms to filter

        selected = select_papers(papers, topic, n=5)

        assert len(selected) <= 5

    def test_populates_scores(self):
        papers = [create_paper(title="Imitation learning paper")]
        topic = create_topic(must=["imitation learning"])

        selected = select_papers(papers, topic, n=1)

        assert selected[0].score > 0

    def test_populates_reason(self):
        papers = [create_paper(
            title="Imitation learning",
            abstract="Uses covariate shift.",
            citation_count=100
        )]
        topic = create_topic(must=["imitation learning"])

        selected = select_papers(papers, topic, n=1)

        assert selected[0].selected_reason != ""
