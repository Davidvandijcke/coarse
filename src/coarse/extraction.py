"""Text extraction for coarse.

Supports PDF, TXT, MD, DOCX, TEX/LATEX, HTML, and EPUB.

PDF priority: Mistral OCR (direct) → OpenRouter → Docling.
DOCX/HTML/TEX: Docling (if installed) → lightweight fallback (mammoth/markdownify/regex).
TXT/MD: Direct read. EPUB: ebooklib + markdownify.
"""
from __future__ import annotations

import html
import json
import logging
import re
from pathlib import Path

from coarse.types import ExtractionError, PaperText

logger = logging.getLogger(__name__)

PAGE_BREAK = "\n\n<!-- PAGE BREAK -->\n\n"

SUPPORTED_EXTENSIONS = frozenset({
    ".pdf", ".txt", ".md", ".tex", ".latex",
    ".html", ".htm", ".docx", ".epub",
})


def _cache_path(pdf_path: Path) -> Path:
    """Return the cache file path for a given PDF."""
    return pdf_path.with_suffix(".extraction_cache.json")


def _load_cache(pdf_path: Path) -> PaperText | None:
    """Load cached extraction if it exists and is newer than the PDF."""
    cache = _cache_path(pdf_path)
    if not cache.exists():
        return None
    if cache.stat().st_mtime < pdf_path.stat().st_mtime:
        logger.info("Cache stale (PDF modified since cache), re-extracting")
        return None
    try:
        data = json.loads(cache.read_text(encoding="utf-8"))
        paper_text = PaperText.model_validate(data)
        logger.info("Loaded extraction cache from %s", cache.name)
        return paper_text
    except Exception:
        logger.warning("Cache corrupt, re-extracting")
        return None


def _save_cache(pdf_path: Path, paper_text: PaperText) -> None:
    """Save extraction result to cache file next to the PDF."""
    cache = _cache_path(pdf_path)
    try:
        cache.write_text(
            paper_text.model_dump_json(indent=None),
            encoding="utf-8",
        )
        size_kb = cache.stat().st_size / 1024
        logger.info("Saved extraction cache (%.1f KB) to %s", size_kb, cache.name)
    except Exception:
        logger.warning("Failed to write extraction cache, continuing without cache")


# ---------------------------------------------------------------------------
# Extraction backends
# ---------------------------------------------------------------------------


def _extract_mistral_direct(path: Path) -> str:
    """Extract via Mistral OCR API (requires MISTRAL_API_KEY)."""
    from litellm import ocr

    from coarse.config import resolve_api_key
    from coarse.models import OCR_MODEL

    key = resolve_api_key(OCR_MODEL)
    if not key:
        raise ValueError("No MISTRAL_API_KEY")

    response = ocr(
        model=OCR_MODEL,
        document={"type": "document_url", "document_url": f"file://{path.resolve()}"},
        api_key=key,
    )
    pages = response.pages
    if not pages:
        raise ValueError("Mistral OCR returned no pages")
    return PAGE_BREAK.join(page.markdown for page in pages)


_MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB


def _extract_mistral_openrouter(path: Path) -> str:
    """Extract via OpenRouter's Mistral OCR file-parser plugin."""
    import base64

    import requests

    from coarse.config import resolve_api_key
    from coarse.models import OPENROUTER_EXTRACTION_MODEL
    from coarse.prompts import OPENROUTER_EXTRACTION_PROMPT

    api_key = resolve_api_key("openrouter/auto")
    if not api_key:
        raise ValueError("No OPENROUTER_API_KEY")

    file_size = path.stat().st_size
    if file_size > _MAX_FILE_SIZE:
        raise ExtractionError(
            f"File too large ({file_size / 1024 / 1024:.0f} MB). "
            f"Maximum supported size is {_MAX_FILE_SIZE / 1024 / 1024:.0f} MB."
        )

    with open(path, "rb") as f:
        pdf_b64 = base64.b64encode(f.read()).decode()

    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": OPENROUTER_EXTRACTION_MODEL,
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": OPENROUTER_EXTRACTION_PROMPT},
                {"type": "file", "file": {
                    "filename": path.name,
                    "file_data": f"data:application/pdf;base64,{pdf_b64}",
                }},
            ]}],
            "plugins": [{"id": "file-parser", "pdf": {"engine": "mistral-ocr"}}],
        },
        timeout=300,
    )
    resp.raise_for_status()
    try:
        data = resp.json()
    except ValueError as e:
        raise ExtractionError(
            f"OpenRouter returned invalid JSON (HTTP {resp.status_code}): {e}"
        ) from e

    # Try annotations first (raw OCR output, no model modification)
    annotations = (
        data.get("choices", [{}])[0].get("message", {}).get("annotations", [])
    )
    for ann in annotations:
        if ann.get("type") == "file":
            texts = [
                p["text"]
                for p in ann["file"].get("content", [])
                if p.get("type") == "text"
            ]
            if texts:
                return PAGE_BREAK.join(texts)

    # Fallback: model response (asked to return text verbatim)
    content = data["choices"][0]["message"]["content"]
    if not content:
        raise ValueError("No content from OpenRouter OCR")
    return content


