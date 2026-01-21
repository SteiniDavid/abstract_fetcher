"""Paper Digest CLI - Daily scholarly paper discovery pipeline."""

import json
import logging
from datetime import date
from pathlib import Path

import click
import yaml

from .search import Paper, TopicConfig
from .search.semantic_scholar import SemanticScholarAdapter
from .search.arxiv import ArxivAdapter
from .db import PaperDatabase
from .rank import select_papers
from .acquire import download_pdfs
from .extract import extract_text
from .digest import generate_digest


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_topics(config_path: Path) -> dict[str, TopicConfig]:
    """Load topic configurations from YAML."""
    with open(config_path) as f:
        data = yaml.safe_load(f)

    topics = {}
    for key, topic_data in data.get("topics", {}).items():
        topics[key] = TopicConfig.from_dict(topic_data)
    return topics


def create_run_dir(base_path: Path, run_date: date, topic_key: str) -> Path:
    """Create and return the run output directory."""
    run_dir = base_path / f"{run_date.isoformat()}_{topic_key}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "papers").mkdir(exist_ok=True)
    return run_dir


def get_paper_id(paper) -> str:
    """Get a unique identifier for a paper for deduplication."""
    return paper.doi or paper.arxiv_id or paper.title_normalized


def run_searches(
    topic: TopicConfig,
    cache_dir: Path,
    failures: dict,
) -> list[Paper]:
    """Run searches across all configured sources.

    Returns list of candidate papers.
    """
    candidates: list[Paper] = []

    # Semantic Scholar
    try:
        semantic_scholar_adapter = SemanticScholarAdapter(cache_dir=cache_dir)
        s2_papers = semantic_scholar_adapter.search(topic, max_results=100)
        logger.info(f"  Semantic Scholar: {len(s2_papers)} papers")
        candidates.extend(s2_papers)
    except Exception as e:
        logger.warning(f"  Semantic Scholar search failed: {e}")
        failures["search"].append({"source": "semantic_scholar", "error": str(e)})

    # arXiv
    try:
        arxiv_adapter = ArxivAdapter(cache_dir=cache_dir)
        arxiv_papers = arxiv_adapter.search(topic, max_results=100)
        logger.info(f"  arXiv: {len(arxiv_papers)} papers")
        candidates.extend(arxiv_papers)
    except Exception as e:
        logger.warning(f"  arXiv search failed: {e}")
        failures["search"].append({"source": "arxiv", "error": str(e)})

    return candidates


def deduplicate_and_filter(
    candidates: list[Paper],
    db: PaperDatabase,
    num_papers: int,
) -> tuple[list[Paper], list[Paper], list[Paper]]:
    """Deduplicate candidates and filter for novel papers.

    Returns (unique_papers, novel_papers, papers_to_rank).
    """
    unique_papers = db.deduplicate(candidates)
    novel_papers = db.filter_novel(unique_papers, days=365)
    logger.info(f"  After dedup: {len(unique_papers)}, Novel: {len(novel_papers)}")

    # If not enough novel papers, include some repeats
    papers_to_rank = list(novel_papers)  # Make a copy
    if len(novel_papers) < num_papers:
        logger.info(f"  Not enough novel papers, including {num_papers - len(novel_papers)} recent ones")
        seen_ids = {get_paper_id(p) for p in novel_papers}
        for p in unique_papers:
            if len(papers_to_rank) >= num_papers * 2:
                break
            pid = get_paper_id(p)
            if pid not in seen_ids:
                papers_to_rank.append(p)
                seen_ids.add(pid)

    return unique_papers, novel_papers, papers_to_rank


