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
