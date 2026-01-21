"""Tests for the database module."""

import tempfile
from pathlib import Path

import pytest

from src.db import PaperDatabase


@pytest.fixture
def db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.sqlite"
        database = PaperDatabase(db_path)
        yield database
        database.close()


class TestDeduplication:
    """Tests for paper deduplication."""

    def test_deduplicate_by_doi(self, db, create_paper):
        papers = [
            create_paper(title="Paper 1", doi="10.1234/a"),
            create_paper(title="Paper 1 Copy", doi="10.1234/a"),
            create_paper(title="Paper 2", doi="10.1234/b"),
        ]

        unique = db.deduplicate(papers)

        assert len(unique) == 2
        dois = {p.doi for p in unique}
        assert dois == {"10.1234/a", "10.1234/b"}

    def test_deduplicate_by_arxiv_id(self, db, create_paper):
        papers = [
            create_paper(title="Paper 1", arxiv_id="2401.00001"),
            create_paper(title="Paper 1 Copy", arxiv_id="2401.00001"),
            create_paper(title="Paper 2", arxiv_id="2401.00002"),
        ]

        unique = db.deduplicate(papers)

        assert len(unique) == 2
        arxiv_ids = {p.arxiv_id for p in unique}
        assert arxiv_ids == {"2401.00001", "2401.00002"}

    def test_deduplicate_by_fuzzy_title(self, db, create_paper):
        papers = [
            create_paper(title="Imitation Learning via DAgger"),
            create_paper(title="Imitation Learning via Dagger"),  # Slightly different
            create_paper(title="Completely Different Paper"),
        ]

        unique = db.deduplicate(papers)

        # Should find the similar titles as duplicates
        assert len(unique) == 2

    def test_deduplicate_preserves_order(self, db, create_paper):
        papers = [
            create_paper(title="First Paper", doi="10.1234/1"),
            create_paper(title="Second Paper", doi="10.1234/2"),
            create_paper(title="First Paper Duplicate", doi="10.1234/1"),
        ]

        unique = db.deduplicate(papers)

        assert unique[0].title == "First Paper"
        assert unique[1].title == "Second Paper"


class TestFindPaper:
    """Tests for finding papers in database."""

    def test_find_by_doi(self, db, create_paper):
        paper = create_paper(title="Original", doi="10.1234/find")
        db.add_paper(paper)

        search_paper = create_paper(title="Different Title", doi="10.1234/find")
        found = db.find_paper(search_paper)

        assert found is not None
        assert found["doi"] == "10.1234/find"

    def test_find_by_arxiv_id(self, db, create_paper):
        paper = create_paper(title="Original", arxiv_id="2401.12345")
        db.add_paper(paper)

        search_paper = create_paper(title="Different Title", arxiv_id="2401.12345")
        found = db.find_paper(search_paper)

        assert found is not None
        assert found["arxiv_id"] == "2401.12345"

    def test_find_by_title(self, db, create_paper):
        paper = create_paper(title="Unique Specific Title Here")
        db.add_paper(paper)

        search_paper = create_paper(title="Unique Specific Title Here")
        found = db.find_paper(search_paper)

        assert found is not None

    def test_not_found_returns_none(self, db, create_paper):
        search_paper = create_paper(title="Nonexistent Paper")
        found = db.find_paper(search_paper)

        assert found is None


class TestAddPaper:
    """Tests for adding papers to database."""

    def test_add_new_paper(self, db, create_paper):
        paper = create_paper(title="Brand New Paper")
        paper_id = db.add_paper(paper)

        assert paper_id > 0
        found = db.find_paper(paper)
        assert found is not None

    def test_add_updates_existing(self, db, create_paper):
        paper = create_paper(title="Paper to Update", doi="10.1234/update")

        first_id = db.add_paper(paper)
        second_id = db.add_paper(paper)  # Add again

        assert first_id == second_id  # Same paper, same ID


class TestFilterNovel:
    """Tests for novel paper filtering."""

    def test_new_papers_are_novel(self, db, create_paper):
        papers = [
            create_paper(title="New Paper 1"),
            create_paper(title="New Paper 2"),
        ]

        novel = db.filter_novel(papers)

        assert len(novel) == 2

    def test_recent_papers_are_not_novel(self, db, create_paper):
        # Add a paper to database
        paper = create_paper(title="Already Seen Paper", doi="10.1234/seen")
        db.add_paper(paper)

        # Try to filter it as novel
        papers = [create_paper(title="Already Seen Paper", doi="10.1234/seen")]
        novel = db.filter_novel(papers, days=365)

        assert len(novel) == 0


class TestRuns:
    """Tests for run management."""

    def test_create_run(self, db):
        from datetime import date

        run_id = db.create_run(date.today(), "test_topic")

        assert run_id > 0

    def test_add_run_paper(self, db, create_paper):
        from datetime import date

        run_id = db.create_run(date.today(), "test_topic")
        paper = create_paper(title="Test Paper")
        paper_id = db.add_paper(paper)

        # Should not raise
        db.add_run_paper(
            run_id=run_id,
            paper_id=paper_id,
            rank=1,
            selected_reason="test reason",
        )
