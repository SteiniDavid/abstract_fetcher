"""Generate markdown digest from selected papers."""

from datetime import date
from pathlib import Path

from .search import Paper, TopicConfig


def format_authors(authors: list[str], max_authors: int = 5) -> str:
    """Format author list for display."""
    if not authors:
        return "Unknown"

    if len(authors) <= max_authors:
        return ", ".join(authors)

    return ", ".join(authors[:max_authors]) + f" et al. ({len(authors)} authors)"


def format_links(paper: Paper) -> str:
    """Format paper links."""
    links = []

    if paper.url:
        links.append(f"[Paper]({paper.url})")

    if paper.doi:
        doi_url = f"https://doi.org/{paper.doi}"
        links.append(f"[DOI]({doi_url})")

    if paper.arxiv_id:
        arxiv_url = f"https://arxiv.org/abs/{paper.arxiv_id}"
        links.append(f"[arXiv]({arxiv_url})")

    return " | ".join(links) if links else "No links available"


def format_pdf_link(download_result: dict, run_dir: Path) -> str:
    """Format PDF download status/link."""
    if download_result["status"] == "success":
        pdf_path = Path(download_result["path"])
        relative_path = pdf_path.relative_to(run_dir)
        return f"`{relative_path}`"
    elif download_result["status"] == "skipped":
        return "Not available (OA only)"
    else:
        error = download_result.get("error", "Unknown error")
        return f"Download failed: {error}"


def format_abstract(extract_result: dict) -> str:
    """Format abstract section."""
    abstract = extract_result.get("abstract")
    if not abstract:
        return "*Abstract not available*"

    source = extract_result.get("abstract_source", "unknown")
    return f"{abstract}\n\n*(Source: {source})*"


def format_conclusion(extract_result: dict, download_result: dict) -> str:
    """Format conclusion section."""
    conclusion = extract_result.get("conclusion")
    if conclusion:
        return conclusion

    # Provide reason why conclusion is not available
    if download_result["status"] != "success":
        return "*Conclusion not available (PDF not downloaded)*"

    return "*Conclusion not found in PDF*"


def generate_paper_entry(
    rank: int,
    paper: Paper,
    download_result: dict,
    extract_result: dict,
    run_dir: Path,
) -> str:
    """Generate markdown entry for a single paper."""
    lines = []

    # Header with title, year, venue
    venue_str = f" — {paper.venue}" if paper.venue else ""
    lines.append(f"## {rank}) {paper.title} ({paper.year}){venue_str}")
    lines.append("")

    # Authors
    lines.append(f"**Authors:** {format_authors(paper.authors)}")
    lines.append("")

    # Links
    lines.append(f"**Links:** {format_links(paper)}")
    lines.append("")

    # Why selected
    lines.append(f"**Why selected:** {paper.selected_reason}")
    lines.append("")

    # PDF status
    lines.append(f"**PDF:** {format_pdf_link(download_result, run_dir)}")
    lines.append("")

    # Abstract
    lines.append("### Abstract")
    lines.append("")
    lines.append(format_abstract(extract_result))
    lines.append("")

    # Conclusion
    lines.append("### Conclusion")
    lines.append("")
    lines.append(format_conclusion(extract_result, download_result))
    lines.append("")

    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def generate_summary(
    papers: list[Paper],
    download_results: list[dict],
    extract_results: list[dict],
) -> str:
    """Generate summary statistics."""
    total = len(papers)
    downloaded = sum(1 for r in download_results if r["status"] == "success")
    skipped = sum(1 for r in download_results if r["status"] == "skipped")
    failed_download = sum(1 for r in download_results if r["status"] == "failed")

    abstracts = sum(1 for r in extract_results if r.get("abstract"))
    conclusions = sum(1 for r in extract_results if r.get("conclusion"))

    lines = [
        "## Summary",
        "",
        f"- **Papers selected:** {total}",
        f"- **PDFs downloaded:** {downloaded} (skipped: {skipped}, failed: {failed_download})",
        f"- **Abstracts available:** {abstracts}",
        f"- **Conclusions extracted:** {conclusions}",
        "",
    ]

    return "\n".join(lines)


def generate_digest(
    run_dir: Path,
    topic: TopicConfig,
    run_date: date,
    papers: list[Paper],
    download_results: list[dict],
    extract_results: list[dict],
) -> Path:
    """Generate the full digest markdown file.

    Returns path to the generated file.
    """
    lines = []

    # Title
    lines.append(f"# Daily Paper Digest — {topic.name} — {run_date.isoformat()}")
    lines.append("")

    # Summary
    lines.append(generate_summary(papers, download_results, extract_results))

    # Paper entries
    for i, (paper, dl_result, ex_result) in enumerate(
        zip(papers, download_results, extract_results)
    ):
        entry = generate_paper_entry(
            rank=i + 1,
            paper=paper,
            download_result=dl_result,
            extract_result=ex_result,
            run_dir=run_dir,
        )
        lines.append(entry)

    # Footer
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Generated by paper-digest*")

    # Write file
    digest_path = run_dir / "digest.md"
    with open(digest_path, "w") as f:
        f.write("\n".join(lines))

    return digest_path
