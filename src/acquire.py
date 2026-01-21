"""PDF acquisition for open access papers."""

import logging
import re
import time
from pathlib import Path
from typing import TypedDict
from urllib.parse import urlparse

import requests

from .search import Paper
from .utils.retry import retry_on_http_error


logger = logging.getLogger(__name__)

# PDF validation constants
PDF_MAGIC_BYTES = b"%PDF-"
PDF_EOF_MARKER = b"%%EOF"
MIN_PDF_SIZE = 1024  # 1KB minimum for valid PDF


class DownloadResult(TypedDict, total=False):
    """Result of downloading a PDF."""

    status: str
    path: str | None
    error: str | None
    url: str | None

# Known OA domains
OA_DOMAINS = {
    "arxiv.org",
    "export.arxiv.org",
    "openreview.net",
    "proceedings.mlr.press",
    "papers.nips.cc",
    "proceedings.neurips.cc",
    "aclanthology.org",
    "jmlr.org",
    "aaai.org",
}

# Rate limiting
DOWNLOAD_DELAY = 1.0  # seconds between downloads


def is_oa_url(url: str) -> bool:
    """Check if URL is from a known open access domain."""
    if not url:
        return False

    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove www. prefix
        domain = re.sub(r"^www\.", "", domain)

        for oa_domain in OA_DOMAINS:
            if domain.endswith(oa_domain):
                return True

        return False

    except (ValueError, AttributeError):
        # ValueError from urlparse on malformed URLs
        # AttributeError if netloc is None
        return False


def safe_filename(paper: Paper) -> str:
    """Generate a safe filename for the PDF."""
    return f"{paper.safe_filename()}.pdf"


def validate_pdf(file_path: Path) -> tuple[bool, str | None]:
    """Validate that a file is a valid PDF.

    Checks:
    - File exists and has minimum size (1KB)
    - File starts with PDF magic bytes (%PDF-)
    - File contains EOF marker (detect truncation)

    Args:
        file_path: Path to the PDF file to validate.

    Returns:
        Tuple of (is_valid, error_message).
        If valid, returns (True, None).
        If invalid, returns (False, error_description).
    """
    if not file_path.exists():
        return False, "File does not exist"

    file_size = file_path.stat().st_size
    if file_size < MIN_PDF_SIZE:
        return False, f"File too small ({file_size} bytes, minimum {MIN_PDF_SIZE})"

    try:
        with open(file_path, "rb") as f:
            # Check magic bytes at start
            header = f.read(len(PDF_MAGIC_BYTES))
            if not header.startswith(PDF_MAGIC_BYTES):
                return False, "Invalid PDF header (missing %PDF- magic bytes)"

            # Check for EOF marker (read last 1KB to find it)
            f.seek(max(0, file_size - 1024))
            tail = f.read()
            if PDF_EOF_MARKER not in tail:
                return False, "PDF appears truncated (missing %%EOF marker)"

    except IOError as e:
        return False, f"Failed to read file: {e}"

    return True, None


@retry_on_http_error(max_attempts=3, min_wait=1.0, max_wait=30.0)
def _fetch_pdf(url: str, headers: dict, timeout: float) -> requests.Response:
    """Fetch PDF from URL with retry logic."""
    response = requests.get(
        url,
        headers=headers,
        timeout=timeout,
        stream=True,
    )
    response.raise_for_status()
    return response


def download_pdf(paper: Paper, output_dir: Path, timeout: float = 60.0) -> DownloadResult:
    """Download PDF for a paper.

    Returns a DownloadResult with:
    - status: "success", "failed", or "skipped"
    - path: path to downloaded file (if success)
    - error: error message (if failed)

    Args:
        paper: The paper to download.
        output_dir: Directory to save the PDF.
        timeout: Request timeout in seconds (default: 60.0).
    """
    if not paper.pdf_url:
        return {"status": "skipped", "error": "No PDF URL available"}

    # Check if URL is from known OA source
    if not is_oa_url(paper.pdf_url):
        # Could be paywalled - skip to avoid issues
        logger.debug(f"Skipping non-OA URL: {paper.pdf_url}")
        return {"status": "skipped", "error": f"Not a known OA source: {paper.pdf_url}"}

    output_path = output_dir / safe_filename(paper)

    # Skip if already downloaded and valid
    if output_path.exists():
        is_valid, error = validate_pdf(output_path)
        if is_valid:
            return {"status": "success", "path": str(output_path)}
        else:
            # Remove invalid cached file
            logger.warning(f"Removing invalid cached PDF: {error}")
            output_path.unlink()

    try:
        # Rate limit
        time.sleep(DOWNLOAD_DELAY)

        headers = {
            "User-Agent": "paper-digest/1.0 (academic research tool)",
        }

        response = _fetch_pdf(paper.pdf_url, headers, timeout)

        # Check content type
        content_type = response.headers.get("Content-Type", "")
        if "pdf" not in content_type.lower() and not paper.pdf_url.endswith(".pdf"):
            # Might be HTML error page
            logger.warning(f"Unexpected content type: {content_type} for {paper.pdf_url}")
            return {"status": "failed", "error": f"Unexpected content type: {content_type}"}

        # Write to file
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Validate the downloaded PDF
        is_valid, validation_error = validate_pdf(output_path)
        if not is_valid:
            logger.warning(f"Downloaded PDF is invalid: {validation_error}")
            # Remove invalid file
            output_path.unlink(missing_ok=True)
            return {"status": "failed", "error": f"PDF validation failed: {validation_error}"}

        logger.debug(f"Downloaded: {output_path}")
        return {"status": "success", "path": str(output_path)}

    except requests.Timeout:
        logger.warning(f"Timeout downloading: {paper.pdf_url}")
        return {"status": "failed", "error": "Download timeout"}

    except requests.RequestException as e:
        logger.warning(f"Failed to download {paper.pdf_url}: {e}")
        return {"status": "failed", "error": str(e)}

    except IOError as e:
        logger.warning(f"Failed to save PDF: {e}")
        return {"status": "failed", "error": f"IO error: {e}"}


def download_pdfs(papers: list[Paper], output_dir: Path) -> list[DownloadResult]:
    """Download PDFs for a list of papers.

    Returns a list of DownloadResult dicts (same order as input papers).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for paper in papers:
        result = download_pdf(paper, output_dir)
        results.append(result)

        if result["status"] == "success":
            logger.info(f"  Downloaded: {paper.title[:50]}...")
        elif result["status"] == "failed":
            logger.warning(f"  Failed: {paper.title[:50]}... ({result['error']})")
        else:
            logger.debug(f"  Skipped: {paper.title[:50]}...")

    return results
