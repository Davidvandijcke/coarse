"""Format-specific extraction backends for non-OpenRouter paths."""

from __future__ import annotations

import re
from pathlib import Path

from coarse.types import ExtractionError


def _extract_docling(path: Path) -> str:
    """Extract via Docling (free, offline). Supports PDF, DOCX, HTML, LaTeX."""
    from docling.document_converter import DocumentConverter

    converter = DocumentConverter()
    result = converter.convert(str(path))
    return result.document.export_to_markdown(page_break_placeholder="<!-- PAGE BREAK -->")


def _extract_plaintext(path: Path) -> str:
    """Read a plain text or markdown file as-is."""
    return path.read_text(encoding="utf-8")


_LATEX_HEADING_RE = re.compile(r"\\(section|subsection|subsubsection|paragraph)\*?\{([^}]*)\}")
_LATEX_HEADING_LEVEL = {
    "section": "#",
    "subsection": "##",
    "subsubsection": "###",
    "paragraph": "####",
}
_LATEX_PREAMBLE_RE = re.compile(
    r"^\\(documentclass|usepackage|title|author|date|maketitle"
    r"|begin\{document\}|end\{document\})\b.*$",
    re.MULTILINE,
)


def _extract_latex_regex(path: Path) -> str:
    """Extract from LaTeX source with heading conversion to markdown."""
    text = path.read_text(encoding="utf-8")
    text = _LATEX_PREAMBLE_RE.sub("", text)
    text = _LATEX_HEADING_RE.sub(lambda m: f"{_LATEX_HEADING_LEVEL[m.group(1)]} {m.group(2)}", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_html_markdownify(path: Path) -> str:
    """Convert HTML to markdown via markdownify (lightweight fallback)."""
    try:
        import markdownify
    except ImportError:
        raise ExtractionError(
            "HTML extraction requires markdownify: pip install coarse-ink[formats]"
        )
    html_str = path.read_text(encoding="utf-8")
    return markdownify.markdownify(html_str, heading_style="ATX")


def _extract_docx_mammoth(path: Path) -> str:
    """Convert DOCX to markdown via mammoth (lightweight fallback)."""
    try:
        import mammoth
    except ImportError:
        raise ExtractionError("DOCX extraction requires mammoth: pip install coarse-ink[formats]")
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
            "EPUB extraction requires ebooklib and markdownify: pip install coarse-ink[formats]"
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
