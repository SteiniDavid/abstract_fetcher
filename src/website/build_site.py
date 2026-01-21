"""Build Jekyll site from paper digests.

Scans runs/ for digest.md + metadata.json pairs and generates Jekyll-compatible
pages in docs/_digests/ with proper front matter.
"""

import json
import re
from pathlib import Path


def load_metadata(run_dir: Path) -> dict | None:
    """Load metadata.json from a run directory."""
    metadata_path = run_dir / "metadata.json"
    if not metadata_path.exists():
        return None
    with open(metadata_path) as f:
        return json.load(f)


def load_digest(run_dir: Path) -> str | None:
    """Load digest.md content from a run directory."""
    digest_path = run_dir / "digest.md"
    if not digest_path.exists():
        return None
    with open(digest_path) as f:
        return f.read()


def strip_h1_title(content: str) -> str:
    """Remove the first H1 title line from markdown content."""
    lines = content.split("\n")
    # Find and remove the first H1 line
    for i, line in enumerate(lines):
        if line.startswith("# "):
            lines.pop(i)
            # Also remove blank line after if present
            if i < len(lines) and lines[i].strip() == "":
                lines.pop(i)
            break
    return "\n".join(lines)


def generate_front_matter(metadata: dict) -> str:
    """Generate Jekyll front matter from metadata."""
    return f"""---
layout: digest
title: "{metadata['topic_name']}"
date: {metadata['run_date']}
topic_key: {metadata['topic_key']}
num_candidates: {metadata['num_candidates']}
num_unique: {metadata['num_unique']}
num_novel: {metadata['num_novel']}
num_selected: {metadata['num_selected']}
num_downloaded: {metadata['num_downloaded']}
num_abstracts: {metadata['num_abstracts']}
---
"""


def process_digest(run_dir: Path, output_dir: Path) -> bool:
    """Process a single run directory and write Jekyll-compatible digest."""
    metadata = load_metadata(run_dir)
    if not metadata:
        return False

    digest = load_digest(run_dir)
    if not digest:
        return False

    # Strip original H1 title (will be generated from front matter)
    content = strip_h1_title(digest)

    # Remove PDF local paths (they won't work on the web)
    content = re.sub(r"\*\*PDF:\*\* `papers/[^`]+`\n\n", "", content)
    content = re.sub(r"\*\*PDF:\*\* Not available[^\n]*\n\n", "", content)

    # Generate output filename: YYYY-MM-DD-topic_key.md
    output_name = f"{metadata['run_date']}-{metadata['topic_key']}.md"
    output_path = output_dir / output_name

    # Write with front matter
    front_matter = generate_front_matter(metadata)
    with open(output_path, "w") as f:
        f.write(front_matter)
        f.write(content)

    return True


def generate_index(digests_dir: Path, output_path: Path) -> None:
    """Generate index.md with digest listing grouped by topic."""
    # Collect all digest metadata
    digests = []
    for digest_file in digests_dir.glob("*.md"):
        # Parse front matter
        with open(digest_file) as f:
            content = f.read()

        # Extract front matter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                front_matter = parts[1]
                metadata = {}
                for line in front_matter.strip().split("\n"):
                    if ": " in line:
                        key, value = line.split(": ", 1)
                        # Remove quotes from string values
                        value = value.strip('"')
                        metadata[key] = value
                metadata["filename"] = digest_file.name
                digests.append(metadata)

    # Group by topic
    topics = {}
    for d in digests:
        topic = d.get("topic_key", "unknown")
        if topic not in topics:
            topics[topic] = []
        topics[topic].append(d)

    # Sort each topic's digests by date (newest first)
    for topic in topics:
        topics[topic].sort(key=lambda x: x.get("date", ""), reverse=True)

    # Generate index content
    index_content = """---
layout: default
title: Paper Digests
---

# Paper Digests

A collection of daily paper digests on various research topics.

"""

    for topic_key in sorted(topics.keys()):
        topic_digests = topics[topic_key]
        # Use the topic name from the first (most recent) digest
        topic_name = topic_digests[0].get("title", topic_key)
        index_content += f"## {topic_name}\n\n"

        for d in topic_digests:
            date = d.get("date", "unknown")
            num_selected = d.get("num_selected", "?")
            filename = d.get("filename", "")
            # Link without .md extension for Jekyll
            link = filename.replace(".md", "")
            index_content += f"- [{date}]({{% link _digests/{filename} %}}) - {num_selected} papers\n"

        index_content += "\n"

    with open(output_path, "w") as f:
        f.write(index_content)


def build_site(runs_dir: Path | None = None, docs_dir: Path | None = None) -> None:
    """Build the Jekyll site from all digests in runs/."""
    if runs_dir is None:
        runs_dir = Path("runs")
    if docs_dir is None:
        docs_dir = Path("docs")

    digests_dir = docs_dir / "_digests"
    digests_dir.mkdir(parents=True, exist_ok=True)

    # Process all run directories
    processed = 0
    for run_dir in sorted(runs_dir.iterdir()):
        if run_dir.is_dir():
            if process_digest(run_dir, digests_dir):
                print(f"Processed: {run_dir.name}")
                processed += 1

    print(f"\nProcessed {processed} digests")

    # Generate index
    index_path = docs_dir / "index.md"
    generate_index(digests_dir, index_path)
    print(f"Generated: {index_path}")


if __name__ == "__main__":
    build_site()
