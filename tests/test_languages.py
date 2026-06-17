"""Tests for src/coarse/languages.py — catalog + resolution."""

from __future__ import annotations

from coarse.languages import (
    SUPPORTED_LANGUAGES,
    coerce_detected_code,
    is_supported,
    language_name,
    normalize_code,
    resolve_language_context,
    text_direction,
)

# --- catalog basics ---


def test_normalize_code_bcp47_casing():
    assert normalize_code("ZH-hant") == "zh-Hant"
    assert normalize_code("pt_br") == "pt-BR"
    assert normalize_code("ES") == "es"
    assert normalize_code(" en ") == "en"
    assert normalize_code(None) == ""
    assert normalize_code("") == ""


def test_language_name_and_direction():
    assert language_name("es") == "Spanish"
    assert language_name("zh-Hant") == "Traditional Chinese"
    assert language_name("xx") is None
    assert language_name("") is None
    assert text_direction("ar") == "rtl"
    assert text_direction("es") == "ltr"
    assert text_direction("unknown") == "ltr"
    assert text_direction("") == "ltr"


def test_is_supported():
    assert is_supported("ar") is True
    assert is_supported("ZH-hant") is True  # normalized
    assert is_supported("zh") is False  # ambiguous bare Chinese
    assert is_supported("") is False


# --- coerce_detected_code: lenient mapping of model output ---


def test_coerce_detected_code_exact_and_regional():
    assert coerce_detected_code("es") == "es"
    assert coerce_detected_code("pt-BR") == "pt"  # region dropped
    assert coerce_detected_code("es-419") == "es"  # numeric region dropped
    assert coerce_detected_code("ja-JP") == "ja"
    assert coerce_detected_code("zh-Hant-HK") == "zh-Hant"  # keep script, drop region
    assert coerce_detected_code("zh-Hans") == "zh-Hans"


def test_coerce_detected_code_unmappable():
    assert coerce_detected_code("zh") == ""  # ambiguous Hans/Hant -> English path
    assert coerce_detected_code("xx") == ""
    assert coerce_detected_code("") == ""
    assert coerce_detected_code(None) == ""


# --- resolve_language_context ---


def test_resolve_english_detected_is_byte_identical_path():
    directive, ctx = resolve_language_context(explicit=None, detected_code="en")
    assert directive is None  # no directive -> byte-identical English output
    assert ctx.review_language == "en"
    assert ctx.paper_language == "en"
    assert ctx.text_direction == "ltr"


def test_resolve_unknown_paper_no_directive():
    directive, ctx = resolve_language_context(explicit=None, detected_code="")
    assert directive is None
    assert ctx.review_language == ""
    assert ctx.paper_language == ""


def test_resolve_explicit_english_also_no_directive():
    """Selecting English explicitly must collapse to the byte-identical path."""
    for value in ("en", "English", "ENGLISH"):
        directive, ctx = resolve_language_context(explicit=value, detected_code="es")
        assert directive is None, f"explicit {value!r} should inject no directive"
        assert ctx.review_language == "en"


def test_resolve_detected_nonenglish():
    directive, ctx = resolve_language_context(explicit=None, detected_code="es")
    assert directive == "Spanish"
    assert ctx.review_language == "es"
    assert ctx.paper_language == "es"
    assert ctx.paper_language_source == "detected"
    assert ctx.text_direction == "ltr"


def test_resolve_explicit_overrides_detection_and_marks_user():
    # French paper, user explicitly wants German.
    directive, ctx = resolve_language_context(explicit="German", detected_code="fr")
    assert directive == "German"
    assert ctx.review_language == "de"
    assert ctx.paper_language == "fr"  # paper language still recorded
    assert ctx.paper_language_source == "user"


def test_resolve_explicit_code_accepted():
    directive, ctx = resolve_language_context(explicit="ja", detected_code="en")
    assert directive == "Japanese"
    assert ctx.review_language == "ja"
    assert ctx.paper_language_source == "user"


def test_resolve_rtl_review_language():
    directive, ctx = resolve_language_context(explicit="ar", detected_code="ar")
    assert directive == "Arabic"
    assert ctx.text_direction == "rtl"


def test_resolve_site_fallback():
    # No explicit, paper undetected -> fall back to site language.
    directive, ctx = resolve_language_context(explicit=None, detected_code="", site_code="fr")
    assert directive == "French"
    assert ctx.review_language == "fr"
    assert ctx.paper_language_source == "default"


def test_resolve_freeform_language_does_not_crash():
    """An unrecognized explicit name still steers the model (code unknown)."""
    directive, ctx = resolve_language_context(explicit="Catalan", detected_code="en")
    assert directive == "Catalan"
    assert ctx.review_language == ""  # no catalog code
    assert ctx.text_direction == "ltr"


def test_resolve_regional_detection_localizes():
    # A Brazilian-Portuguese detection ("pt-BR") must still localize to Portuguese.
    directive, ctx = resolve_language_context(explicit=None, detected_code="pt-BR")
    assert directive == "Portuguese"
    assert ctx.review_language == "pt"
    assert ctx.paper_language == "pt"


def test_catalog_has_expected_languages():
    # Dutch + Arabic explicitly included; Arabic is the lone RTL.
    assert SUPPORTED_LANGUAGES["nl"]["name"] == "Dutch"
    assert SUPPORTED_LANGUAGES["ar"]["direction"] == "rtl"
    rtl = [c for c, e in SUPPORTED_LANGUAGES.items() if e["direction"] == "rtl"]
    assert rtl == ["ar"]
