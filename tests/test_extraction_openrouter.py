"""Tests for coarse.extraction_openrouter."""

from __future__ import annotations

import base64
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from coarse.extraction_openrouter import (
    _can_fall_through_api_error,
    _classify_api_error,
    _extract_openrouter_file_parser,
    _response_was_billed,
    signed_url_ctx,
)
from coarse.types import ExtractionError


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


@patch("coarse.config.resolve_api_key", return_value="fake-key")
def test_extract_openrouter_file_parser_rejects_large_files(
    mock_key, tmp_path: Path, monkeypatch
) -> None:
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    monkeypatch.setattr("coarse.extraction_openrouter.MAX_FILE_SIZE", 4)

    with pytest.raises(ExtractionError, match="File too large"):
        _extract_openrouter_file_parser(pdf, engine="pdf-text")


@patch("coarse.prompts.OPENROUTER_EXTRACTION_PROMPT", "Extract verbatim")
@patch("coarse.models.OPENROUTER_EXTRACTION_MODEL", "google/gemini-test")
@patch("coarse.config.resolve_api_key", return_value="fake-key")
def test_extract_openrouter_file_parser_builds_expected_payload(mock_key, tmp_path: Path) -> None:
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4\nbody")
    response = MagicMock()
    response.raise_for_status.return_value = None

    with (
        patch("coarse.extraction_openrouter._post_openrouter_ocr", return_value=response) as post,
        patch(
            "coarse.extraction_openrouter._parse_openrouter_ocr_response",
            return_value="parsed markdown",
        ) as parse,
    ):
        result = _extract_openrouter_file_parser(pdf, engine="pdf-text")

    assert result == "parsed markdown"
    kwargs = post.call_args.kwargs
    assert kwargs["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert kwargs["timeout"] == 300
    assert kwargs["headers"] == {
        "Authorization": "Bearer fake-key",
        "Content-Type": "application/json",
    }
    assert kwargs["payload"]["model"] == "google/gemini-test"
    assert kwargs["payload"]["plugins"] == [{"id": "file-parser", "pdf": {"engine": "pdf-text"}}]

    message = kwargs["payload"]["messages"][0]
    assert message["role"] == "user"
    assert message["content"][0] == {"type": "text", "text": "Extract verbatim"}
    file_part = message["content"][1]
    assert file_part["type"] == "file"
    assert file_part["file"]["filename"] == "paper.pdf"
    assert file_part["file"]["file_data"].startswith("data:application/pdf;base64,")
    encoded = file_part["file"]["file_data"].split(",", 1)[1]
    assert base64.b64decode(encoded) == pdf.read_bytes()
    response.raise_for_status.assert_called_once_with()
    parse.assert_called_once_with(response)


@patch("coarse.prompts.OPENROUTER_EXTRACTION_PROMPT", "Extract verbatim")
@patch("coarse.models.OPENROUTER_EXTRACTION_MODEL", "google/gemini-test")
@patch("coarse.config.resolve_api_key", return_value="fake-key")
def test_extract_openrouter_file_parser_uses_signed_url_when_context_set(
    mock_key, tmp_path: Path
) -> None:
    """When signed_url_ctx is set, send the URL directly to OpenRouter
    instead of base64-encoding the file into the request body.

    This is the fix path for large PDFs: OpenRouter's inline base64
    limit (~8-16 MB) rejects 20 MB papers before Mistral OCR sees
    them, but the URL path bypasses the request-body limit entirely.
    """
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4\n" + b"large body " * 10000)
    signed_url = "https://example.supabase.co/storage/v1/object/sign/papers/abc.pdf?token=abc"
    response = MagicMock()
    response.raise_for_status.return_value = None

    token = signed_url_ctx.set(signed_url)
    try:
        with (
            patch(
                "coarse.extraction_openrouter._post_openrouter_ocr",
                return_value=response,
            ) as post,
            patch(
                "coarse.extraction_openrouter._parse_openrouter_ocr_response",
                return_value="parsed markdown",
            ),
        ):
            result = _extract_openrouter_file_parser(pdf, engine="mistral-ocr")
    finally:
        signed_url_ctx.reset(token)

    assert result == "parsed markdown"
    file_part = post.call_args.kwargs["payload"]["messages"][0]["content"][1]
    # URL passed straight through — no base64 prefix anywhere.
    assert file_part["file"]["file_data"] == signed_url
    assert "base64" not in file_part["file"]["file_data"]
    # Filename still derived from the local path (unchanged behavior).
    assert file_part["file"]["filename"] == "paper.pdf"
    # Engine routing still works for both mistral-ocr and pdf-text.
    assert post.call_args.kwargs["payload"]["plugins"] == [
        {"id": "file-parser", "pdf": {"engine": "mistral-ocr"}}
    ]


@patch("coarse.prompts.OPENROUTER_EXTRACTION_PROMPT", "Extract verbatim")
@patch("coarse.models.OPENROUTER_EXTRACTION_MODEL", "google/gemini-test")
@patch("coarse.config.resolve_api_key", return_value="fake-key")
def test_extract_openrouter_file_parser_clears_signed_url_after_reset(
    mock_key, tmp_path: Path
) -> None:
    """Resetting the contextvar restores the base64 fallback path.

    Guards against contextvar leakage between extraction calls — a
    handoff run shouldn't accidentally influence a subsequent
    non-handoff run in the same process.
    """
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4\nbody")
    response = MagicMock()
    response.raise_for_status.return_value = None

    token = signed_url_ctx.set("https://example.supabase.co/file.pdf?token=abc")
    signed_url_ctx.reset(token)

    with (
        patch("coarse.extraction_openrouter._post_openrouter_ocr", return_value=response) as post,
        patch(
            "coarse.extraction_openrouter._parse_openrouter_ocr_response",
            return_value="parsed markdown",
        ),
    ):
        _extract_openrouter_file_parser(pdf, engine="pdf-text")

    file_data = post.call_args.kwargs["payload"]["messages"][0]["content"][1]["file"]["file_data"]
    assert file_data.startswith("data:application/pdf;base64,")
