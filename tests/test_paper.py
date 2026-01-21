"""Tests for the Paper dataclass."""

import pytest

from src.search.base import Paper


def create_paper(**kwargs) -> Paper:
    """Create a Paper with default values, overriding with kwargs."""
    defaults = {
        "title": "Test Paper Title",
        "authors": ["Author One", "Author Two"],
        "year": 2024,
        "venue": "NeurIPS",
        "doi": "10.1234/test.2024",
        "arxiv_id": "2401.12345",
        "url": "https://example.com/paper",
        "pdf_url": "https://example.com/paper.pdf",
        "abstract": "This is a test abstract.",
        "citation_count": 10,
        "source": "test",
    }
    defaults.update(kwargs)
    return Paper(**defaults)


class TestPaperTitleNormalized:
    """Tests for title normalization."""

    def test_lowercase(self):
        paper = create_paper(title="UPPERCASE Title")
        assert paper.title_normalized == "uppercase title"

    def test_removes_punctuation(self):
        paper = create_paper(title="Title: With, Punctuation!")
        assert paper.title_normalized == "title with punctuation"

    def test_collapses_whitespace(self):
        paper = create_paper(title="Title   with    extra   spaces")
        assert paper.title_normalized == "title with extra spaces"

    def test_strips_whitespace(self):
        paper = create_paper(title="  padded title  ")
        assert paper.title_normalized == "padded title"


class TestPaperArxivIdNormalization:
    """Tests for arXiv ID normalization."""

    def test_removes_version_suffix(self):
        paper = create_paper(arxiv_id="2401.12345v3")
        assert paper.arxiv_id == "2401.12345"

    def test_keeps_id_without_version(self):
        paper = create_paper(arxiv_id="2401.12345")
        assert paper.arxiv_id == "2401.12345"

    def test_handles_none(self):
        paper = create_paper(arxiv_id=None)
        assert paper.arxiv_id is None


class TestPaperSafeFilename:
    """Tests for safe filename generation."""

    def test_basic_filename(self):
        paper = create_paper(title="Simple Title", year=2024, arxiv_id="2401.12345")
        filename = paper.safe_filename()
        assert "Simple_Title" in filename
        assert "2024" in filename
        assert "2401_12345" in filename

    def test_removes_special_chars(self):
        paper = create_paper(title="Title: With/Special*Chars!")
        filename = paper.safe_filename()
        # Should not contain special characters
        assert "/" not in filename
        assert "*" not in filename
        assert "!" not in filename

    def test_truncates_long_title(self):
        long_title = "A" * 100
        paper = create_paper(title=long_title)
        filename = paper.safe_filename(max_length=20)
        assert len(filename.split("_")[0]) <= 20

    def test_uses_doi_when_no_arxiv(self):
        paper = create_paper(arxiv_id=None, doi="10.1234/test.paper.2024")
        filename = paper.safe_filename()
        assert "test.paper.2024" in filename


class TestPaperToDict:
    """Tests for dictionary serialization."""

    def test_basic_serialization(self):
        paper = create_paper()
        data = paper.to_dict()
        assert data["title"] == "Test Paper Title"
        assert data["year"] == 2024
        assert data["source"] == "test"

    def test_excludes_abstract_by_default(self):
        paper = create_paper(abstract="Secret abstract")
        data = paper.to_dict(include_abstract=False)
        assert "abstract" not in data

    def test_includes_abstract_when_requested(self):
        paper = create_paper(abstract="Test abstract")
        data = paper.to_dict(include_abstract=True)
        assert data["abstract"] == "Test abstract"

    def test_rounds_score(self):
        paper = create_paper()
        paper.score = 3.14159265
        data = paper.to_dict()
        assert data["score"] == 3.14
