"""Text extraction for coarse.

Supports PDF, TXT, MD, DOCX, TEX/LATEX, HTML, and EPUB.

Public API stays here; backend-specific helpers live in focused modules:
- extraction_cache.py
- extraction_openrouter.py
- extraction_formats.py
"""

from __future__ import annotations

import html
import logging
import os
import re
from pathlib import Path

from coarse import extraction_formats as _formats
from coarse import extraction_openrouter as _openrouter
from coarse.extraction_cache import _load_cache, _save_cache
from coarse.garble import garble_ratio as compute_garble_ratio
from coarse.garble import normalize_ocr_garble
from coarse.types import ExtractionError, PaperText

logger = logging.getLogger(__name__)

_extract_docling = _formats._extract_docling
_extract_docx_mammoth = _formats._extract_docx_mammoth
_extract_epub = _formats._extract_epub
_extract_html_markdownify = _formats._extract_html_markdownify
_extract_latex_regex = _formats._extract_latex_regex
_extract_plaintext = _formats._extract_plaintext
_LATEX_HEADING_LEVEL = _formats._LATEX_HEADING_LEVEL
_LATEX_HEADING_RE = _formats._LATEX_HEADING_RE

_MAX_FILE_SIZE = _openrouter.MAX_FILE_SIZE
_OCR_MAX_BACKOFF = _openrouter._OCR_MAX_BACKOFF
_OCR_MAX_RETRIES = _openrouter._OCR_MAX_RETRIES
_can_fall_through_api_error = _openrouter._can_fall_through_api_error
_classify_api_error = _openrouter._classify_api_error
_describe_api_error = _openrouter._describe_api_error
_extract_mistral_openrouter = _openrouter._extract_mistral_openrouter
_extract_pdftext_openrouter = _openrouter._extract_pdftext_openrouter
_response_was_billed = _openrouter._response_was_billed
_scrub_secrets = _openrouter._scrub_secrets


def _strip_nul_bytes(text: str) -> str:
    """Remove NUL bytes and literal \\u0000 escapes from an extracted string."""
    if not text:
        return text
    return text.replace("\x00", "").replace("\\u0000", "")


SUPPORTED_EXTENSIONS = frozenset(
    {
        ".pdf",
        ".txt",
        ".md",
        ".tex",
        ".latex",
        ".html",
        ".htm",
        ".docx",
        ".epub",
    }
)


# Minimum markdown length (in chars) below which we consider pymupdf4llm's
# output "empty enough to fall through to OCR". Scanned PDFs with no text
# layer tend to return <50 chars; real academic papers return much more.
_PYMUPDF4LLM_MIN_CHARS = 200


def _extract_pymupdf4llm(path: Path) -> str:
    """Fast pure-Python PDF extraction for text-bearing PDFs."""
    try:
        import pymupdf4llm
    except ImportError as exc:
        raise ExtractionError(
            "pymupdf4llm is not installed. Install it with "
            "`pip install pymupdf4llm` to enable the fast extraction path."
        ) from exc

    pymupdf4llm.use_layout(False)
    markdown = pymupdf4llm.to_markdown(str(path))
    if not isinstance(markdown, str):
        raise ExtractionError(
            f"pymupdf4llm.to_markdown returned {type(markdown).__name__}, expected str"
        )
    stripped = markdown.strip()
    if len(stripped) < _PYMUPDF4LLM_MIN_CHARS:
        raise ExtractionError(
            f"pymupdf4llm returned too little text ({len(stripped)} chars). "
            f"This is usually a scanned / image-only PDF with no text layer. "
            f"Falling through to the OCR cascade."
        )
    return markdown


_GLYPH_MAP: dict[str, str] = {
    "lscript": "ℓ",
    "epsilon1": "ε",
    "negationslash": "≠",
    "square": "□",
    "element": "∈",
    "arrowright": "→",
    "lessequal": "≤",
    "greaterequal": "≥",
    "infinity": "∞",
    "summation": "Σ",
    "integral": "∫",
    "partialdiff": "∂",
}
_GLYPH_RE = re.compile(r"glyph\[(\w+)\]")


def normalize_mistral_artifacts(text: str) -> str:
    """Normalize Mistral OCR artifacts (glyph[...], /lscript, HTML entities, etc.)."""
    result = text
    result = _GLYPH_RE.sub(lambda m: _GLYPH_MAP.get(m.group(1), m.group(0)), result)
    result = result.replace("/lscript", "ℓ")
    result = result.replace("<!-- formula-not-decoded -->", "")
    result = html.unescape(result)
    return result


