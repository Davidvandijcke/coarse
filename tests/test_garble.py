"""Tests for coarse.garble — OCR garble detection and normalization.

Covers the i18n de-Anglicization fix: legitimately-accented non-English text
(French, Portuguese, Spanish, Italian) and real trademark symbols must NOT be
flagged as garble or corrupted by normalization, while genuine old-PDF garble
strings must still be detected and repaired.
"""

from coarse.garble import garble_ratio, normalize_ocr_garble

# ---------------------------------------------------------------------------
# (a) Romance / accented text -> ratio 0.0 and normalize is the identity.
# ---------------------------------------------------------------------------

ACCENTED_SAMPLES = [
    # French: includes the ï/é/à/è that previously tripped GARBLE_CHARS.
    "naïve déjà résumé à la Côte d'Azur où l'élève étudie.",
    # Portuguese: São Paulo, função, and a bare õ in "razões".
    "São Paulo: a função das razões é clara, não há ambiguidade.",
    # Spanish: García, ñ, and accented vowels.
    "José García analizó el ñandú con atención increíble.",
    # Italian: città, è (the accented grave that was flagged).
    "La città è bella; perché non andiamo lì oggi?",
    # Capitalized accented Latin letters that were explicitly removed
    # from GARBLE_CHARS: À, Á, È, õ.
    "À Á È õ — Élève Ámbar Ève Õrlando.",
]


def test_accented_text_has_zero_garble_ratio():
    """Legitimate Romance-language accents must not inflate the ratio."""
    for sample in ACCENTED_SAMPLES:
        assert garble_ratio(sample) == 0.0, sample


def test_accented_text_normalizes_unchanged():
    """normalize_ocr_garble is the identity on clean accented text."""
    for sample in ACCENTED_SAMPLES:
        assert normalize_ocr_garble(sample) == sample, sample


def test_individual_removed_codepoints_not_flagged():
    """À, Á, È, õ on their own must not count as garble."""
    for char in ("À", "Á", "È", "õ"):  # À Á È õ
        assert garble_ratio(char) == 0.0, repr(char)
        assert normalize_ocr_garble(char) == char, repr(char)


# ---------------------------------------------------------------------------
# (b) A real ® trademark in clean text -> not flagged, not corrupted.
# ---------------------------------------------------------------------------


def test_registered_trademark_not_flagged():
    """A genuine ® in clean prose must yield a zero garble ratio."""
    text = "We benchmarked Acme® and Globex® against the Initech® suite."
    assert garble_ratio(text) == 0.0


def test_registered_trademark_not_corrupted():
    """The dangerous bare ® -> 'fi' replacement must be gone."""
    text = "We benchmarked Acme® and Globex® against the Initech® suite."
    assert normalize_ocr_garble(text) == text
    # Belt-and-suspenders: the old bug rewrote every ® to "fi".
    assert "fi" not in normalize_ocr_garble("Acme®")
    assert normalize_ocr_garble("Acme®") == "Acme®"


def test_bare_trademark_alone_is_identity():
    text = "Product®"  # Product®
    assert garble_ratio(text) == 0.0
    assert normalize_ocr_garble(text) == text


# ---------------------------------------------------------------------------
# (c) Genuine garble strings still detected and repaired.
# ---------------------------------------------------------------------------


def test_hard_garble_markers_detected_by_ratio():
    """garble_ratio still flags the unambiguous hard markers.

    Note: the ®-based fi-ligature garble (e.g. "de®ned") is intentionally
    NOT detected by garble_ratio anymore, because a bare ® is a legitimate
    trademark symbol — it is handled at the normalization layer instead
    (see test_genuine_garble_strings_repaired). The hard markers below have
    no legitimate use and remain ratio-detectable.
    """
    for text in (
        "glyph[c3] appears here",
        "operator /C40 and /C41",
        "corrupted � replacement",  # U+FFFD replacement char
        "the /lscript operator",
    ):
        assert garble_ratio(text) > 0.0, text


def test_bare_trademark_does_not_raise_ratio():
    """The core of the fix: a standalone ® must not inflate the ratio,
    even though the ®-ligature garble strings still get repaired.
    """
    assert garble_ratio("de®ned the in®nite set") == 0.0
    assert garble_ratio("Acme® ships worldwide") == 0.0


def test_genuine_garble_strings_repaired():
    assert normalize_ocr_garble("de®ne") == "define"
    assert normalize_ocr_garble("de®ned") == "defined"
    assert normalize_ocr_garble("de®nition") == "definition"
    assert normalize_ocr_garble("in®nite") == "infinite"
    assert normalize_ocr_garble("the ®nite case") == "the finite case"
    assert normalize_ocr_garble("/C40x/C41") == "(x)"


def test_garbled_naive_still_repaired():
    """The unambiguous broken-ligature naïve spellings still get fixed."""
    assert normalize_ocr_garble("naõÈve") == "naïve"
    assert normalize_ocr_garble("naõève") == "naïve"


def test_replacement_char_counts_as_garble():
    """The Unicode replacement char remains a hard garble signal."""
    assert garble_ratio("���") > 0.0
    assert garble_ratio("￾") > 0.0
    assert garble_ratio("￿") > 0.0


# ---------------------------------------------------------------------------
# (d) Plain English / ASCII is unaffected.
# ---------------------------------------------------------------------------


def test_english_text_unaffected():
    text = "Hello world, this is clean ASCII text with numbers 123."
    assert garble_ratio(text) == 0.0
    assert normalize_ocr_garble(text) == text


def test_empty_string():
    assert garble_ratio("") == 0.0
    assert normalize_ocr_garble("") == ""


def test_clean_text_normalize_identity():
    assert normalize_ocr_garble("hello world") == "hello world"


def test_fi_ligature_repaired_between_letters():
    # The ® fi-ligature mis-encoding is repaired for the whole long tail
    # (context-gated regex), not just a hardcoded word list.
    assert normalize_ocr_garble("de®ned") == "defined"
    assert normalize_ocr_garble("in®nite") == "infinite"
    assert normalize_ocr_garble("speci®c classi®cation") == "specific classification"


def test_standalone_trademark_preserved():
    # A real registered-trademark ® (not between letters) is left intact.
    assert normalize_ocr_garble("Acme® product") == "Acme® product"
    assert normalize_ocr_garble("(®)") == "(®)"
