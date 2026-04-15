"""Post-processing quote verification against paper text.

Programmatically verifies that comment quotes are actual substrings of the paper.
Uses fuzzy matching to correct garbled quotes from PDF extraction artifacts.
Applies stricter thresholds for math-heavy quotes where single-character changes
(e.g., an exponent or subscript) can completely alter the meaning.
"""

from __future__ import annotations

import difflib
import logging
import re
import unicodedata
from dataclasses import dataclass, field

from coarse.garble import garble_ratio as _passage_garble_score
from coarse.types import DetailedComment

logger = logging.getLogger(__name__)

# Minimum fuzzy match ratio to accept a corrected quote
_MIN_MATCH_RATIO = 0.80
# Stricter threshold for quotes containing math/numeric content
_MIN_MATH_MATCH_RATIO = 0.92
# Garble score above this indicates OCR-damaged source passage
_GARBLE_THRESHOLD = 0.005

# Pattern detecting math-heavy content: LaTeX commands, digits, operators
_MATH_PATTERN = re.compile(
    r"\\[a-zA-Z]+|"  # LaTeX commands (\frac, \phi, etc.)
    r"\$[^$]+\$|"  # inline math $...$
    r"\b\d+\.?\d*\b|"  # numbers
    r"[=<>≤≥±∑∏∫]"  # math operators
)
_TABLE_LINE_RE = re.compile(r"^\s*\|.*\|\s*$")


@dataclass
class QuoteVerificationDrop:
    """Dropped comment plus matching diagnostics for optional salvage."""

    comment: DetailedComment
    ratio: float
    threshold: float
    best_match: str = ""
    candidate_passages: list[str] = field(default_factory=list)
    math_heavy: bool = False


@dataclass
class QuoteVerificationResult:
    """Structured quote-verification result with dropped-comment diagnostics."""

    verified_comments: list[DetailedComment]
    dropped_comments: list[QuoteVerificationDrop]
    stats: dict[str, int]


def _is_math_heavy(text: str) -> bool:
    """Return True if the quote contains significant mathematical content."""
    if not text:
        return False
    matches = _MATH_PATTERN.findall(text)
    if not matches:
        return False
    # Consider math-heavy if density ≥5% AND (≥3 tokens or ≥10% density).
    # The 5% density floor stops three bare numbers in a prose paragraph
    # (e.g. "Table 3 shows 15.2 in 2020") from flipping to strict mode.
    math_len = sum(len(m) for m in matches)
    density = math_len / len(text)
    if density < 0.05:
        return False
    return len(matches) >= 3 or density > 0.10


def verify_quotes(
    comments: list[DetailedComment],
    paper_text: str,
    drop_unverified: bool = True,
) -> list[DetailedComment]:
    """Backward-compatible wrapper returning only verified comments."""
    return verify_quotes_detailed(
        comments,
        paper_text,
        drop_unverified=drop_unverified,
    ).verified_comments


