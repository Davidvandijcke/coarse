"""Post-processing quote verification against paper text.

Programmatically verifies that comment quotes are actual substrings of the paper.
Uses fuzzy matching to correct garbled quotes from PDF extraction artifacts.
"""
from __future__ import annotations

import difflib
import logging

from coarse.types import DetailedComment

logger = logging.getLogger(__name__)

# Minimum fuzzy match ratio to accept a corrected quote
_MIN_MATCH_RATIO = 0.70


def verify_quotes(
    comments: list[DetailedComment],
    paper_text: str,
    drop_unverified: bool = True,
) -> list[DetailedComment]:
    """Verify and correct quotes in comments against the paper text.

    For each comment:
    - If quote is an exact substring of paper_text: keep as-is
    - If fuzzy match ratio > _MIN_MATCH_RATIO: replace with nearest passage
    - If drop_unverified=True and ratio < threshold: DROP the comment entirely
    - If drop_unverified=False and ratio < threshold: prefix with "[approximate] "

    Returns a new list of DetailedComment with corrected quotes.
    """
    paper_lower = paper_text.lower()
    result = []

    for comment in comments:
        if not comment.quote or not comment.quote.strip():
            result.append(comment)
            continue

        # Exact substring match (case-insensitive)
        if comment.quote.lower() in paper_lower:
            result.append(comment)
            continue

        # Fuzzy match: find the best matching passage
        best_match, ratio = _find_nearest_passage(comment.quote, paper_text)

        if ratio >= _MIN_MATCH_RATIO and best_match:
            corrected = comment.model_copy(update={"quote": best_match})
            result.append(corrected)
        elif drop_unverified:
            logger.info(
                "Dropping comment '%s' — quote not found in paper (ratio=%.2f)",
                comment.title, ratio,
            )
        else:
            flagged = comment.model_copy(
                update={"quote": f"[approximate] {comment.quote}"}
            )
            result.append(flagged)

    return result


def _find_nearest_passage(
    quote: str, paper_text: str, window_factor: float = 1.5
) -> tuple[str, float]:
    """Find the passage in paper_text most similar to quote.

    Uses a sliding window of length ~ len(quote) * window_factor and
    SequenceMatcher to find the best match.

    Returns (best_matching_passage, match_ratio).
    """
    if not quote or not paper_text:
        return "", 0.0

    quote_len = len(quote)
    window_size = int(quote_len * window_factor)

    # For very short quotes, increase window
    window_size = max(window_size, 50)
    # For very long paper text, cap the search window step
    step = max(1, quote_len // 4)

    best_ratio = 0.0
    best_passage = ""

    quote_lower = quote.lower()

    for i in range(0, len(paper_text) - min(quote_len, len(paper_text)) + 1, step):
        candidate = paper_text[i : i + window_size]
        ratio = difflib.SequenceMatcher(
            None, quote_lower, candidate.lower()
        ).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_passage = candidate

    # Refine: try to trim the best passage to match quote length more closely
    if best_passage and best_ratio >= _MIN_MATCH_RATIO:
        best_passage = _trim_to_best_match(quote, best_passage)

    return best_passage, best_ratio


def _trim_to_best_match(quote: str, passage: str) -> str:
    """Find the subsequence of passage that best matches quote, allowing slight expansion."""
    if len(passage) <= len(quote):
        return passage

    # Allow window up to 1.5x quote length to recover truncated quotes
    window = min(len(passage), int(len(quote) * 1.5))
    best_ratio = 0.0
    best_sub = passage[:window]

    for start in range(0, len(passage) - window + 1, max(1, window // 8)):
        sub = passage[start : start + window]
        ratio = difflib.SequenceMatcher(None, quote.lower(), sub.lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_sub = sub

    return best_sub
