"""Shared OCR garble detection utilities.

Used by extraction and quote verification to detect/score garbled text.
"""
from __future__ import annotations

import re

# Regex matching non-standard characters that suggest OCR garbling
GARBLE_CHARS = re.compile(
    r"[\u00ae\u00f5\u00c8\u00c0\u00c1\ufffd\ufffe\uffff]"
    r"|/C[0-9]{2}"
    r"|glyph\[\w+\]"
    r"|/lscript"
)


def garble_ratio(text: str) -> float:
    """Compute the ratio of garbled characters to total characters.

    Returns a float in [0, 1]. Values above ~0.005 suggest OCR quality issues.
    """
    if not text:
        return 0.0
    matches = GARBLE_CHARS.findall(text)
    return sum(len(m) for m in matches) / max(len(text), 1)


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


def normalize_ocr_garble(text: str) -> str:
    """Apply known OCR garble fixes to extracted text.

    Fixes common character encoding issues from older PDFs without
    altering correctly-encoded content.
    """
    result = text
    for garbled, clean in _GARBLE_REPLACEMENTS:
        result = result.replace(garbled, clean)
    return result