def verify_quotes_detailed(
    comments: list[DetailedComment],
    paper_text: str,
    drop_unverified: bool = True,
) -> QuoteVerificationResult:
    """Verify and correct quotes in comments against the paper text.

    For each comment:
    - If quote is an exact substring of paper_text: keep as-is
    - If fuzzy match ratio > _MIN_MATCH_RATIO: replace with nearest passage
    - If drop_unverified=True and ratio < threshold: DROP the comment entirely
    - If drop_unverified=False and ratio < threshold: prefix with "[approximate] "

    Logs summary statistics about quote quality, including garble artifacts
    in matched source passages.

    Returns verified comments plus dropped-comment diagnostics for optional salvage.
    """
    paper_lower = paper_text.lower()
    result = []
    stats = {"exact": 0, "fuzzy": 0, "dropped": 0, "empty": 0, "garbled_source": 0}
    dropped: list[QuoteVerificationDrop] = []

    for comment in comments:
        if not comment.quote or not comment.quote.strip():
            stats["empty"] += 1
            result.append(comment)
            continue

        # Exact substring match (case-insensitive)
        if comment.quote.lower() in paper_lower:
            stats["exact"] += 1
            result.append(comment)
            continue

        # Normalized exact match: recover quotes that only differ by harmless
        # formatting drift such as line wraps, unicode dashes, or spacing.
        normalized_match = _find_normalized_substring(comment.quote, paper_text)
        if normalized_match:
            stats["fuzzy"] += 1
            corrected = comment.model_copy(update={"quote": normalized_match})
            result.append(corrected)
            continue

        table_match = _find_table_substring(comment.quote, paper_text)
        if table_match:
            stats["fuzzy"] += 1
            corrected = comment.model_copy(update={"quote": table_match})
            result.append(corrected)
            continue

        # Fuzzy match: find the best matching passage
        candidates = _find_candidate_passages(comment.quote, paper_text)
        best_match, ratio = candidates[0] if candidates else ("", 0.0)

        # Use stricter threshold for math-heavy quotes where single-char
        # changes (exponents, subscripts) alter meaning completely
        math_heavy = _is_math_heavy(comment.quote)
        threshold = _MIN_MATH_MATCH_RATIO if math_heavy else _MIN_MATCH_RATIO

        if ratio >= threshold and best_match:
            stats["fuzzy"] += 1
            # Track if the matched source passage itself is garbled
            garble_score = _passage_garble_score(best_match)
            if garble_score > _GARBLE_THRESHOLD:
                stats["garbled_source"] += 1
                logger.warning(
                    "Comment '%s' matched garbled source passage (garble_score=%.3f)",
                    comment.title,
                    garble_score,
                )
            corrected = comment.model_copy(update={"quote": best_match})
            result.append(corrected)
        elif drop_unverified:
            stats["dropped"] += 1
            dropped.append(
                QuoteVerificationDrop(
                    comment=comment,
                    ratio=ratio,
                    threshold=threshold,
                    best_match=best_match,
                    candidate_passages=[passage for passage, _ in candidates[:3] if passage],
                    math_heavy=math_heavy,
                )
            )
            logger.info(
                "Dropping comment '%s' — quote not found in paper (ratio=%.2f)",
                comment.title,
                ratio,
            )
        else:
            flagged = comment.model_copy(update={"quote": f"[approximate] {comment.quote}"})
            result.append(flagged)

    logger.info(
        "Quote verification: %d exact, %d fuzzy-corrected, %d dropped, %d garbled-source matches",
        stats["exact"],
        stats["fuzzy"],
        stats["dropped"],
        stats["garbled_source"],
    )

    return QuoteVerificationResult(
        verified_comments=result,
        dropped_comments=dropped,
        stats=stats,
    )


_MIN_WINDOW_SIZE = 50
_JACCARD_TOP_K = 5  # number of candidate chunks to refine with SequenceMatcher


def _tokenize(text: str) -> set[str]:
    """Split lowercased text into word-level tokens for Jaccard similarity."""
    return set(text.lower().split())


