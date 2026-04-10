"""Tests for coarse.garble — OCR garble detection and normalization."""
from coarse.garble import garble_ratio, normalize_ocr_garble


def test_garble_ratio_clean_text():
    assert garble_ratio("Hello world, this is clean text.") == 0.0


def test_garble_ratio_empty():
    assert garble_ratio("") == 0.0


def test_garble_ratio_garbled():
    text = "de®ne the in®nite set"
    ratio = garble_ratio(text)
    assert ratio > 0.0


def test_garble_ratio_glyph_artifacts():
    text = "The glyph[lscript] and glyph[epsilon1] symbols"
    ratio = garble_ratio(text)
    assert ratio > 0.0


def test_normalize_ocr_garble_fixes_known_patterns():
    assert normalize_ocr_garble("de®ne") == "define"
    assert normalize_ocr_garble("in®nite") == "infinite"
    assert normalize_ocr_garble("de®nition") == "definition"
    assert normalize_ocr_garble("/C40x/C41") == "(x)"


def test_normalize_ocr_garble_preserves_clean():
    assert normalize_ocr_garble("hello world") == "hello world"


def test_normalize_ocr_garble_fixes_naive():
    assert normalize_ocr_garble("naõÈve") == "naïve"
    assert normalize_ocr_garble("naõève") == "naïve"
