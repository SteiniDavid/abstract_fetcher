"""Text extraction from papers (abstract and conclusion)."""

import logging
import re
from pathlib import Path

import fitz  # PyMuPDF

from .search import Paper


logger = logging.getLogger(__name__)

# Section header patterns
ABSTRACT_PATTERNS = [
    r"^abstract\s*$",
    r"^abstract\s*[:\.]",
    r"^\d+\.?\s*abstract",
]

CONCLUSION_PATTERNS = [
    r"^conclusions?\s*$",
    r"^conclusions?\s*[:\.]",
    r"^\d+\.?\s*conclusions?",
    r"^[ivx]+\.?\s*conclusions?",  # Roman numerals
    r"^concluding\s+remarks",
    r"^summary\s+and\s+conclusions?",
    r"^discussion\s+and\s+conclusions?",
    r"^conclusions?\s+and\s+future\s+work",
    r"^conclusions?\s+and\s+limitations",
    r"^final\s+remarks",
    r"^closing\s+remarks",
    r"^summary",
]

# Patterns that indicate end of section
SECTION_END_PATTERNS = [
    r"^\d+\.?\s+\w+",  # Numbered section header
    r"^introduction",
    r"^related\s+work",
    r"^background",
    r"^method",
    r"^approach",
    r"^experiment",
    r"^result",
    r"^discussion",
    r"^conclusion",
    r"^reference",
    r"^acknowledge",
    r"^appendix",
    r"^supplementary",
]


def clean_text(text: str) -> str:
    """Clean extracted text."""
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)
    # Remove common artifacts
    text = re.sub(r"-\s+", "", text)  # Hyphenation
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)  # Space before punctuation
    return text.strip()


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """Extract full text from a PDF."""
    try:
        doc = fitz.open(pdf_path)
        text_parts = []

        for page in doc:
            text_parts.append(page.get_text())

        doc.close()
        return "\n".join(text_parts)

    except FileNotFoundError:
        logger.warning(f"PDF file not found: {pdf_path}")
        return ""
    except RuntimeError as e:
        # PyMuPDF raises RuntimeError for corrupt/invalid PDFs
        logger.warning(f"Failed to parse PDF {pdf_path}: {e}")
        return ""
    except (IOError, OSError) as e:
        logger.warning(f"IO error reading PDF {pdf_path}: {e}")
        return ""


def find_section(
    text: str,
    start_patterns: list[str],
    end_patterns: list[str] | None = None,
    max_length: int = 3000,
) -> str | None:
    """Find and extract a section from text.

    Args:
        text: Full document text
        start_patterns: Regex patterns that indicate section start
        end_patterns: Regex patterns that indicate section end
        max_length: Maximum characters to extract

    Returns:
        Extracted section text or None if not found
    """
    if end_patterns is None:
        end_patterns = SECTION_END_PATTERNS

    lines = text.split("\n")
    section_start = None
    section_lines = []

    for i, line in enumerate(lines):
        line_lower = line.lower().strip()

        # Look for section start
        if section_start is None:
            for pattern in start_patterns:
                if re.match(pattern, line_lower):
                    section_start = i
                    break
            continue

        # We're in the section - check for end
        for pattern in end_patterns:
            # Don't match our own start pattern
            if any(re.match(sp, line_lower) for sp in start_patterns):
                continue
            if re.match(pattern, line_lower):
                # Found end of section
                section_text = "\n".join(section_lines)
                return clean_text(section_text)[:max_length]

        section_lines.append(line)

        # Limit section length
        current_text = "\n".join(section_lines)
        if len(current_text) > max_length:
            return clean_text(current_text)[:max_length]

    # Return what we found if section started
    if section_lines:
        section_text = "\n".join(section_lines)
        return clean_text(section_text)[:max_length]

    return None


def extract_abstract_from_pdf(pdf_path: str | Path) -> str | None:
    """Extract abstract from a PDF."""
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return None

    # Try to find abstract section
    abstract = find_section(
        text,
        ABSTRACT_PATTERNS,
        max_length=2000,
    )

    if abstract and len(abstract) > 50:
        return abstract

    # Fallback: try to find text before introduction
    # Many papers have abstract as first paragraph
    intro_match = re.search(r"\n\s*1\.?\s*introduction", text.lower())
    if intro_match:
        first_part = text[: intro_match.start()]
        # Find first substantial paragraph
        paragraphs = [p.strip() for p in first_part.split("\n\n") if len(p.strip()) > 100]
        if paragraphs:
            return clean_text(paragraphs[-1])[:2000]

    return None


def extract_conclusion_from_pdf(pdf_path: str | Path) -> str | None:
    """Extract conclusion from a PDF."""
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return None

    # Try to find conclusion section
    conclusion = find_section(
        text,
        CONCLUSION_PATTERNS,
        end_patterns=[
            r"^reference",
            r"^acknowledge",
            r"^appendix",
            r"^supplementary",
            r"^broader\s+impact",
        ],
        max_length=3000,
    )

    if conclusion and len(conclusion) > 50:
        return conclusion

    return None


def extract_text(
    papers: list[Paper],
    download_results: list[dict],
    extract_conclusion: bool = True,
) -> list[dict]:
    """Extract abstract and optionally conclusion for papers.

    Args:
        papers: List of papers
        download_results: Results from download_pdfs (same order as papers)
        extract_conclusion: Whether to extract conclusions

    Returns:
        List of extraction results with:
        - abstract: extracted abstract text
        - abstract_source: "metadata" or "pdf"
        - abstract_status: "success" or "failed"
        - abstract_error: error message if failed
        - conclusion: extracted conclusion text (if extract_conclusion)
        - conclusion_source: "pdf"
        - conclusion_status: "success", "failed", or "skipped"
    """
    results = []

    for paper, dl_result in zip(papers, download_results):
        result = {
            "abstract": None,
            "abstract_source": None,
            "abstract_status": "failed",
            "abstract_error": None,
        }

        # Try metadata abstract first
        if paper.abstract:
            result["abstract"] = paper.abstract
            result["abstract_source"] = "metadata"
            result["abstract_status"] = "success"
        elif dl_result["status"] == "success":
            # Try extracting from PDF
            try:
                pdf_abstract = extract_abstract_from_pdf(dl_result["path"])
                if pdf_abstract:
                    result["abstract"] = pdf_abstract
                    result["abstract_source"] = "pdf"
                    result["abstract_status"] = "success"
                else:
                    result["abstract_error"] = "Could not find abstract in PDF"
            except Exception as e:
                result["abstract_error"] = str(e)
        else:
            result["abstract_error"] = "No abstract in metadata and PDF not available"

        # Extract conclusion if requested
        if extract_conclusion:
            result["conclusion"] = None
            result["conclusion_source"] = None
            result["conclusion_status"] = "skipped"

            if dl_result["status"] == "success":
                try:
                    conclusion = extract_conclusion_from_pdf(dl_result["path"])
                    if conclusion:
                        result["conclusion"] = conclusion
                        result["conclusion_source"] = "pdf"
                        result["conclusion_status"] = "success"
                    else:
                        result["conclusion_status"] = "failed"
                        result["conclusion_error"] = "Could not find conclusion in PDF"
                except Exception as e:
                    result["conclusion_status"] = "failed"
                    result["conclusion_error"] = str(e)
            else:
                result["conclusion_error"] = "PDF not available"

        results.append(result)

    return results
