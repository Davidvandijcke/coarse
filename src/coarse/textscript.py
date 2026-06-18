"""Script-aware text heuristics for non-English papers.

Token estimation and "is this a spaceless CJK script?" detection, used by the
cost gate / section-count heuristics and by quote verification. English/Latin
text is unaffected: ``estimate_tokens`` returns the same value as the old
``len(text) // 4`` for pure-Latin text, and ``is_cjk_heavy`` is False for it.
"""

from __future__ import annotations


def _is_cjk_char(ch: str) -> bool:
    """True for characters from spaceless CJK scripts (Han / Kana / Hangul).

    These scripts write without spaces between words and pack far more tokens
    per character than Latin text, so they need different token + tokenization
    heuristics.
    """
    o = ord(ch)
    return (
        0x3040 <= o <= 0x30FF  # Hiragana + Katakana
        or 0x3400 <= o <= 0x4DBF  # CJK Unified Ext A
        or 0x4E00 <= o <= 0x9FFF  # CJK Unified Ideographs
        or 0xF900 <= o <= 0xFAFF  # CJK Compatibility Ideographs
        or 0xAC00 <= o <= 0xD7A3  # Hangul syllables
        or 0x20000 <= o <= 0x2FA1F  # CJK Unified Ext B+ (supplementary)
    )


def cjk_fraction(text: str) -> float:
    """Fraction of non-whitespace characters that are CJK. 0.0 for English/empty."""
    non_space = [c for c in text if not c.isspace()]
    if not non_space:
        return 0.0
    return sum(_is_cjk_char(c) for c in non_space) / len(non_space)


# Above this fraction of CJK characters, treat the text as a spaceless script
# and switch off whitespace-tokenization heuristics.
_CJK_HEAVY_THRESHOLD = 0.2


def is_cjk_heavy(text: str) -> bool:
    """True if the text is predominantly a spaceless CJK script.

    Quote verification uses this to avoid whitespace ``.split()`` tokenization
    (which degenerates for CJK, where there are no inter-word spaces).
    """
    return cjk_fraction(text) >= _CJK_HEAVY_THRESHOLD


def estimate_tokens(text: str) -> int:
    """Estimate the LLM token count of ``text``, script-aware.

    Latin text averages ~4 characters per token; CJK averages ~1.6 because each
    ideograph/kana is roughly its own token. The old ``len(text) // 4`` under-
    counted CJK by ~2.5x (4 / 1.6), making the cost gate under-quote and the
    section-count heuristic misbehave on CJK papers. We bucket characters by
    script: CJK at ~1.6 chars/token, everything else at ~4 chars/token.

    For pure-Latin text this equals ``len(text) // 4`` exactly, so existing
    English cost estimates and section counts are unchanged.
    """
    if not text:
        return 0
    cjk = sum(1 for c in text if _is_cjk_char(c))
    other = len(text) - cjk
    return int(cjk / 1.6 + other / 4)