def _extract_docling(path: Path) -> str:
    """Extract via Docling (free, offline). Supports PDF, DOCX, HTML, LaTeX."""
    from docling.document_converter import DocumentConverter

    converter = DocumentConverter()
    result = converter.convert(str(path))
    return result.document.export_to_markdown(
        page_break_placeholder="<!-- PAGE BREAK -->"
    )


# ---------------------------------------------------------------------------
# Non-PDF extraction backends (lightweight fallbacks)
# ---------------------------------------------------------------------------


def _extract_plaintext(path: Path) -> str:
    """Read a plain text or markdown file as-is."""
    return path.read_text(encoding="utf-8")


# LaTeX heading patterns: \section{...}, \subsection{...}, etc.
_LATEX_HEADING_RE = re.compile(
    r"\\(section|subsection|subsubsection|paragraph)\*?\{([^}]*)\}"
)
_LATEX_HEADING_LEVEL = {
    "section": "#",
    "subsection": "##",
    "subsubsection": "###",
    "paragraph": "####",
}
# Preamble lines to strip (noise for the reviewer)
_LATEX_PREAMBLE_RE = re.compile(
    r"^\\(documentclass|usepackage|title|author|date|maketitle"
    r"|begin\{document\}|end\{document\})\b.*$",
    re.MULTILINE,
)


def _extract_latex_regex(path: Path) -> str:
    """Extract from LaTeX source with heading conversion to markdown.

    Converts \\section{X} → # X, etc. Strips preamble noise.
    Leaves math, environments, and all other content intact.
    """
    text = path.read_text(encoding="utf-8")
    # Strip preamble lines
    text = _LATEX_PREAMBLE_RE.sub("", text)
    # Convert LaTeX headings to markdown headings
    text = _LATEX_HEADING_RE.sub(
        lambda m: f"{_LATEX_HEADING_LEVEL[m.group(1)]} {m.group(2)}", text
    )
    # Clean up excessive blank lines from stripping
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_html_markdownify(path: Path) -> str:
    """Convert HTML to markdown via markdownify (lightweight fallback)."""
    try:
        import markdownify
    except ImportError:
        raise ExtractionError(
            "HTML extraction requires markdownify: pip install coarse[formats]"
        )
    html_str = path.read_text(encoding="utf-8")
    return markdownify.markdownify(html_str, heading_style="ATX")


def _extract_docx_mammoth(path: Path) -> str:
    """Convert DOCX to markdown via mammoth (lightweight fallback)."""
    try:
        import mammoth
    except ImportError:
        raise ExtractionError(
            "DOCX extraction requires mammoth: pip install coarse[formats]"
        )
    with open(path, "rb") as f:
        result = mammoth.convert_to_markdown(f)
    return result.value


def _extract_epub(path: Path) -> str:
    """Extract EPUB chapters to markdown via ebooklib + markdownify."""
    try:
        import ebooklib
        import markdownify
        from ebooklib import epub
    except ImportError:
        raise ExtractionError(
            "EPUB extraction requires ebooklib and markdownify: pip install coarse[formats]"
        )
    book = epub.read_epub(str(path))
    chapters = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        html_content = item.get_content().decode("utf-8", errors="replace")
        md = markdownify.markdownify(html_content, heading_style="ATX")
        md = md.strip()
        if md:
            chapters.append(md)
    if not chapters:
        raise ExtractionError(f"No text content found in EPUB: {path}")
    return "\n\n---\n\n".join(chapters)


# ---------------------------------------------------------------------------
# Garble detection and normalization
# ---------------------------------------------------------------------------

# Common OCR garble patterns from older PDFs (pre-2005, non-standard encodings)
_GARBLE_REPLACEMENTS: list[tuple[str, str]] = [
    ("®nite", "finite"),
    ("in®nite", "infinite"),
    ("de®ne", "define"),
    ("de®ned", "defined"),
    ("de®nition", "definition"),
    ("/C40", "("),
    ("/C41", ")"),
    ("naõÈve", "naïve"),
    ("naõève", "naïve"),
    ("\u00ae", "fi"),  # ® used as ligature for fi
]

