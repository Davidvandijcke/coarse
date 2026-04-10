"""Tests for coarse.models — model manifest invariants."""
from coarse.models import (
    CHEAP_MODELS,
    DEFAULT_MODEL,
    JSON_MODE_PREFIXES,
    MARKDOWN_JSON_PREFIXES,
    OCR_MODEL,
    QUALITY_MODEL,
    VISION_MODEL,
)


def test_default_model_has_provider_prefix():
    assert "/" in DEFAULT_MODEL


def test_all_models_have_provider_prefix():
    for name, model_id in [
        ("VISION_MODEL", VISION_MODEL),
        ("OCR_MODEL", OCR_MODEL),
        ("QUALITY_MODEL", QUALITY_MODEL),
    ]:
        assert "/" in model_id, f"{name} missing provider prefix: {model_id}"


def test_cheap_models_have_provider_prefix():
    for env_var, model_id in CHEAP_MODELS.items():
        assert "/" in model_id, f"CHEAP_MODELS[{env_var}] missing prefix: {model_id}"


def test_json_and_markdown_prefixes_no_overlap():
    overlap = set(JSON_MODE_PREFIXES) & set(MARKDOWN_JSON_PREFIXES)
    assert not overlap, f"Overlap between JSON and MD_JSON prefixes: {overlap}"


def test_all_prefixes_are_lowercase():
    for p in JSON_MODE_PREFIXES:
        assert p == p.lower(), f"JSON prefix not lowercase: {p}"
    for p in MARKDOWN_JSON_PREFIXES:
        assert p == p.lower(), f"MD_JSON prefix not lowercase: {p}"