def download_and_extract(
    selected: list,
    run_dir: Path,
    extract_conclusion: bool,
    failures: dict,
) -> tuple[list[dict], list[dict], int]:
    """Download PDFs and extract text from selected papers.

    Returns (download_results, extract_results, downloaded_count).
    """
    logger.info("Downloading PDFs...")
    download_results = download_pdfs(selected, run_dir / "papers")

    for paper, result in zip(selected, download_results):
        if result["status"] == "failed":
            failures["download"].append({
                "title": paper.title,
                "error": result.get("error", "Unknown error"),
            })

    downloaded_count = sum(1 for r in download_results if r["status"] == "success")
    logger.info(f"  Downloaded: {downloaded_count}/{len(selected)}")

    logger.info("Extracting text...")
    extract_results = extract_text(selected, download_results, extract_conclusion)

    for paper, result in zip(selected, extract_results):
        if result.get("abstract_status") == "failed":
            failures["extract"].append({
                "title": paper.title,
                "type": "abstract",
                "error": result.get("abstract_error", "Unknown error"),
            })

    return download_results, extract_results, downloaded_count


def save_candidates(
    papers_to_rank: list,
    selected: list,
    run_dir: Path,
) -> None:
    """Save all candidates with scores to JSON."""
    selected_ids = {get_paper_id(p) for p in selected}
    all_candidates = []

    for paper in sorted(papers_to_rank, key=lambda p: p.score, reverse=True):
        paper_id = get_paper_id(paper)
        candidate_data = paper.to_dict(include_abstract=False)
        candidate_data["selected"] = paper_id in selected_ids
        all_candidates.append(candidate_data)

    with open(run_dir / "candidates.json", "w") as f:
        json.dump(all_candidates, f, indent=2)


