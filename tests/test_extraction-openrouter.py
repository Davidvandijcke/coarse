"""Tests for coarse.extraction_openrouter."""

from __future__ import annotations

from unittest.mock import MagicMock

from coarse.extraction_openrouter import (
    _can_fall_through_api_error,
    _classify_api_error,
    _response_was_billed,
)


def test_classify_api_error_maps_spend_limit_message() -> None:
    exc = RuntimeError("quota exceeded for this key")
    assert "spend limit" in (_classify_api_error(exc) or "")


def test_can_fall_through_api_error_for_openrouter_403() -> None:
    exc = RuntimeError("forbidden")
    exc.status_code = 403  # type: ignore[attr-defined]
    assert _can_fall_through_api_error("Mistral OCR (OpenRouter)", exc) is True


def test_response_was_billed_detects_positive_usage() -> None:
    resp = MagicMock()
    resp.json.return_value = {"usage": {"total_tokens": 5}}
    assert _response_was_billed(resp) is True