def _jaccard(a: set[str], b: set[str]) -> float:
    """Jaccard similarity between two token sets."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _find_nearest_passage(
    quote: str, paper_text: str, window_factor: float = 1.5
) -> tuple[str, float]:
    """Find the passage in paper_text most similar to quote.

    Uses a two-phase approach for performance:
    1. Cheap Jaccard pre-filter on overlapping chunks to find top-k candidates
    2. Expensive SequenceMatcher only on the top-k candidates

    Returns (best_matching_passage, match_ratio).
    """
    candidates = _find_candidate_passages(quote, paper_text, window_factor=window_factor, top_k=1)
    return candidates[0] if candidates else ("", 0.0)


def _find_candidate_passages(
    quote: str,
    paper_text: str,
    *,
    window_factor: float = 1.5,
    top_k: int = 3,
) -> list[tuple[str, float]]:
    """Return top candidate passages for a quote, sorted by similarity."""
    if not quote or not paper_text:
        return []

    quote_len = len(quote)
    window_size = max(int(quote_len * window_factor), _MIN_WINDOW_SIZE)
    step = max(1, quote_len // 4)

    quote_tokens = _tokenize(quote)
    stop = max(1, len(paper_text) - window_size + 1)
    candidates: list[tuple[float, int]] = []
    for i in range(0, stop, step):
        chunk = paper_text[i : i + window_size]
        score = _jaccard(quote_tokens, _tokenize(chunk))
        candidates.append((score, i))

    candidates.sort(key=lambda x: x[0], reverse=True)
    top_candidates = candidates[:_JACCARD_TOP_K]

    scored: list[tuple[str, float]] = []
    seen: set[str] = set()
    for _, i in top_candidates:
        candidate = paper_text[i : i + window_size]
        trimmed = _trim_to_best_match(quote, candidate)
        variants = [candidate, trimmed]
        best_variant = ""
        best_ratio = 0.0
        for variant in variants:
            ratio = _similarity_ratio(quote, variant)
            if ratio > best_ratio:
                best_ratio = ratio
                best_variant = variant
        canonical = _normalize_dedupe_key(best_variant)
        if best_variant and canonical not in seen:
            seen.add(canonical)
            scored.append((best_variant, best_ratio))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:top_k]


def _trim_to_best_match(quote: str, passage: str) -> str:
    """Find the subsequence of passage that best matches quote, allowing slight expansion."""
    if len(passage) <= len(quote):
        return passage

    quote_len = len(quote)
    max_window = min(len(passage), int(quote_len * 1.5))
    candidate_windows = sorted({quote_len, max_window, int(quote_len * 1.1), int(quote_len * 1.25)})
    best_ratio = 0.0
    best_sub = passage[:max_window]

    for window in candidate_windows:
        window = max(quote_len, min(window, len(passage)))
        step = max(1, window // 8)
        for start in range(0, len(passage) - window + 1, step):
            sub = passage[start : start + window]
            ratio = _similarity_ratio(quote, sub)
            if ratio > best_ratio + 0.02:
                best_ratio = ratio
                best_sub = sub
            elif ratio >= best_ratio - 0.02 and len(sub) > len(best_sub):
                best_ratio = ratio
                best_sub = sub

    if len(best_sub) <= quote_len:
        loc = passage.find(best_sub)
        if loc != -1:
            end = loc + len(best_sub)
            max_end = min(len(passage), end + max(4, quote_len // 8))
            while end < max_end and end < len(passage):
                ch = passage[end]
                end += 1
                if ch in ".,;:":
                    break
                if ch.isspace() and end > loc + len(best_sub) + 1:
                    break
            expanded = passage[loc:end].rstrip()
            if len(expanded) > len(best_sub):
                best_sub = expanded

    return best_sub


def _similarity_ratio(a: str, b: str) -> float:
    """Case-insensitive SequenceMatcher ratio."""
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _normalize_for_matching(text: str) -> tuple[str, list[int]]:
    """Normalize text for exact-ish matching while preserving an index map.

    Collapses whitespace and normalizes unicode variants that commonly differ
    between extracted paper text and LLM-copied quotes.
    """
    out: list[str] = []
    index_map: list[int] = []
    in_whitespace = False

    for idx, ch in enumerate(text):
        normalized = unicodedata.normalize("NFKC", ch)
        for norm_ch in normalized:
            if norm_ch in {"–", "—", "−"}:
                norm_ch = "-"
            elif norm_ch in {"“", "”"}:
                norm_ch = '"'
            elif norm_ch in {"‘", "’"}:
                norm_ch = "'"

            if norm_ch.isspace():
                if out and not in_whitespace:
                    out.append(" ")
                    index_map.append(idx)
                in_whitespace = True
                continue

            out.append(norm_ch.lower())
            index_map.append(idx)
            in_whitespace = False

    if out and out[-1] == " ":
        out.pop()
        index_map.pop()

    return "".join(out), index_map


def _find_normalized_substring(quote: str, paper_text: str) -> str:
    """Return the original paper span if quote matches after normalization."""
    if not quote or not paper_text:
        return ""

    norm_quote, _ = _normalize_for_matching(quote)
    norm_paper, index_map = _normalize_for_matching(paper_text)
    if not norm_quote or not norm_paper:
        return ""

    start = norm_paper.find(norm_quote)
    if start == -1:
        return ""

    end = start + len(norm_quote) - 1
    orig_start = index_map[start]
    orig_end = index_map[end] + 1
    return paper_text[orig_start:orig_end]


def _find_table_substring(quote: str, paper_text: str) -> str:
    """Return the original paper table span if canonicalized rows match."""
    quote_rows = _extract_table_rows(quote)
    if not quote_rows:
        return ""

    paper_lines = paper_text.splitlines()
    paper_rows: list[tuple[int, str]] = []
    for idx, line in enumerate(paper_lines):
        canonical = _canonicalize_table_line(line)
        if canonical:
            paper_rows.append((idx, canonical))

    if len(paper_rows) < len(quote_rows):
        return ""

    for start in range(0, len(paper_rows) - len(quote_rows) + 1):
        window = paper_rows[start : start + len(quote_rows)]
        if [row for _, row in window] == quote_rows:
            line_start = window[0][0]
            line_end = window[-1][0] + 1
            return "\n".join(paper_lines[line_start:line_end]).strip()

    return ""


def _normalize_dedupe_key(text: str) -> str:
    """Canonical key for de-duplicating candidate passages."""
    normalized, _ = _normalize_for_matching(text)
    return normalized


def _extract_table_rows(text: str) -> list[str]:
    """Extract canonical markdown table rows from text."""
    rows: list[str] = []
    for line in text.splitlines():
        canonical = _canonicalize_table_line(line)
        if canonical:
            rows.append(canonical)
    return rows


def _canonicalize_table_line(line: str) -> str:
    """Canonicalize a markdown table row, ignoring alignment whitespace."""
    if not _TABLE_LINE_RE.match(line):
        return ""

    raw_cells = line.strip().strip("|").split("|")
    cells = [re.sub(r"\s+", " ", cell.strip()) for cell in raw_cells]
    if not any(cells):
        return ""

    # Ignore markdown separator rows like | --- | :---: |.
    if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells if cell):
        return ""

    return "|".join(cells)
