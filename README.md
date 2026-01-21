# Paper Digest

A daily paper discovery pipeline that searches academic sources, selects top papers, downloads open-access PDFs, and generates readable markdown digests.

## Features

- **Multi-source search**: Semantic Scholar and arXiv APIs
- **Smart deduplication**: DOI, arXiv ID, and fuzzy title matching
- **Relevance ranking**: Keyword matching, citation counts, venue quality, recency
- **Diversity selection**: Ensures variety across subtopics
- **OA-only PDF download**: Respects paywalls, downloads only open-access papers
- **Text extraction**: Abstracts from metadata, fallback to PDF extraction with PyMuPDF
- **Conclusion extraction**: Automatically extracts conclusions from downloaded PDFs
- **Persistent library**: SQLite database tracks seen papers to avoid repeats

## Installation

Requires [uv](https://docs.astral.sh/uv/) package manager.

```bash
uv sync
```

## Usage

List available topics:

```bash
uv run python -m src.main --list-topics
```

Run a digest for a topic:

```bash
uv run python -m src.main --topic covshift_imitation_learning
```

Options:

```
--topic, -t       Topic key from topics.yaml (required)
--date, -d        Run date in YYYY-MM-DD format (default: today)
--n               Number of papers to select (default: from topic config)
--conclusion      Extract conclusions from PDFs (default: from topic config)
--no-conclusion   Skip conclusion extraction
--config, -c      Path to config directory (default: config)
--data            Path to data directory (default: data)
--runs            Path to runs output directory (default: runs)
```

## Output

Each run creates a folder in `runs/` with:

```
runs/YYYY-MM-DD_<topic>/
├── papers/          # Downloaded PDFs
├── digest.md        # Readable markdown summary
├── metadata.json    # Run statistics
└── failures.json    # Any download/extraction failures
```

## Configuration

Topics are defined in `config/topics.yaml`:

```yaml
topics:
  covshift_imitation_learning:
    name: "Covariate shift in imitation learning"
    query:
      must:
        - "imitation learning"
      should:
        - "covariate shift"
        - "distribution shift"
        - "DAgger"
        - "behavioral cloning"
      exclude:
        - "domain adaptation"
    recency_years: 12
    papers_per_day: 10
    extract_conclusion: true
    venue_boost:
      - "NeurIPS"
      - "ICML"
      - "ICLR"
```

## Project Structure

```
paper-digest/
├── config/
│   └── topics.yaml          # Topic definitions
├── data/
│   ├── library.sqlite       # Paper tracking database
│   └── cache/               # API response cache
├── runs/                    # Daily run outputs
├── src/
│   ├── main.py              # CLI entry point
│   ├── search/
│   │   ├── base.py          # Paper dataclass
│   │   ├── semantic_scholar.py
│   │   └── arxiv.py
│   ├── db.py                # SQLite + dedup
│   ├── rank.py              # Scoring + selection
│   ├── acquire.py           # PDF download
│   ├── extract.py           # Text extraction
│   └── digest.py            # Markdown generation
└── pyproject.toml
```

## Notes

- **Rate limits**: Semantic Scholar has strict rate limits (100 req/5min without API key). Consider getting an API key for better coverage.
- **OA policy**: Only downloads PDFs from known open-access sources (arXiv, OpenReview, JMLR, etc.)
- **Caching**: API responses are cached in `data/cache/` to reduce repeated requests
