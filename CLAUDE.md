# Claude Code Instructions

## Running Commands

This project uses [uv](https://docs.astral.sh/uv/) as the package manager. Always prefix commands with `uv run`:

```bash
uv run pytest tests/ -v      # Run tests
uv run python -m src.main    # Run the app
uv run ruff check src/       # Lint (if needed)
```

Do NOT use bare `python`, `python3`, or `pytest` commands - they won't have access to the project's dependencies.
