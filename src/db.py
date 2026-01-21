"""SQLite database for paper tracking and deduplication."""

import sqlite3
from datetime import date, timedelta
from pathlib import Path

from rapidfuzz import fuzz

from .search import Paper

# Fuzzy matching threshold for title deduplication (0-100)
FUZZY_MATCH_THRESHOLD = 92


SCHEMA = """
CREATE TABLE IF NOT EXISTS papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doi TEXT,
    arxiv_id TEXT,
    title_norm TEXT NOT NULL,
    title TEXT NOT NULL,
    year INTEGER,
    venue TEXT,
    url TEXT,
    pdf_url TEXT,
    first_seen DATE NOT NULL,
    last_seen DATE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_papers_doi ON papers(doi);
CREATE INDEX IF NOT EXISTS idx_papers_arxiv ON papers(arxiv_id);
CREATE INDEX IF NOT EXISTS idx_papers_title_norm ON papers(title_norm);
CREATE INDEX IF NOT EXISTS idx_papers_last_seen ON papers(last_seen);

CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_date DATE NOT NULL,
    topic_key TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_runs_date ON runs(run_date);
CREATE INDEX IF NOT EXISTS idx_runs_topic ON runs(topic_key);

CREATE TABLE IF NOT EXISTS run_papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES runs(id),
    paper_id INTEGER NOT NULL REFERENCES papers(id),
    rank INTEGER NOT NULL,
    selected_reason TEXT,
    pdf_path TEXT,
    abstract_source TEXT,
    extraction_status TEXT
);

CREATE INDEX IF NOT EXISTS idx_run_papers_run ON run_papers(run_id);
CREATE INDEX IF NOT EXISTS idx_run_papers_paper ON run_papers(paper_id);
"""


class PaperDatabase:
    """SQLite database for paper tracking."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        """Initialize database schema."""
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self):
        """Close the database connection."""
        self.conn.close()

    def _find_paper_by_doi(self, doi: str) -> dict | None:
        """Find paper by DOI."""
        cursor = self.conn.execute(
            "SELECT * FROM papers WHERE doi = ?",
            (doi,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def _find_paper_by_arxiv(self, arxiv_id: str) -> dict | None:
        """Find paper by arXiv ID."""
        cursor = self.conn.execute(
            "SELECT * FROM papers WHERE arxiv_id = ?",
            (arxiv_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def _find_paper_by_title(self, title_norm: str, threshold: int = FUZZY_MATCH_THRESHOLD) -> dict | None:
        """Find paper by fuzzy title match."""
        cursor = self.conn.execute("SELECT * FROM papers")
        for row in cursor:
            if fuzz.ratio(row["title_norm"], title_norm) >= threshold:
                return dict(row)
        return None

    def find_paper(self, paper: Paper) -> dict | None:
        """Find an existing paper in the database.

        Matching priority:
        1. DOI exact match
        2. arXiv ID exact match
        3. Fuzzy title match (ratio >= 92)
        """
        # Try DOI first
        if paper.doi:
            existing = self._find_paper_by_doi(paper.doi)
            if existing:
                return existing

        # Try arXiv ID
        if paper.arxiv_id:
            existing = self._find_paper_by_arxiv(paper.arxiv_id)
            if existing:
                return existing

        # Try fuzzy title match
        existing = self._find_paper_by_title(paper.title_normalized)
        return existing

    def add_paper(self, paper: Paper) -> int:
        """Add a paper to the database or update if exists.

        Returns the paper ID.
        """
        today = date.today()

        # Check if paper exists
        existing = self.find_paper(paper)
        if existing:
            # Update last_seen
            self.conn.execute(
                "UPDATE papers SET last_seen = ? WHERE id = ?",
                (today, existing["id"]),
            )
            self.conn.commit()
            return existing["id"]

        # Insert new paper
        cursor = self.conn.execute(
            """
            INSERT INTO papers (doi, arxiv_id, title_norm, title, year, venue, url, pdf_url, first_seen, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                paper.doi,
                paper.arxiv_id,
                paper.title_normalized,
                paper.title,
                paper.year,
                paper.venue,
                paper.url,
                paper.pdf_url,
                today,
                today,
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def create_run(self, run_date: date, topic_key: str) -> int:
        """Create a new run record.

        Returns the run ID.
        """
        cursor = self.conn.execute(
            "INSERT INTO runs (run_date, topic_key) VALUES (?, ?)",
            (run_date, topic_key),
        )
        self.conn.commit()
        return cursor.lastrowid

    def add_run_paper(
        self,
        run_id: int,
        paper_id: int,
        rank: int,
        selected_reason: str | None = None,
        pdf_path: str | None = None,
        abstract_source: str | None = None,
        extraction_status: str | None = None,
    ):
        """Add a paper to a run."""
        self.conn.execute(
            """
            INSERT INTO run_papers (run_id, paper_id, rank, selected_reason, pdf_path, abstract_source, extraction_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (run_id, paper_id, rank, selected_reason, pdf_path, abstract_source, extraction_status),
        )
        self.conn.commit()

    def deduplicate(self, papers: list[Paper]) -> list[Paper]:
        """Remove duplicate papers from a list.

        Uses the same matching rules as find_paper but operates on the input list only.
        Returns papers deduplicated against each other.
        """
        seen_dois = set()
        seen_arxiv = set()
        seen_titles = []
        unique = []

        for paper in papers:
            # Check DOI
            if paper.doi:
                if paper.doi in seen_dois:
                    continue
                seen_dois.add(paper.doi)

            # Check arXiv ID
            if paper.arxiv_id:
                if paper.arxiv_id in seen_arxiv:
                    continue
                seen_arxiv.add(paper.arxiv_id)

            # Check fuzzy title match
            title_norm = paper.title_normalized
            is_dup = False
            for seen_title in seen_titles:
                if fuzz.ratio(seen_title, title_norm) >= FUZZY_MATCH_THRESHOLD:
                    is_dup = True
                    break

            if is_dup:
                continue

            seen_titles.append(title_norm)
            unique.append(paper)

        return unique

    def filter_novel(self, papers: list[Paper], days: int = 365) -> list[Paper]:
        """Filter to papers not seen in the last N days.

        Papers without a match in the database are considered novel.
        """
        cutoff = date.today() - timedelta(days=days)
        novel = []

        for paper in papers:
            existing = self.find_paper(paper)
            if existing is None:
                # New paper
                novel.append(paper)
            elif existing["last_seen"] < str(cutoff):
                # Not seen recently
                novel.append(paper)

        return novel

    def get_recent_papers(self, topic_key: str, days: int = 30) -> list[dict]:
        """Get papers from recent runs for a topic."""
        cutoff = date.today() - timedelta(days=days)

        cursor = self.conn.execute(
            """
            SELECT DISTINCT p.* FROM papers p
            JOIN run_papers rp ON p.id = rp.paper_id
            JOIN runs r ON rp.run_id = r.id
            WHERE r.topic_key = ? AND r.run_date >= ?
            ORDER BY r.run_date DESC, rp.rank
            """,
            (topic_key, cutoff),
        )

        return [dict(row) for row in cursor]
