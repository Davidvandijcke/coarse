"""Shared text helpers for review agents and evaluation code."""

from __future__ import annotations

import re
from typing import Literal

from coarse.types import SectionInfo


def build_sections_text(sections: list[SectionInfo]) -> str:
    """Convert sections list to a text block with full, untruncated text."""
    parts: list[str] = []
    for sec in sections:
        if not sec.text:
            parts.append(f"## {sec.number}. {sec.title} ({sec.section_type.value})\n(empty)")
            continue
        parts.append(f"## {sec.number}. {sec.title} ({sec.section_type.value})\n{sec.text}")
    return "\n\n".join(parts)


def tokenize_text(text: str, *, mode: Literal["words", "whitespace"] = "words") -> set[str]:
    """Tokenize text into a lowercase token set.

    `quote_verify` needs whitespace-delimited tokens so punctuation-heavy
    claims like `p<0.05` remain distinct. Recall matching uses word tokens.
    """
    normalized = text.lower()
    if mode == "whitespace":
        return {token for token in normalized.split() if token}
    return set(re.findall(r"\w+", normalized))


def jaccard_similarity(a: set[str], b: set[str]) -> float:
    """Jaccard similarity between two token sets."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)