def extract_text(pdf_path: str | Path, use_cache: bool = True) -> PaperText:
    """Extract text from a PDF file."""
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    file_size = path.stat().st_size
    if file_size > _MAX_FILE_SIZE:
        raise ExtractionError(
            f"File too large ({file_size / 1024 / 1024:.0f} MB). "
            f"Maximum supported size is {_MAX_FILE_SIZE // 1024 // 1024} MB."
        )

    with open(path, "rb") as f:
        magic = f.read(5)
    if magic != b"%PDF-":
        raise ExtractionError(f"File does not appear to be a PDF: {pdf_path}")

    if use_cache:
        cached = _load_cache(path)
        if cached is not None:
            return cached

    # Both modes keep Mistral OCR first. The fast path adds a local
    # pymupdf4llm fallback for the live handoff workflow.
    if os.environ.get("COARSE_EXTRACTION_FAST") == "1":
        extractors = [
            ("Mistral OCR (OpenRouter, chunked)", _extract_mistral_openrouter),
            ("pymupdf4llm", _extract_pymupdf4llm),
            ("pdf-text (OpenRouter)", _extract_pdftext_openrouter),
        ]
    else:
        extractors = [
            ("Mistral OCR (OpenRouter, chunked)", _extract_mistral_openrouter),
            ("pdf-text (OpenRouter)", _extract_pdftext_openrouter),
            ("Docling", _extract_docling),
        ]

    full_markdown = None
    errors: list[str] = []
    for idx, (name, fn) in enumerate(extractors):
        try:
            full_markdown = fn(path)
            logger.info("Extracted via %s (%d chars)", name, len(full_markdown))
            break
        except Exception as exc:
            api_msg = _classify_api_error(exc)
            if api_msg:
                summary = _describe_api_error(exc)
                has_fallback = idx < len(extractors) - 1
                if has_fallback and _can_fall_through_api_error(name, exc, api_msg):
                    errors.append(f"{name}: {api_msg}")
                    if summary:
                        logger.warning(
                            "%s returned a recoverable API denial; trying fallback backend. %s",
                            name,
                            summary,
                        )
                    else:
                        logger.warning(
                            "%s returned a recoverable API denial; trying fallback backend: %s",
                            name,
                            api_msg,
                        )
                    continue
                if summary:
                    logger.warning("%s failed with API error: %s", name, summary)
                raise ExtractionError(api_msg) from exc
            scrubbed = _scrub_secrets(str(exc))
            errors.append(f"{name}: {scrubbed}")
            logger.warning("%s failed: %s", name, scrubbed)

    if full_markdown is None:
        detail = _scrub_secrets("; ".join(errors))
        raise ExtractionError(f"Cannot convert PDF: all extraction backends failed. {detail}")

    full_markdown = normalize_mistral_artifacts(full_markdown)
    full_markdown = _strip_nul_bytes(full_markdown)

    garble = compute_garble_ratio(full_markdown)
    if garble > 0.001:
        logger.info("Garble ratio %.4f detected, applying OCR normalization", garble)
        full_markdown = normalize_ocr_garble(full_markdown)
        garble = compute_garble_ratio(full_markdown)

    paper_text = PaperText(
        full_markdown=full_markdown,
        token_estimate=_estimate_tokens(full_markdown),
        garble_ratio=garble,
    )

    if use_cache:
        _save_cache(path, paper_text)

    return paper_text


def _estimate_tokens(text: str) -> int:
    """Rough token estimate using the len // 4 heuristic."""
    return len(text) // 4


def _has_meaningful_markdown(text: str) -> bool:
    """Return True when extracted markdown contains non-whitespace content."""
    return bool(text.strip())


_DOCLING_FORMATS = frozenset({".docx", ".html", ".htm", ".tex", ".latex"})
_FALLBACKS = {
    ".docx": _extract_docx_mammoth,
    ".html": _extract_html_markdownify,
    ".htm": _extract_html_markdownify,
    ".tex": _extract_latex_regex,
    ".latex": _extract_latex_regex,
}


def extract_file(file_path: str | Path, use_cache: bool = True) -> PaperText:
    """Extract text from any supported file format."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    file_size = path.stat().st_size
    if file_size > _MAX_FILE_SIZE:
        raise ExtractionError(
            f"File too large ({file_size / 1024 / 1024:.0f} MB). "
            f"Maximum supported size is {_MAX_FILE_SIZE // 1024 // 1024} MB."
        )

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ExtractionError(
            f"Unsupported file format: {ext}. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    if ext == ".pdf":
        return extract_text(path, use_cache=use_cache)

    if use_cache:
        cached = _load_cache(path)
        if cached is not None:
            return cached

    if ext in _DOCLING_FORMATS:
        try:
            full_markdown = _extract_docling(path)
            if not _has_meaningful_markdown(full_markdown):
                raise ExtractionError("Docling returned empty content")
            logger.info("Extracted %s via Docling (%d chars)", ext, len(full_markdown))
        except Exception as exc:
            logger.info("Docling unusable for %s: %s, using fallback", ext, exc)
            full_markdown = _FALLBACKS[ext](path)
    elif ext == ".epub":
        full_markdown = _extract_epub(path)
    else:
        full_markdown = _extract_plaintext(path)

    full_markdown = _strip_nul_bytes(full_markdown)

    paper_text = PaperText(
        full_markdown=full_markdown,
        token_estimate=_estimate_tokens(full_markdown),
        garble_ratio=0.0,
    )
    if use_cache:
        _save_cache(path, paper_text)
    return paper_text
