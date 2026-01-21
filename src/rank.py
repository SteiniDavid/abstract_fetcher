"""Ranking and diversity selection for papers."""

import math
import re
from collections import Counter
from datetime import date

from .search import Paper, TopicConfig


def get_paper_text(paper: Paper) -> str:
    """Get combined lowercase text from paper title and abstract for matching."""
    return f"{paper.title} {paper.abstract or ''}".lower()


def compute_keyword_score(paper: Paper, topic: TopicConfig) -> tuple[float, list[str]]:
    """Compute keyword relevance score and return matched terms.

    Uses a simple BM25-like heuristic based on term presence in title and abstract.
    """
    score = 0.0
    matched_terms = []

    # Combine title and abstract for matching
    text = get_paper_text(paper)

    # Must terms are required - give high weight
    for term in topic.must:
        term_lower = term.lower()
        if term_lower in text:
            score += 2.0
            matched_terms.append(term)

    # Should terms add to relevance
    for term in topic.should:
        term_lower = term.lower()
        if term_lower in text:
            score += 1.0
            matched_terms.append(term)

            # Bonus for title match
            if term_lower in paper.title.lower():
                score += 0.5

    # Penalty for exclude terms (soft filter - doesn't eliminate)
    for term in topic.exclude:
        term_lower = term.lower()
        if term_lower in text:
            score -= 0.5

    return score, matched_terms


def compute_citation_score(paper: Paper) -> float:
    """Compute citation score (log-scaled to avoid over-weighting classics)."""
    if paper.citation_count is None or paper.citation_count <= 0:
        return 0.0

    # Log scale with diminishing returns
    # 10 citations -> ~2.3, 100 -> ~4.6, 1000 -> ~6.9
    return math.log(1 + paper.citation_count)


def compute_venue_score(paper: Paper, topic: TopicConfig) -> float:
    """Compute venue quality score."""
    if not paper.venue:
        return 0.0

    venue_upper = paper.venue.upper()
    for boost_venue in topic.venue_boost:
        if boost_venue.upper() in venue_upper:
            return 2.0

    return 0.0


def compute_recency_score(paper: Paper, topic: TopicConfig) -> float:
    """Compute recency score - mild boost for newer papers."""
    current_year = date.today().year
    paper_age = current_year - paper.year

    if paper_age <= 0:
        return 1.5  # This year
    elif paper_age <= 1:
        return 1.2  # Last year
    elif paper_age <= 2:
        return 1.0  # 2 years ago
    elif paper_age <= topic.recency_years // 2:
        return 0.8  # Within half recency window
    else:
        return 0.5  # Older


def score_paper(paper: Paper, topic: TopicConfig) -> tuple[float, str]:
    """Compute overall score for a paper and generate selection reason."""
    keyword_score, matched_terms = compute_keyword_score(paper, topic)
    citation_score = compute_citation_score(paper)
    venue_score = compute_venue_score(paper, topic)
    recency_score = compute_recency_score(paper, topic)

    # Weighted combination
    total_score = (
        keyword_score * 3.0    # Relevance is most important
        + citation_score * 1.0  # Citations matter but don't dominate
        + venue_score * 1.5     # Good venues are a signal
        + recency_score * 0.5   # Slight recency preference
    )

    # Generate selection reason
    reason_parts = []

    if matched_terms:
        terms_str = ", ".join(matched_terms[:3])
        reason_parts.append(f"matches: {terms_str}")

    if paper.citation_count and paper.citation_count > 10:
        reason_parts.append(f"{paper.citation_count} citations")

    if venue_score > 0 and paper.venue:
        venue_name = paper.venue.split(":")[0] if ":" in paper.venue else paper.venue
        reason_parts.append(f"published at {venue_name}")

    if paper.year >= date.today().year - 1:
        reason_parts.append("recent publication")

    reason = "; ".join(reason_parts) if reason_parts else "relevant to topic"

    return total_score, reason


def extract_key_phrases(paper: Paper) -> set[str]:
    """Extract key phrases from paper for diversity checking."""
    text = get_paper_text(paper)
    phrases = set()

    # Common method/concept keywords to track
    keywords = [
        "dagger", "dataset aggregation",
        "behavioral cloning", "bc",
        "imitation learning",
        "covariate shift", "distribution shift", "dataset shift",
        "compounding error", "error accumulation",
        "offline", "off-policy",
        "inverse reinforcement", "irl",
        "gail", "adversarial",
        "demonstration", "expert",
        "policy", "trajectory",
        "benchmark", "evaluation",
        "theoretical", "analysis", "bounds",
    ]

    for kw in keywords:
        if kw in text:
            phrases.add(kw)

    return phrases


def select_with_diversity(
    papers: list[Paper],
    n: int,
    max_per_phrase: int = 2,
) -> list[Paper]:
    """Select top N papers while maintaining diversity.

    Ensures no single key phrase dominates the selection.
    """
    if len(papers) <= n:
        return papers

    selected = []
    phrase_counts = Counter()

    # Sort by score descending
    sorted_papers = sorted(papers, key=lambda p: p.score, reverse=True)

    for paper in sorted_papers:
        if len(selected) >= n:
            break

        phrases = extract_key_phrases(paper)

        # Check if adding this paper would over-represent any phrase
        would_exceed = False
        for phrase in phrases:
            if phrase_counts[phrase] >= max_per_phrase:
                would_exceed = True
                break

        if would_exceed and len(selected) < n * 0.8:
            # Skip this paper for diversity, unless we're running low
            continue

        selected.append(paper)
        for phrase in phrases:
            phrase_counts[phrase] += 1

    # If we didn't get enough, add remaining top papers
    if len(selected) < n:
        remaining = [p for p in sorted_papers if p not in selected]
        selected.extend(remaining[: n - len(selected)])

    return selected


def select_papers(
    papers: list[Paper],
    topic: TopicConfig,
    n: int = 10,
) -> list[Paper]:
    """Score and select top N papers with diversity.

    Returns papers sorted by rank (best first) with scores and reasons populated.
    """
    if not papers:
        return []

    # Score all papers
    for paper in papers:
        score, reason = score_paper(paper, topic)
        paper.score = score
        paper.selected_reason = reason

    # Filter out papers with very low relevance (no must terms matched)
    relevant_papers = []
    for paper in papers:
        text = get_paper_text(paper)
        has_must = any(term.lower() in text for term in topic.must)
        if has_must or paper.score >= 1.0:
            relevant_papers.append(paper)

    if not relevant_papers:
        # Fall back to all papers if none match must terms
        relevant_papers = papers

    # Select with diversity
    selected = select_with_diversity(relevant_papers, n)

    return selected