# Mistral OCR glyph[...] artifact → Unicode mapping
_GLYPH_MAP: dict[str, str] = {
    "lscript": "ℓ", "epsilon1": "ε", "negationslash": "≠", "square": "□",
    "element": "∈", "arrowright": "→", "lessequal": "≤", "greaterequal": "≥",
    "infinity": "∞", "summation": "Σ", "integral": "∫", "partialdiff": "∂",
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


from coarse.garble import garble_ratio as compute_garble_ratio  # noqa: E402, F401


def normalize_ocr_garble(text: str) -> str:
    """Apply known OCR garble fixes to extracted text.

    Fixes common character encoding issues from older PDFs without
    altering correctly-encoded content.
    """
    result = text
    for garbled, clean in _GARBLE_REPLACEMENTS:
        result = result.replace(garbled, clean)
    return result


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def extract_text(pdf_path: str | Path, use_cache: bool = True) -> PaperText:
    """Extract text from a PDF file.

    Tries Mistral OCR (direct API, then OpenRouter plugin) for high-quality
    LaTeX extraction, falling back to Docling for offline use.

    Args:
        pdf_path: Path to the PDF file.
        use_cache: If True (default), use cached extraction when available.

    Returns:
        PaperText with full_markdown and token_estimate.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        ValueError: If no extraction backend can convert the file.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    with open(path, "rb") as f:
        magic = f.read(5)
    if magic != b"%PDF-":
        raise ExtractionError(f"File does not appear to be a PDF: {pdf_path}")

    # Try loading from cache first
    if use_cache:
        cached = _load_cache(path)
        if cached is not None:
            return cached

    # Priority: Mistral direct → OpenRouter → Docling
    extractors = [
        ("Mistral OCR (direct)", _extract_mistral_direct),
        ("Mistral OCR (OpenRouter)", _extract_mistral_openrouter),
        ("Docling", _extract_docling),
    ]
    full_markdown = None
    for name, fn in extractors:
        try:
            full_markdown = fn(path)
            logger.info("Extracted via %s (%d chars)", name, len(full_markdown))
            break
        except Exception as exc:
            logger.info("%s unavailable: %s", name, exc)

    if full_markdown is None:
        raise ValueError(
            f"Cannot convert PDF: no extraction backend available for {pdf_path}. "
            "Set MISTRAL_API_KEY or OPENROUTER_API_KEY, or install offline extraction: "
            "pip install coarse[docling]"
        )

    # Normalize Mistral OCR artifacts unconditionally
    full_markdown = normalize_mistral_artifacts(full_markdown)

    # Detect and normalize OCR garble from older PDFs
    garble = compute_garble_ratio(full_markdown)
    if garble > 0.001:
        logger.info("Garble ratio %.4f detected, applying OCR normalization", garble)
        full_markdown = normalize_ocr_garble(full_markdown)
        garble = compute_garble_ratio(full_markdown)  # recompute after normalization

    paper_text = PaperText(
        full_markdown=full_markdown,
        token_estimate=_estimate_tokens(full_markdown),
        garble_ratio=garble,
    )

    # Cache for next time
    if use_cache:
        _save_cache(path, paper_text)

    return paper_text


def _estimate_tokens(text: str) -> int:
    """Rough token estimate using the len // 4 heuristic."""
    return len(text) // 4


# ---------------------------------------------------------------------------
# Multi-format entry point
# ---------------------------------------------------------------------------

# Formats where Docling gives best quality (try first, fall back to lightweight)
_DOCLING_FORMATS = frozenset({".docx", ".html", ".htm", ".tex", ".latex"})
_FALLBACKS = {
    ".docx": _extract_docx_mammoth,
    ".html": _extract_html_markdownify,
    ".htm": _extract_html_markdownify,
    ".tex": _extract_latex_regex,
    ".latex": _extract_latex_regex,
}


def extract_file(file_path: str | Path, use_cache: bool = True) -> PaperText:
    """Extract text from any supported file format.

    For PDFs: Mistral OCR (direct) → OpenRouter → Docling.
    For DOCX/HTML/TEX: Docling (if installed) → lightweight fallback.
    For TXT/MD: direct read. For EPUB: ebooklib + markdownify.

    Args:
        file_path: Path to the file.
        use_cache: If True (default), use cached extraction when available.

    Returns:
        PaperText with full_markdown and token_estimate.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ExtractionError(
            f"Unsupported file format: {ext}. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    # PDFs: existing Mistral OCR → OpenRouter → Docling pipeline
    if ext == ".pdf":
        return extract_text(path, use_cache=use_cache)

    # Non-PDF: cache check
    if use_cache:
        cached = _load_cache(path)
        if cached is not None:
            return cached

    # Formats where Docling gives best quality
    if ext in _DOCLING_FORMATS:
        try:
            full_markdown = _extract_docling(path)
            logger.info("Extracted %s via Docling (%d chars)", ext, len(full_markdown))
        except Exception as exc:
            logger.info("Docling unavailable for %s: %s, using fallback", ext, exc)
            full_markdown = _FALLBACKS[ext](path)
    elif ext == ".epub":
        full_markdown = _extract_epub(path)
    else:  # .txt, .md
        full_markdown = _extract_plaintext(path)

    paper_text = PaperText(
        full_markdown=full_markdown,
        token_estimate=_estimate_tokens(full_markdown),
        garble_ratio=0.0,
    )
    if use_cache:
        _save_cache(path, paper_text)
    return paper_text
