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
    return len(matches) / max(len(text), 1)