def save_run_metadata(
    run_dir: Path,
    topic_key: str,
    topic: TopicConfig,
    run_date: date,
    candidates: list,
    unique_papers: list,
    novel_papers: list,
    selected: list,
    downloaded_count: int,
    extract_results: list[dict],
    failures: dict,
) -> None:
    """Save run metadata and failures to JSON files."""
    metadata = {
        "topic_key": topic_key,
        "topic_name": topic.name,
        "run_date": run_date.isoformat(),
        "num_candidates": len(candidates),
        "num_unique": len(unique_papers),
        "num_novel": len(novel_papers),
        "num_selected": len(selected),
        "num_downloaded": downloaded_count,
        "num_abstracts": sum(1 for r in extract_results if r.get("abstract")),
    }

    with open(run_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    with open(run_dir / "failures.json", "w") as f:
        json.dump(failures, f, indent=2)


def record_papers_in_db(
    db: PaperDatabase,
    run_date: date,
    topic_key: str,
    selected: list,
    download_results: list[dict],
    extract_results: list[dict],
) -> None:
    """Record selected papers in the database."""
    run_id = db.create_run(run_date, topic_key)

    for i, (paper, dl_result, ex_result) in enumerate(zip(selected, download_results, extract_results)):
        paper_id = db.add_paper(paper)
        db.add_run_paper(
            run_id=run_id,
            paper_id=paper_id,
            rank=i + 1,
            selected_reason=paper.selected_reason,
            pdf_path=dl_result.get("path"),
            abstract_source=ex_result.get("abstract_source"),
            extraction_status="success" if ex_result.get("abstract") else "failed",
        )


@click.command()
@click.option(
    "--topic",
    "-t",
    "topic_key",
    help="Topic key from topics.yaml to search for",
)
@click.option(
    "--date",
    "-d",
    "run_date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=None,
    help="Date for the run (default: today)",
)
@click.option(
    "--n",
    "-n",
    "num_papers",
    type=int,
    default=None,
    help="Number of papers to select (default: from topic config)",
)
@click.option(
    "--conclusion/--no-conclusion",
    "extract_conclusion",
    default=None,
    help="Extract conclusions from PDFs",
)
@click.option(
    "--list-topics",
    is_flag=True,
    help="List available topics and exit",
)
@click.option(
    "--config",
    "-c",
    "config_dir",
    type=click.Path(exists=True, path_type=Path),
    default=Path("config"),
    help="Path to config directory",
)
@click.option(
    "--data",
    "data_dir",
    type=click.Path(path_type=Path),
    default=Path("data"),
    help="Path to data directory",
)
@click.option(
    "--runs",
    "runs_dir",
    type=click.Path(path_type=Path),
    default=Path("runs"),
    help="Path to runs output directory",
)
def main(
    topic_key: str | None,
    run_date: date | None,
    num_papers: int | None,
    extract_conclusion: bool | None,
    list_topics: bool,
    config_dir: Path,
    data_dir: Path,
    runs_dir: Path,
) -> None:
    """Daily paper digest pipeline for scholarly paper discovery.

    Search academic sources, select top papers, download PDFs, and generate
    a readable digest markdown file.
    """
    # Load topics
    topics_file = config_dir / "topics.yaml"
    if not topics_file.exists():
        raise click.ClickException(f"Topics config not found: {topics_file}")

    topics = load_topics(topics_file)

    # List topics mode
    if list_topics:
        click.echo("Available topics:")
        for key, topic in topics.items():
            click.echo(f"  {key}: {topic.name}")
        return

    # Require topic for run
    if not topic_key:
        raise click.ClickException("--topic is required. Use --list-topics to see available topics.")

    if topic_key not in topics:
        raise click.ClickException(f"Unknown topic: {topic_key}. Use --list-topics to see available topics.")

    topic = topics[topic_key]

    # Set defaults from topic config
    if run_date is None:
        run_date = date.today()
    else:
        run_date = run_date.date()

    if num_papers is None:
        num_papers = topic.papers_per_day

    if extract_conclusion is None:
        extract_conclusion = topic.extract_conclusion

    logger.info(f"Starting paper digest for topic: {topic.name}")
    logger.info(f"Run date: {run_date}, Papers: {num_papers}, Conclusions: {extract_conclusion}")

    # Initialize database
    data_dir.mkdir(parents=True, exist_ok=True)
    db = PaperDatabase(data_dir / "library.sqlite")

    # Create run directory
    run_dir = create_run_dir(runs_dir, run_date, topic_key)
    logger.info(f"Output directory: {run_dir}")

    # Search phase
    logger.info("Searching for papers...")
    failures: dict[str, list] = {"search": [], "download": [], "extract": []}
    candidates = run_searches(topic, data_dir / "cache", failures)

    if not candidates:
        raise click.ClickException("No papers found from any source!")

    logger.info(f"Total candidates: {len(candidates)}")

    # Dedup and filter previously seen
    logger.info("Deduplicating and filtering...")
    unique_papers, novel_papers, papers_to_rank = deduplicate_and_filter(
        candidates, db, num_papers
    )

    # Rank and select
    logger.info("Ranking and selecting papers...")
    selected = select_papers(papers_to_rank, topic, num_papers)
    logger.info(f"Selected {len(selected)} papers")

    # Save all candidates with scores
    save_candidates(papers_to_rank, selected, run_dir)

    # Download PDFs and extract text
    download_results, extract_results, downloaded_count = download_and_extract(
        selected, run_dir, extract_conclusion, failures
    )

    # Record papers in database
    record_papers_in_db(
        db, run_date, topic_key, selected, download_results, extract_results
    )

    # Generate digest
    logger.info("Generating digest...")
    digest_path = generate_digest(
        run_dir=run_dir,
        topic=topic,
        run_date=run_date,
        papers=selected,
        download_results=download_results,
        extract_results=extract_results,
    )
    logger.info(f"Digest written to: {digest_path}")

    # Save metadata and failures
    save_run_metadata(
        run_dir, topic_key, topic, run_date,
        candidates, unique_papers, novel_papers, selected,
        downloaded_count, extract_results, failures
    )

    logger.info("Done!")
    logger.info(f"  Digest: {digest_path}")
    logger.info(f"  Selected: {len(selected)}, Downloaded: {downloaded_count}")

    total_failures = sum(len(v) for v in failures.values())
    if total_failures > 0:
        logger.warning(f"  Failures: {total_failures} (see failures.json)")


if __name__ == "__main__":
    main()
