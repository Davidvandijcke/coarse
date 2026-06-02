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


def test_classify_api_error_detects_management_key_user_not_found() -> None:
    """OpenRouter returns 401 + body 'User not found' for provisioning keys.

    Generic 'Invalid API key' copy doesn't help the user — they need to
    know it's the wrong *kind* of key. Reproduces the friend's
    2026-04-20 submission where a pasted management key hit the inference
    endpoint.
    """
    resp = MagicMock()
    resp.status_code = 401
    resp.json.return_value = {"error": {"message": "User not found.", "code": 401}}
    exc = RuntimeError(
        "401 Client Error: Unauthorized for url: https://openrouter.ai/api/v1/chat/completions"
    )
    exc.response = resp  # type: ignore[attr-defined]

    msg = _classify_api_error(exc) or ""
    assert "provisioning" in msg.lower() or "management" in msg.lower()
    assert "openrouter.ai/settings/keys" in msg


def test_classify_api_error_keeps_generic_401_message_without_user_not_found() -> None:
    """A plain 401 with no 'User not found' body keeps the existing copy."""
    resp = MagicMock()
    resp.status_code = 401
    resp.json.return_value = {"error": {"message": "Unauthorized", "code": 401}}
    exc = RuntimeError("401 Unauthorized")
    exc.response = resp  # type: ignore[attr-defined]

    msg = _classify_api_error(exc) or ""
    assert msg == "Invalid API key. Check that your key is correct and active."


def test_setup_page_warns_about_provisioning_keys() -> None:
    """The setup page must surface the same guidance the Python
    classifier points users to.

    ``_classify_api_error``'s management-key branch tells the user to
    create a regular API key at openrouter.ai/settings/keys; the setup
    page's Step 3 must echo that guidance so a user who hits the error
    in Modal sees matching UI copy. A future edit that drops either
    half breaks the cross-reference silently — this test pins both the
    name of the wrong key type and the exact error string the
    classifier returns, so the drift surfaces at CI time rather than
    in a confused user's status page.
    """
    setup = Path(__file__).resolve().parents[1] / "web" / "src" / "app" / "setup" / "page.tsx"
    assert setup.exists(), "web/src/app/setup/page.tsx must exist"
    src = setup.read_text(encoding="utf-8")

    assert "provisioning" in src.lower(), (
        "setup page Step 3 must name the wrong key type ('provisioning' / "
        "'management') so users can self-diagnose. See the classifier "
        "message in src/coarse/extraction_openrouter.py."
    )
    assert "User not found" in src, (
        "setup page Step 3 must quote the exact 'User not found' error "
        "string users will see if they paste a provisioning key; drops "
        "the cross-reference with _classify_api_error otherwise."
    )


def test_classify_api_error_does_not_leak_management_key_copy_on_403() -> None:
    """A 403 with 'User not found' body must hit the 403 branch, not the
    401 management-key branch.

    Pins the scope of the management-key detection to 401 only so a
    later edit that widens the outer ``if`` can't silently misroute a
    legitimate forbidden response into provisioning-key remediation
    copy.
    """
    resp = MagicMock()
    resp.status_code = 403
    resp.json.return_value = {"error": {"message": "User not found.", "code": 403}}
    exc = RuntimeError("403 Forbidden")
    exc.response = resp  # type: ignore[attr-defined]

    msg = _classify_api_error(exc) or ""
    assert "provisioning" not in msg.lower()
    assert "management" not in msg.lower()
    assert "403" in msg


def test_classify_api_error_403_tos_violation_drops_credits_redherring() -> None:
    """A 403 'violation of provider Terms Of Service' is a data-policy /
    routing block, not billing. The message must point at privacy settings
    and NOT tell the (credit-holding) user to add credits (issues #71, #183).
    """
    resp = MagicMock()
    resp.status_code = 403
    resp.json.return_value = {
        "error": {
            "message": "The request is prohibited due to a violation of provider Terms Of Service.",
            "code": 403,
        }
    }
    exc = RuntimeError("403 Forbidden")
    exc.response = resp  # type: ignore[attr-defined]

    msg = (_classify_api_error(exc) or "").lower()
    assert "terms" in msg
    assert "openrouter.ai/settings/privacy" in msg
    assert "add credits" not in msg and "no credits" not in msg


def test_classify_api_error_403_generic_body_keeps_credits_copy() -> None:
    """A 403 without the ToS body keeps the existing generic guidance
    (which mentions credits as one possible cause)."""
    resp = MagicMock()
    resp.status_code = 403
    resp.json.return_value = {"error": {"message": "Forbidden.", "code": 403}}
    exc = RuntimeError("403 Forbidden")
    exc.response = resp  # type: ignore[attr-defined]

    msg = (_classify_api_error(exc) or "").lower()
    assert "credits" in msg
    assert "openrouter.ai/credits" in msg


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
