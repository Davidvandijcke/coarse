"""Tests for src/coarse/review_labels.py — localized review + email labels."""

from __future__ import annotations

from coarse.review_labels import (
    _EMAIL,
    _EMAIL_EN,
    _EMAIL_KEYS,
    _EN,
    _LABEL_KEYS,
    _LABELS,
    email_completion_labels,
    review_labels,
)


def test_english_is_byte_identical_default():
    """Unknown/empty/None/'en' all return the exact English labels."""
    for code in (None, "", "en", "xx-unknown"):
        labels = review_labels(code)
        assert labels["overall_feedback"] == "Overall Feedback"
        assert labels["quote"] == "Quote"
        assert labels["feedback"] == "Feedback"
        assert labels["status"] == "Status"
        assert labels["pending"] == "Pending"


def test_every_language_defines_all_label_keys():
    for code, table in _LABELS.items():
        assert set(table) == set(_LABEL_KEYS), f"{code} label keys mismatch"


def test_localized_labels_differ_from_english():
    es = review_labels("es")
    assert es["overall_feedback"] == "Valoración general"
    assert es["quote"] == "Cita"
    # feedback ("Comentarios") must be distinct from active_comments
    assert es["feedback"] == "Comentarios"
    assert es["active_comments"] == "Comentarios activos"
    assert es["feedback"] != es["active_comments"]


def test_review_labels_always_complete():
    """Returned dict always has every key (English fill-in), so callers can
    index unconditionally even if a language omits a key."""
    for code in list(_LABELS) + ["en", "zz"]:
        labels = review_labels(code)
        for key in _LABEL_KEYS:
            assert key in labels and labels[key], (code, key)


def test_arabic_present_and_nonlatin():
    ar = review_labels("ar")
    assert ar["overall_feedback"] == "التقييم العام"


# --- completion email copy ---


def test_email_english_byte_identical():
    for code in (None, "", "en", "zz"):
        e = email_completion_labels(code)
        assert e["subject"] == "Your paper review is ready"
        assert e["ready"] == "Your review is ready."


def test_email_every_language_defines_all_keys():
    for code, table in _EMAIL.items():
        assert set(table) == set(_EMAIL_KEYS), f"{code} email keys mismatch"


def test_email_localized():
    es = email_completion_labels("es")
    assert es["subject"] == "La revisión de tu artículo está lista"
    assert es["view"].startswith("Ver tu revisión")


def test_email_languages_match_review_languages():
    """Email catalog covers the same language set as the review-label catalog."""
    assert set(_EMAIL) == set(_LABELS)


def test_english_catalogs_have_expected_key_counts():
    assert set(_EN) == set(_LABEL_KEYS)
    assert set(_EMAIL_EN) == set(_EMAIL_KEYS)
