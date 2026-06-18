"""Shared OCR garble detection utilities.

Used by extraction and quote verification to detect/score garbled text.
"""

from __future__ import annotations

import re

# Regex matching non-standard characters that suggest OCR garbling.
#
# Only true garble markers belong here. Accented Latin code points
# (À U+00C0, Á U+00C1, È U+00C8, õ U+00F5) and the registered-
# trademark symbol ® (U+00AE) are legitimate in French, Portuguese, Spanish,
# Italian, etc., so they must NOT inflate the garble ratio for clean non-English
# text.
# What remains are unambiguous artifacts: the Unicode replacement character,
# the non-characters U+FFFE/U+FFFF, and the old-PDF glyph/operator patterns.
GARBLE_CHARS = re.compile(
    r"[\ufffd\ufffe\uffff]"
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


# Common OCR garble patterns from older PDFs (pre-2005, non-standard encodings).
#
# Every entry here is a multi-character string that only ever appears as genuine
# garble. The bare single-character mapping ("®" -> "fi") was intentionally
# removed: ® is a legitimate registered-trademark symbol, and a global replace
# corrupted any real ® in clean text. The specific patterns below ("de®ned",
# "in®nite", "naõÈve", ...) are unambiguous artifacts of the broken fi-ligature
# encoding and remain safe to fix.
_GARBLE_REPLACEMENTS: list[tuple[str, str]] = [
    ("/C40", "("),
    ("/C41", ")"),
    ("naõÈve", "naïve"),
    ("naõève", "naïve"),
]

# Broken fi-ligature: older PDFs mis-encode the "fi" ligature as ® *followed by
# a letter* (de®ned -> defined, ®nite -> finite, speci®c -> specific). The
# distinguishing feature vs. a legitimate trademark is the FOLLOWING character: a
# fi-ligature ® is followed by a letter; a trademark ® ("Acme®", "(®)") is
# followed by a space, punctuation, or end-of-string — so a trailing-letter
# lookahead repairs the whole ligature long tail (including word-initial ®nite)
# while leaving real ® symbols untouched.
_FI_LIGATURE_RE = re.compile(r"®(?=[A-Za-z])")


def normalize_ocr_garble(text: str) -> str:
    """Apply known OCR garble fixes to extracted text.

    Fixes common character-encoding artifacts from older PDFs without altering
    correctly-encoded content. Safe to run unconditionally: on clean text every
    pattern is a no-op (the fi-ligature regex only matches ® *between* letters,
    so a trademark ® and legitimately-accented non-English text are left intact).
    """
    result = text
    for garbled, clean in _GARBLE_REPLACEMENTS:
        result = result.replace(garbled, clean)
    return _FI_LIGATURE_RE.sub("fi", result)
