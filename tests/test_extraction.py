"""Tests for coarse.extraction."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from coarse.extraction import (
    SUPPORTED_EXTENSIONS,
    _estimate_tokens,
    _response_was_billed,
    _scrub_secrets,
    _strip_nul_bytes,
    compute_garble_ratio,
    extract_file,
    extract_text,
    normalize_mistral_artifacts,
    normalize_ocr_garble,
)
from coarse.types import ExtractionError, PaperText


def _mock_ocr_response(pages_markdown: list[str]):
    """Create a mock OpenRouter file-parser response.

    The real response shape is:
    {"choices": [{"message": {"annotations": [{"type": "file",
      "file": {"content": [{"type": "text", "text": "..."}, ...]}}]}}]}

    Each "text" item represents one page. Returned as a MagicMock with
    status_code=200 and .json() returning the dict, so it can be used as
    the return value for patch("requests.post", ...).
    """
    content_items = [{"type": "text", "text": md} for md in pages_markdown]
    data = {
        "choices": [
            {
                "message": {
                    "annotations": [
                        {
                            "type": "file",
                            "file": {"content": content_items},
                        }
                    ],
                    "content": None,
                }
            }
        ]
    }
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = data
    resp.raise_for_status = MagicMock()
    return resp


@pytest.fixture
def mock_ocr_pages():
    """Sample OCR page markdowns."""
    return [
        "# Test Paper\n\n## Abstract\n\nThis is a test abstract.",
        "## Introduction\n\nHello, this is a test PDF for coarse extraction.",
    ]


@pytest.fixture
def minimal_pdf(tmp_path: Path) -> Path:
    """Create a minimal PDF file (just needs to exist for the mock)."""
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 minimal")
    return pdf_path


def test_extract_text_returns_paper_text(minimal_pdf: Path, mock_ocr_pages) -> None:
    with patch("requests.post", return_value=_mock_ocr_response(mock_ocr_pages)):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
            result = extract_text(minimal_pdf, use_cache=False)
    assert isinstance(result, PaperText)
    assert isinstance(result.full_markdown, str)
    assert len(result.full_markdown) > 0
    assert result.token_estimate > 0


def test_extract_text_contains_page_breaks(minimal_pdf: Path, mock_ocr_pages) -> None:
    with patch("requests.post", return_value=_mock_ocr_response(mock_ocr_pages)):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
            result = extract_text(minimal_pdf, use_cache=False)
    assert "<!-- PAGE BREAK -->" in result.full_markdown
    assert "# Test Paper" in result.full_markdown
    assert "Introduction" in result.full_markdown


def test_extract_text_joins_pages_with_page_break(minimal_pdf: Path) -> None:
    pages = ["Page 1 content", "Page 2 content", "Page 3 content"]
    with patch("requests.post", return_value=_mock_ocr_response(pages)):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
            result = extract_text(minimal_pdf, use_cache=False)
    assert result.full_markdown.count("<!-- PAGE BREAK -->") == 2


def test_extract_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        extract_text("/nonexistent/path/file.pdf")


# ---------------------------------------------------------------------------
# NUL byte scrubbing (#62) — Postgres text columns reject \x00, and
# PostgREST's JSON path rejects the 6-char escape \u0000 with SQLSTATE 22P05.
# ---------------------------------------------------------------------------


def test_strip_nul_bytes_removes_real_nul() -> None:
    assert _strip_nul_bytes("before\x00after") == "beforeafter"


def test_strip_nul_bytes_removes_literal_u0000_escape() -> None:
    assert _strip_nul_bytes("before\\u0000after") == "beforeafter"


def test_strip_nul_bytes_safe_on_empty() -> None:
    assert _strip_nul_bytes("") == ""


def test_strip_nul_bytes_leaves_normal_text_alone() -> None:
    text = "# Paper\n\nRegular content with math $x^2$ and newlines.\n"
    assert _strip_nul_bytes(text) == text


def test_extract_text_strips_nul_byte_from_ocr_output(minimal_pdf: Path) -> None:
    """If an OCR backend emits a NUL byte, extract_text must scrub it before
    handing the markdown to the caller. Without this guard, the downstream
    Supabase write crashes with Postgres 22P05 after the user has already
    paid for the whole review pipeline.
    """
    pages = ["Page 1 content with \x00 NUL byte in the middle."]
    with patch("requests.post", return_value=_mock_ocr_response(pages)):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
            result = extract_text(minimal_pdf, use_cache=False)
    assert "\x00" not in result.full_markdown
    assert "Page 1 content with" in result.full_markdown
    assert "NUL byte in the middle" in result.full_markdown


def test_extract_text_strips_literal_u0000_escape_from_ocr_output(
    minimal_pdf: Path,
) -> None:
    """Same defense for the 6-char literal \\u0000 sequence, which PostgREST
    rejects at the JSON-decode layer even though it isn't a real NUL byte
    until Postgres materializes it.
    """
    pages = ["Page with a literal \\u0000 escape in OCR output."]
    with patch("requests.post", return_value=_mock_ocr_response(pages)):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
            result = extract_text(minimal_pdf, use_cache=False)
    assert "\\u0000" not in result.full_markdown
    assert "literal" in result.full_markdown
    assert "escape in OCR output" in result.full_markdown


def test_token_estimate_heuristic() -> None:
    text = "a" * 400
    assert _estimate_tokens(text) == 100

    text2 = "hello world " * 10
    assert _estimate_tokens(text2) == len(text2) // 4


def test_extract_text_caching(minimal_pdf: Path, mock_ocr_pages) -> None:
    """Extraction result should be cached and reloaded on second call."""
    mock_fn = MagicMock(return_value=_mock_ocr_response(mock_ocr_pages))
    with patch("requests.post", mock_fn):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
            result1 = extract_text(minimal_pdf, use_cache=True)
            # Second call should use cache — ocr not called again
            result2 = extract_text(minimal_pdf, use_cache=True)

    assert result1.full_markdown == result2.full_markdown
    mock_fn.assert_called_once()


def test_extract_text_no_cache(minimal_pdf: Path, mock_ocr_pages) -> None:
    """With use_cache=False, OCR is always called."""
    mock_fn = MagicMock(return_value=_mock_ocr_response(mock_ocr_pages))
    with patch("requests.post", mock_fn):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
            extract_text(minimal_pdf, use_cache=False)
            extract_text(minimal_pdf, use_cache=False)

    assert mock_fn.call_count == 2


def test_fallback_to_docling(minimal_pdf: Path) -> None:
    """When OpenRouter OCR is unavailable, should fall back to Docling."""
    mock_doc = MagicMock()
    mock_doc.export_to_markdown.return_value = "# Docling Fallback\n\nContent here."
    mock_result = MagicMock()
    mock_result.document = mock_doc

    mock_converter_cls = MagicMock()
    mock_converter_cls.return_value.convert.return_value = mock_result

    # Mock at sys.modules level to avoid importing real docling (pulls in torch)
    mock_docling = MagicMock()
    mock_docling.document_converter.DocumentConverter = mock_converter_cls

    # Ensure no OpenRouter key (resolve_api_key) so the OpenRouter backend skips
    env_clean = {k: v for k, v in os.environ.items() if k not in ("OPENROUTER_API_KEY",)}
    with patch.dict(os.environ, env_clean, clear=True):
        with patch.dict(
            "sys.modules",
            {
                "docling": mock_docling,
                "docling.document_converter": mock_docling.document_converter,
            },
        ):
            result = extract_text(minimal_pdf, use_cache=False)

    assert "Docling Fallback" in result.full_markdown


def test_all_backends_fail(minimal_pdf: Path) -> None:
    """When all backends fail, raises ExtractionError with failure details."""
    from coarse.types import ExtractionError

    # Ensure no OpenRouter key (resolve_api_key) so OpenRouter backend skips
    env_clean = {k: v for k, v in os.environ.items() if k not in ("OPENROUTER_API_KEY",)}
    with patch.dict(os.environ, env_clean, clear=True):
        with patch.dict(
            "sys.modules",
            {"docling": None, "docling.document_converter": None},
        ):
            with pytest.raises(ExtractionError, match="all extraction backends failed"):
                extract_text(minimal_pdf, use_cache=False)


# --- OpenRouter OCR error handling and retry ---


def _mock_error_response(status: int, body: dict | str):
    """Build a mock requests.Response with a given status and JSON body."""
    resp = MagicMock()
    resp.status_code = status
    if isinstance(body, dict):
        resp.json.return_value = body
    else:
        resp.json.side_effect = ValueError(f"invalid json: {body}")
    if status >= 400:
        import requests as _r

        http_err = _r.HTTPError(f"{status} Error", response=resp)
        resp.raise_for_status.side_effect = http_err
    else:
        resp.raise_for_status = MagicMock()
    return resp


def test_openrouter_ocr_http_200_with_error_body(minimal_pdf: Path) -> None:
    """HTTP 200 with {'error': {...}} body should raise a clean ExtractionError,
    not KeyError: 'choices'. This is the exact failure mode we saw in production.

    The error message is intentionally one that doesn't match any keyword in
    _classify_api_error, so we can see our own ExtractionError text pass through.
    """
    error_response = _mock_error_response(
        200,
        {
            "error": {
                "message": "file-parser plugin temporarily unavailable",
                "code": "plugin_error",
            },
        },
    )
    with patch("requests.post", return_value=error_response):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
            with patch.dict(
                "sys.modules",
                {"docling": None, "docling.document_converter": None},
            ):
                with pytest.raises(ExtractionError) as exc_info:
                    extract_text(minimal_pdf, use_cache=False)
                # Must NOT be a KeyError: 'choices' — that was the production bug
                assert "choices" not in str(exc_info.value) or "no choices" in str(exc_info.value)
                assert "plugin" in str(exc_info.value) or "backends failed" in str(exc_info.value)


def test_openrouter_ocr_classifies_402_as_spend_limit(minimal_pdf: Path) -> None:
    """HTTP 200 with a credits-related error body should be classified into a
    user-friendly spend limit message by the extraction orchestrator."""
    error_response = _mock_error_response(
        200,
        {
            "error": {"message": "Insufficient credits", "code": 402},
        },
    )
    with patch("requests.post", return_value=error_response):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
            with patch.dict(
                "sys.modules",
                {"docling": None, "docling.document_converter": None},
            ):
                with pytest.raises(ExtractionError, match="spend limit"):
                    extract_text(minimal_pdf, use_cache=False)


def test_openrouter_ocr_no_choices_in_response(minimal_pdf: Path) -> None:
    """HTTP 200 with no 'choices' and no 'error' should raise with diagnostic info."""
    odd_response = _mock_error_response(200, {"something_else": "value"})
    with patch("requests.post", return_value=odd_response):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
            with patch.dict(
                "sys.modules",
                {"docling": None, "docling.document_converter": None},
            ):
                with pytest.raises(ExtractionError, match="no choices"):
                    extract_text(minimal_pdf, use_cache=False)


def test_openrouter_ocr_malformed_annotation_falls_back_to_content(
    minimal_pdf: Path,
) -> None:
    """Malformed annotations (e.g. missing 'file' key) should not crash;
    should fall back to message.content instead."""
    resp = _mock_error_response(
        200,
        {
            "choices": [
                {
                    "message": {
                        "annotations": [{"type": "file"}],  # missing 'file' key entirely
                        "content": "Fallback markdown text",
                    }
                }
            ]
        },
    )
    with patch("requests.post", return_value=resp):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
            result = extract_text(minimal_pdf, use_cache=False)
    assert "Fallback markdown text" in result.full_markdown


def test_openrouter_ocr_empty_content_raises(minimal_pdf: Path) -> None:
    """When both annotations and content are empty, raise ExtractionError."""
    empty_resp = _mock_error_response(
        200, {"choices": [{"message": {"annotations": [], "content": ""}}]}
    )
    with patch("requests.post", return_value=empty_resp):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
            with patch.dict(
                "sys.modules",
                {"docling": None, "docling.document_converter": None},
            ):
                with pytest.raises(ExtractionError, match="empty content"):
                    extract_text(minimal_pdf, use_cache=False)


def test_openrouter_ocr_retries_on_connection_error(
    minimal_pdf: Path,
    mock_ocr_pages,
) -> None:
    """Transient connection errors should be retried up to _OCR_MAX_RETRIES."""
    import requests as _r

    success = _mock_ocr_response(mock_ocr_pages)
    call_count = {"n": 0}

    def flaky_post(*args, **kwargs):
        call_count["n"] += 1
        if call_count["n"] < 3:
            raise _r.ConnectionError("simulated network blip")
        return success

    with patch("requests.post", side_effect=flaky_post):
        with patch("time.sleep"):  # don't actually wait in tests
            with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
                result = extract_text(minimal_pdf, use_cache=False)
    assert "# Test Paper" in result.full_markdown
    assert call_count["n"] == 3  # two failures + one success


def test_openrouter_ocr_gives_up_after_max_retries(minimal_pdf: Path) -> None:
    """Persistent connection errors should raise after the retry budget is spent."""
    import requests as _r

    def always_fails(*args, **kwargs):
        raise _r.ConnectionError("down")

    with patch("requests.post", side_effect=always_fails):
        with patch("time.sleep"):
            with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
                with patch.dict(
                    "sys.modules",
                    {"docling": None, "docling.document_converter": None},
                ):
                    with pytest.raises(ExtractionError, match="network error after"):
                        extract_text(minimal_pdf, use_cache=False)


def test_openrouter_ocr_honors_env_override_retries() -> None:
    """COARSE_OCR_MAX_RETRIES must cap the retry count at call time.

    Regression guard for the 2e17317 refactor, which hard-coded the
    ceiling against a module constant and silently ignored the env var.
    Any spinner-watching caller (e.g. a future handoff path) needs to be
    able to short-circuit the default 10-attempt/~160s budget, or Modal
    workers get tied up retrying flaky Mistral upstreams instead of
    falling through to the next extractor.
    """
    import requests as _r

    from coarse.extraction_openrouter import _post_openrouter_ocr

    call_count = {"n": 0}

    def always_fails(*args, **kwargs):
        call_count["n"] += 1
        raise _r.ConnectionError("down")

    with patch("requests.post", side_effect=always_fails):
        with patch("time.sleep"):
            with patch.dict(os.environ, {"COARSE_OCR_MAX_RETRIES": "2"}):
                with pytest.raises(ExtractionError, match="network error after 3"):
                    _post_openrouter_ocr(
                        url="https://example.invalid/api/v1/chat/completions",
                        headers={},
                        payload={},
                        timeout=1,
                    )
    # 2 retries + initial attempt = 3 total posts
    assert call_count["n"] == 3, f"env override should cap at 3 posts, got {call_count['n']}"


def test_openrouter_ocr_invalid_env_override_falls_back_to_default() -> None:
    """A malformed COARSE_OCR_MAX_RETRIES value must fall back to the default."""
    from coarse.extraction_openrouter import _OCR_MAX_RETRIES, _get_ocr_max_retries

    with patch.dict(os.environ, {"COARSE_OCR_MAX_RETRIES": "not-an-int"}):
        assert _get_ocr_max_retries() == _OCR_MAX_RETRIES
    with patch.dict(os.environ, {"COARSE_OCR_MAX_RETRIES": ""}):
        assert _get_ocr_max_retries() == _OCR_MAX_RETRIES
    with patch.dict(os.environ, {"COARSE_OCR_MAX_RETRIES": "-5"}):
        # Negative values clamp to 0, not the default — that's the only
        # safe way to let a caller ask for "no retries at all".
        assert _get_ocr_max_retries() == 0


def test_openrouter_ocr_retries_on_503(
    minimal_pdf: Path,
    mock_ocr_pages,
) -> None:
    """HTTP 503 should trigger a retry; subsequent success should be returned."""
    success = _mock_ocr_response(mock_ocr_pages)
    bad = _mock_error_response(503, {"error": "service unavailable"})
    # First call 503, second call succeeds
    with patch("requests.post", side_effect=[bad, success]):
        with patch("time.sleep"):
            with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
                result = extract_text(minimal_pdf, use_cache=False)
    assert "# Test Paper" in result.full_markdown


def test_openrouter_ocr_retries_on_200_with_body_error_504(
    minimal_pdf: Path,
    mock_ocr_pages,
) -> None:
    """The real production failure mode: HTTP 200 with {error: {code: 504,
    message: "Timed out parsing tmp.pdf"}}. Should be retried just like raw 504."""
    success = _mock_ocr_response(mock_ocr_pages)
    timeout_body = _mock_error_response(
        200,
        {
            "error": {"message": "Timed out parsing tmp.pdf", "code": 504},
        },
    )
    # First call returns the 200-with-504 body, second call succeeds
    with patch("requests.post", side_effect=[timeout_body, success]):
        with patch("time.sleep"):
            with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
                result = extract_text(minimal_pdf, use_cache=False)
    assert "# Test Paper" in result.full_markdown


def test_openrouter_ocr_retries_on_200_with_body_error_502(
    minimal_pdf: Path,
    mock_ocr_pages,
) -> None:
    """200 with {error: {code: 502}} is also a transient upstream error."""
    success = _mock_ocr_response(mock_ocr_pages)
    bad_gateway = _mock_error_response(
        200,
        {
            "error": {"message": "Upstream bad gateway", "code": 502},
        },
    )
    with patch("requests.post", side_effect=[bad_gateway, success]):
        with patch("time.sleep"):
            with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
                result = extract_text(minimal_pdf, use_cache=False)
    assert "# Test Paper" in result.full_markdown


def test_openrouter_ocr_does_not_retry_on_200_with_body_error_402(
    minimal_pdf: Path,
) -> None:
    """Non-retryable 402 body codes should not retry the same backend.

    We still allow the extractor chain to try the next backend, but each
    OpenRouter engine should only be attempted once for a hard billing error.
    """
    spend_limit = _mock_error_response(
        200,
        {
            "error": {"message": "Insufficient credits", "code": 402},
        },
    )
    post_mock = MagicMock(return_value=spend_limit)
    with patch("requests.post", post_mock):
        with patch("time.sleep"):
            with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
                with patch.dict(
                    "sys.modules",
                    {"docling": None, "docling.document_converter": None},
                ):
                    with pytest.raises(ExtractionError):
                        extract_text(minimal_pdf, use_cache=False)
    # Exactly one call per OpenRouter backend — no retries on 402.
    assert post_mock.call_count == 2


@pytest.mark.parametrize(
    ("status", "body"),
    [
        (
            402,
            {"error": {"message": "Insufficient credits", "code": 402}},
        ),
        (
            403,
            {
                "error": {
                    "message": "Provider blocked by privacy settings",
                    "code": "provider_forbidden",
                    "metadata": {"provider": "mistral"},
                }
            },
        ),
    ],
)
def test_openrouter_ocr_falls_back_after_mistral_api_denial(
    minimal_pdf: Path,
    mock_ocr_pages,
    caplog,
    status: int,
    body: dict,
) -> None:
    """402/403 on paid Mistral OCR should still try cheaper/offline fallback."""
    first = _mock_error_response(status, body)
    second = _mock_ocr_response(mock_ocr_pages)
    posted_engines: list[str] = []

    def spy_post(url, headers, json, timeout):  # noqa: A002
        plugins = json.get("plugins") or []
        engine = plugins[0].get("pdf", {}).get("engine") if plugins else None
        posted_engines.append(engine)
        return [first, second][len(posted_engines) - 1]

    with caplog.at_level(logging.WARNING):
        with patch("requests.post", side_effect=spy_post):
            with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
                result = extract_text(minimal_pdf, use_cache=False)

    assert "# Test Paper" in result.full_markdown
    assert posted_engines == ["mistral-ocr", "pdf-text"]
    assert "recoverable API denial" in caplog.text
    if status == 402:
        assert "Insufficient credits" in caplog.text
    else:
        assert "Provider blocked by privacy settings" in caplog.text
        assert "provider_forbidden" in caplog.text


def test_openrouter_ocr_retries_on_200_body_504_then_gives_up(
    minimal_pdf: Path,
) -> None:
    """Persistent 200-with-504-body should exhaust retries and raise.

    Both OpenRouter extractors (mistral-ocr and pdf-text) go through the
    same retry loop, so we expect 2 × (_OCR_MAX_RETRIES + 1) total posts
    before the chain falls through to (disabled) Docling and raises.
    """
    from coarse.extraction import _OCR_MAX_RETRIES

    timeout_body = _mock_error_response(
        200,
        {
            "error": {"message": "Timed out parsing", "code": 504},
        },
    )
    post_mock = MagicMock(return_value=timeout_body)
    with patch("requests.post", post_mock):
        with patch("time.sleep"):
            with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
                with patch.dict(
                    "sys.modules",
                    {"docling": None, "docling.document_converter": None},
                ):
                    with pytest.raises(ExtractionError, match="Timed out parsing"):
                        extract_text(minimal_pdf, use_cache=False)
    # Both mistral-ocr and pdf-text exhausted their retries.
    assert post_mock.call_count == 2 * (_OCR_MAX_RETRIES + 1)


def test_pdftext_fallback_runs_when_mistral_ocr_persistently_fails(
    minimal_pdf: Path,
    mock_ocr_pages,
) -> None:
    """When mistral-ocr exhausts retries with a transient body error, the
    extractor chain should fall through to the pdf-text engine before Docling."""
    from coarse.extraction import _OCR_MAX_RETRIES

    timeout_body = _mock_error_response(
        200,
        {
            "error": {"message": "Timed out parsing", "code": 504},
        },
    )
    pdftext_success = _mock_ocr_response(mock_ocr_pages)

    # Return timeout body for all mistral-ocr attempts, then success on the
    # single pdf-text attempt that follows.
    responses = [timeout_body] * (_OCR_MAX_RETRIES + 1) + [pdftext_success]
    posted_engines: list[str] = []

    def spy_post(url, headers, json, timeout):  # noqa: A002
        plugins = json.get("plugins") or []
        engine = plugins[0].get("pdf", {}).get("engine") if plugins else None
        posted_engines.append(engine)
        return responses[len(posted_engines) - 1]

    with patch("requests.post", side_effect=spy_post):
        with patch("time.sleep"):
            with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
                result = extract_text(minimal_pdf, use_cache=False)

    assert "# Test Paper" in result.full_markdown
    # First N calls are mistral-ocr retries, last call is pdf-text fallback.
    assert posted_engines[: _OCR_MAX_RETRIES + 1] == ["mistral-ocr"] * (_OCR_MAX_RETRIES + 1)
    assert posted_engines[-1] == "pdf-text"


def test_ocr_retry_stops_when_response_is_billed(minimal_pdf: Path) -> None:
    """A 200-with-error-body that ALSO reports non-zero usage must not be
    retried — retrying would double-charge the user for a billed error."""
    billed_timeout = _mock_error_response(
        200,
        {
            "error": {"message": "Timed out parsing", "code": 504},
            "usage": {"total_tokens": 123, "total_cost": 0.0042},
        },
    )
    mistral_post_count = {"n": 0}
    pdftext_post_count = {"n": 0}

    def spy_post(url, headers, json, timeout):  # noqa: A002
        plugins = json.get("plugins") or []
        engine = plugins[0].get("pdf", {}).get("engine") if plugins else None
        if engine == "mistral-ocr":
            mistral_post_count["n"] += 1
        elif engine == "pdf-text":
            pdftext_post_count["n"] += 1
        return billed_timeout

    with patch("requests.post", side_effect=spy_post):
        with patch("time.sleep"):
            with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
                with patch.dict(
                    "sys.modules",
                    {"docling": None, "docling.document_converter": None},
                ):
                    with pytest.raises(ExtractionError):
                        extract_text(minimal_pdf, use_cache=False)

    # Mistral OCR made exactly ONE billed call, then bailed out without retry.
    assert mistral_post_count["n"] == 1
    # pdf-text fallback is still tried — but the same billing guard applies
    # there too, so it also bails after one call.
    assert pdftext_post_count["n"] == 1


# --- _response_was_billed direct unit tests ---


def _billed_resp(body: object):
    """Tiny fake Response whose .json() returns body (or raises if callable)."""
    r = MagicMock()
    if callable(body):
        r.json.side_effect = body
    else:
        r.json.return_value = body
    return r


def test_response_was_billed_total_cost_positive():
    assert _response_was_billed(_billed_resp({"usage": {"total_cost": 0.0042}})) is True


def test_response_was_billed_cost_positive():
    assert _response_was_billed(_billed_resp({"usage": {"cost": 0.01}})) is True


def test_response_was_billed_total_tokens_positive():
    assert _response_was_billed(_billed_resp({"usage": {"total_tokens": 5}})) is True


def test_response_was_billed_all_zero():
    body = {"usage": {"total_cost": 0, "cost": 0.0, "total_tokens": 0}}
    assert _response_was_billed(_billed_resp(body)) is False


def test_response_was_billed_missing_usage_field():
    assert _response_was_billed(_billed_resp({"choices": []})) is False


def test_response_was_billed_usage_is_not_dict():
    assert _response_was_billed(_billed_resp({"usage": "free"})) is False
    assert _response_was_billed(_billed_resp({"usage": None})) is False
    assert _response_was_billed(_billed_resp({"usage": [1, 2, 3]})) is False


def test_response_was_billed_json_raises():
    def raise_value_error():
        raise ValueError("not json")

    assert _response_was_billed(_billed_resp(raise_value_error)) is False


def test_response_was_billed_response_is_not_dict():
    assert _response_was_billed(_billed_resp("literal string")) is False
    assert _response_was_billed(_billed_resp([1, 2, 3])) is False


def test_response_was_billed_rejects_bool_total_cost():
    """bool is a subclass of int in Python — the guard must not be fooled
    by a malformed `usage: {"total_cost": true}` response, since True would
    coerce to >0 and kill retries on a free error body."""
    body = {"usage": {"total_cost": True, "total_tokens": 0}}
    assert _response_was_billed(_billed_resp(body)) is False


def test_response_was_billed_rejects_bool_tokens():
    body = {"usage": {"total_tokens": True}}
    assert _response_was_billed(_billed_resp(body)) is False


def test_response_was_billed_accepts_float_total_cost():
    """Real OpenRouter responses report costs as floats; verify we handle them."""
    body = {"usage": {"total_cost": 0.000001, "total_tokens": 0}}
    assert _response_was_billed(_billed_resp(body)) is True


# --- Backoff cap and fallback-order tests ---


def test_ocr_backoff_waits_are_capped_at_max_backoff(minimal_pdf: Path) -> None:
    """Verify _OCR_MAX_BACKOFF actually caps per-retry waits. Without this
    test, someone could delete the `min(..., _OCR_MAX_BACKOFF)` in
    _post_openrouter_ocr and every other test would still pass because
    they all patch time.sleep to a no-op."""
    from coarse.extraction import _OCR_MAX_BACKOFF, _OCR_MAX_RETRIES

    timeout_body = _mock_error_response(
        200,
        {
            "error": {"message": "Timed out parsing", "code": 504},
        },
    )
    sleep_args: list[float] = []

    def fake_sleep(seconds):
        sleep_args.append(seconds)

    with patch("requests.post", return_value=timeout_body):
        with patch("time.sleep", side_effect=fake_sleep):
            with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
                with patch.dict(
                    "sys.modules",
                    {"docling": None, "docling.document_converter": None},
                ):
                    with pytest.raises(ExtractionError):
                        extract_text(minimal_pdf, use_cache=False)

    # Each engine (mistral-ocr, pdf-text) runs _OCR_MAX_RETRIES sleeps.
    # Per-engine sequence: 1, 2, 4, 8, 16, 32, 32, 32, 32 (exponential then capped).
    per_engine = sleep_args[:_OCR_MAX_RETRIES]
    assert per_engine[:5] == [1.0, 2.0, 4.0, 8.0, 16.0]
    assert all(w == _OCR_MAX_BACKOFF for w in per_engine[5:]), (
        f"backoff not capped: tail is {per_engine[5:]}"
    )
    # Same pattern repeats for the pdf-text tier.
    assert sleep_args[_OCR_MAX_RETRIES : 2 * _OCR_MAX_RETRIES] == per_engine


def test_pdftext_is_not_called_when_mistral_ocr_succeeds(
    minimal_pdf: Path,
    mock_ocr_pages,
) -> None:
    """pdf-text is strictly a fallback — when mistral-ocr succeeds on the
    first try, pdf-text must not be hit at all."""
    success = _mock_ocr_response(mock_ocr_pages)
    posted_engines: list[str] = []

    def spy_post(url, headers, json, timeout):  # noqa: A002
        plugins = json.get("plugins") or []
        engine = plugins[0].get("pdf", {}).get("engine") if plugins else None
        posted_engines.append(engine)
        return success

    with patch("requests.post", side_effect=spy_post):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
            result = extract_text(minimal_pdf, use_cache=False)

    assert "# Test Paper" in result.full_markdown
    assert posted_engines == ["mistral-ocr"]


def test_openrouter_ocr_does_not_retry_on_401(minimal_pdf: Path) -> None:
    """4xx errors (except 408/429) are not transient — don't waste retries on them."""
    bad = _mock_error_response(401, {"error": "Invalid API key"})
    post_mock = MagicMock(return_value=bad)
    with patch("requests.post", post_mock):
        with patch("time.sleep"):
            with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
                with patch.dict(
                    "sys.modules",
                    {"docling": None, "docling.document_converter": None},
                ):
                    # 401 propagates through _classify_api_error → ExtractionError
                    with pytest.raises(ExtractionError):
                        extract_text(minimal_pdf, use_cache=False)
    # Exactly one call — no retry on 401
    assert post_mock.call_count == 1


# --- Garble detection and normalization ---


def test_compute_garble_ratio_clean_text():
    """Clean text should have zero garble ratio."""
    assert compute_garble_ratio("This is clean text with LaTeX $x^2$.") == 0.0


def test_compute_garble_ratio_garbled_text():
    """Text with OCR artifacts should have nonzero garble ratio."""
    garbled = "The ®nite case shows /C40x/C41 is naõÈve"
    ratio = compute_garble_ratio(garbled)
    assert ratio > 0.0


def test_compute_garble_ratio_empty():
    assert compute_garble_ratio("") == 0.0


def test_normalize_ocr_garble_fixes_known_patterns():
    """Known garble patterns should be fixed by normalization."""
    garbled = "The ®nite integral over /C40a, b/C41 is naõÈve"
    result = normalize_ocr_garble(garbled)
    assert "finite" in result
    assert "(" in result
    assert ")" in result
    assert "naïve" in result
    assert "®nite" not in result
    assert "/C40" not in result


def test_normalize_ocr_garble_preserves_clean_text():
    """Clean text should not be altered by normalization."""
    clean = "The finite integral over (a, b) is well-defined."
    assert normalize_ocr_garble(clean) == clean


def test_extract_text_sets_garble_ratio(minimal_pdf: Path, mock_ocr_pages) -> None:
    """Extraction should compute and store garble ratio."""
    with patch("requests.post", return_value=_mock_ocr_response(mock_ocr_pages)):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
            result = extract_text(minimal_pdf, use_cache=False)
    assert hasattr(result, "garble_ratio")
    assert result.garble_ratio == 0.0  # clean mock data


def test_extract_text_normalizes_garbled_ocr(minimal_pdf: Path) -> None:
    """Garbled OCR output should be auto-normalized."""
    garbled_pages = ["The ®nite case shows /C40x/C41"]
    with patch("requests.post", return_value=_mock_ocr_response(garbled_pages)):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
            result = extract_text(minimal_pdf, use_cache=False)
    assert "finite" in result.full_markdown
    assert "®nite" not in result.full_markdown


# --- Mistral artifact normalization ---


def test_normalize_mistral_glyph_mapping():
    """Known glyph[...] patterns should be replaced with Unicode."""
    text = "Let glyph[lscript] be a loss, glyph[epsilon1] > 0, glyph[element] S"
    result = normalize_mistral_artifacts(text)
    assert "ℓ" in result
    assert "ε" in result
    assert "∈" in result
    assert "glyph[" not in result


def test_normalize_mistral_unknown_glyph_preserved():
    """Unknown glyph names should be left as-is."""
    text = "glyph[unknownsymbol] stays"
    result = normalize_mistral_artifacts(text)
    assert "glyph[unknownsymbol]" in result


def test_normalize_mistral_lscript():
    """/lscript should become ℓ."""
    assert normalize_mistral_artifacts("the /lscript norm") == "the ℓ norm"


def test_normalize_mistral_html_entities():
    """HTML entities should be unescaped."""
    text = "x &gt; 0 and y &lt; 1 and &amp; done"
    result = normalize_mistral_artifacts(text)
    assert "x > 0" in result
    assert "y < 1" in result
    assert "& done" in result


def test_normalize_mistral_formula_not_decoded():
    """<!-- formula-not-decoded --> markers should be removed."""
    text = "see equation <!-- formula-not-decoded --> above"
    result = normalize_mistral_artifacts(text)
    assert "formula-not-decoded" not in result
    assert "see equation  above" in result


def test_normalize_mistral_clean_text_preserved():
    """Clean text should not be altered."""
    clean = "The finite integral over (a, b) is well-defined."
    assert normalize_mistral_artifacts(clean) == clean


def test_garble_ratio_detects_mistral_artifacts():
    """Garble ratio should detect glyph[...] and /lscript patterns."""
    text = "Let glyph[lscript] be /lscript norm"
    ratio = compute_garble_ratio(text)
    assert ratio > 0.0


def test_extract_text_normalizes_mistral_artifacts(minimal_pdf: Path) -> None:
    """Mistral OCR artifacts should be normalized during extraction."""
    pages = ["Let glyph[lscript] &gt; 0 with <!-- formula-not-decoded --> here"]
    with patch("requests.post", return_value=_mock_ocr_response(pages)):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
            result = extract_text(minimal_pdf, use_cache=False)
    assert "ℓ" in result.full_markdown
    assert "> 0" in result.full_markdown
    assert "glyph[" not in result.full_markdown
    assert "formula-not-decoded" not in result.full_markdown


# ---------------------------------------------------------------------------
# Multi-format extraction tests (extract_file)
# ---------------------------------------------------------------------------


def test_extract_file_txt(tmp_path: Path) -> None:
    """Plain text files are read as-is with garble_ratio=0.0."""
    txt = tmp_path / "paper.txt"
    txt.write_text("This is a plain text paper.\nWith multiple lines.", encoding="utf-8")
    result = extract_file(txt, use_cache=False)
    assert isinstance(result, PaperText)
    assert "plain text paper" in result.full_markdown
    assert result.garble_ratio == 0.0
    assert result.token_estimate > 0


def test_extract_file_md(tmp_path: Path) -> None:
    """Markdown files preserve headings."""
    md = tmp_path / "paper.md"
    md.write_text(
        "# Introduction\n\nSome content.\n\n## Methods\n\nMore content.", encoding="utf-8"
    )
    result = extract_file(md, use_cache=False)
    assert "# Introduction" in result.full_markdown
    assert "## Methods" in result.full_markdown
    assert result.garble_ratio == 0.0


def test_extract_file_tex(tmp_path: Path) -> None:
    """LaTeX files have headings converted to markdown."""
    tex = tmp_path / "paper.tex"
    tex.write_text(
        "\\documentclass{article}\n"
        "\\usepackage{amsmath}\n"
        "\\begin{document}\n"
        "\\section{Introduction}\n"
        "This paper studies $x^2$.\n"
        "\\subsection{Background}\n"
        "Some background.\n"
        "\\end{document}\n",
        encoding="utf-8",
    )
    result = extract_file(tex, use_cache=False)
    assert "# Introduction" in result.full_markdown
    assert "## Background" in result.full_markdown
    assert "$x^2$" in result.full_markdown
    assert "\\documentclass" not in result.full_markdown
    assert result.garble_ratio == 0.0


def test_extract_file_unsupported(tmp_path: Path) -> None:
    """Unsupported extensions raise ExtractionError."""
    bad = tmp_path / "paper.xyz"
    bad.write_text("content", encoding="utf-8")
    with pytest.raises(ExtractionError, match="Unsupported file format"):
        extract_file(bad, use_cache=False)


def test_extract_file_missing() -> None:
    """Missing files raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        extract_file("/nonexistent/paper.txt")


def test_extract_file_pdf_delegates(minimal_pdf: Path, mock_ocr_pages) -> None:
    """PDF files delegate to extract_text."""
    with patch("requests.post", return_value=_mock_ocr_response(mock_ocr_pages)):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-v1-test"}):
            result = extract_file(minimal_pdf, use_cache=False)
    assert isinstance(result, PaperText)
    assert "# Test Paper" in result.full_markdown


def test_extract_file_caching(tmp_path: Path) -> None:
    """Non-PDF files are cached after first extraction."""
    txt = tmp_path / "paper.txt"
    txt.write_text("Cached content.", encoding="utf-8")
    r1 = extract_file(txt, use_cache=True)
    # Modify file content — but cache should still be used (same mtime check)
    r2 = extract_file(txt, use_cache=True)
    assert r1.full_markdown == r2.full_markdown


def test_extract_latex_heading_conversion() -> None:
    """All LaTeX heading levels are correctly converted."""
    # Test the regex directly

    from coarse.extraction import _LATEX_HEADING_LEVEL, _LATEX_HEADING_RE

    test_cases = [
        ("\\section{Intro}", "# Intro"),
        ("\\subsection{Methods}", "## Methods"),
        ("\\subsubsection{Details}", "### Details"),
        ("\\paragraph{Note}", "#### Note"),
        ("\\section*{Starred}", "# Starred"),
    ]
    for latex, expected_md in test_cases:
        converted = _LATEX_HEADING_RE.sub(
            lambda m: f"{_LATEX_HEADING_LEVEL[m.group(1)]} {m.group(2)}", latex
        )
        assert converted == expected_md, f"{latex} → {converted}, expected {expected_md}"


def test_extract_latex_preserves_math(tmp_path: Path) -> None:
    """Math content survives LaTeX extraction (may be converted to $$ format by Docling)."""
    tex = tmp_path / "math.tex"
    tex.write_text(
        "\\begin{document}\n"
        "\\section{Theory}\n"
        "Consider $x^2 + y^2 = z^2$ and\n"
        "\\begin{equation}\n"
        "  E = mc^2\n"
        "\\end{equation}\n"
        "\\end{document}\n",
        encoding="utf-8",
    )
    result = extract_file(tex, use_cache=False)
    # Inline math preserved
    assert "x^2" in result.full_markdown
    # Display math preserved (either as \begin{equation} or $$ depending on backend)
    assert "E = mc^2" in result.full_markdown


def test_extract_latex_strips_preamble(tmp_path: Path) -> None:
    """LaTeX preamble noise is stripped."""
    tex = tmp_path / "preamble.tex"
    tex.write_text(
        "\\documentclass{article}\n"
        "\\usepackage{amsmath}\n"
        "\\usepackage[utf8]{inputenc}\n"
        "\\title{My Paper}\n"
        "\\author{Author}\n"
        "\\date{2026}\n"
        "\\begin{document}\n"
        "\\maketitle\n"
        "\\section{Intro}\n"
        "Content here.\n"
        "\\end{document}\n",
        encoding="utf-8",
    )
    result = extract_file(tex, use_cache=False)
    assert "\\documentclass" not in result.full_markdown
    assert "\\usepackage" not in result.full_markdown
    assert "\\title" not in result.full_markdown
    assert "\\maketitle" not in result.full_markdown
    assert "# Intro" in result.full_markdown
    assert "Content here." in result.full_markdown


def test_supported_extensions_includes_all_formats() -> None:
    """SUPPORTED_EXTENSIONS includes all documented formats."""
    for ext in [".pdf", ".txt", ".md", ".tex", ".latex", ".html", ".htm", ".docx", ".epub"]:
        assert ext in SUPPORTED_EXTENSIONS


# ---------------------------------------------------------------------------
# Secret scrubbing on the error path (issue #41)
# ---------------------------------------------------------------------------


def test_scrub_secrets_strips_bearer_and_keys() -> None:
    """_scrub_secrets redacts bearer headers and provider API keys."""
    # Fake fixture strings only — constructed so each line stays under the
    # line-length limit and gets its own security scanner suppression.
    openrouter = "sk-or-v1-abcdef0123456789abcdef0123456789"  # security: ignore
    anthropic = "sk-ant-abcdef0123456789abcdef"  # security: ignore
    groq = "gsk_abcdefghijklmnopqrst"  # security: ignore
    perplexity = "pplx-abcdefghijklmnopqrst"  # security: ignore
    google = "AIzaSyAbcdefghijklmnopqrstuvwxyz0123456"  # security: ignore
    jwt = "eyJabcdefghijklmnopqrst"  # security: ignore
    raw = (
        f"401 Authorization: Bearer {openrouter} | "
        f"also saw {anthropic} and {groq} "
        f"and {perplexity} and {google} "
        f"and {jwt}"
    )
    scrubbed = _scrub_secrets(raw)
    assert "sk-or-v1-abcdef" not in scrubbed
    assert "sk-ant-abcdef" not in scrubbed
    assert "gsk_abcdef" not in scrubbed
    assert "pplx-abcdef" not in scrubbed
    assert "AIzaSy" not in scrubbed
    assert "eyJabcdef" not in scrubbed
    assert "Bearer sk-or-v1" not in scrubbed
    assert "[key]" in scrubbed


def test_extraction_error_message_is_scrubbed(tmp_path: Path, caplog) -> None:
    """All-backends-failed path scrubs secrets from both the raised exception
    AND the logger.warning side-effect. Without the caplog assertion, a
    refactor that scrubs only at raise time could regress the log path."""
    import logging

    pdf = tmp_path / "paper.pdf"
    # Minimal valid PDF magic so extract_text() proceeds past header check.
    pdf.write_bytes(b"%PDF-1.4\n%fake content\n")

    secret_bearer = "Bearer sk-or-v1-abcdef0123456789abcdef0123456789"  # security: ignore

    def _boom(_path):
        raise RuntimeError(f"upstream 401 with header {secret_bearer}")

    # Force every backend to fail with the same leaky exception. Patching
    # _classify_api_error to return None keeps the error path in the
    # fall-through branch (not the immediate user-actionable raise).
    with (
        caplog.at_level(logging.WARNING, logger="coarse.extraction"),
        patch("coarse.extraction._extract_mistral_openrouter", side_effect=_boom),
        patch("coarse.extraction._extract_pdftext_openrouter", side_effect=_boom),
        patch("coarse.extraction._extract_docling", side_effect=_boom),
        patch("coarse.extraction._classify_api_error", return_value=None),
    ):
        with pytest.raises(ExtractionError) as exc_info:
            extract_text(pdf, use_cache=False)

    raised = str(exc_info.value)
    assert "sk-or-v1-abcdef" not in raised
    assert secret_bearer not in raised
    assert "[key]" in raised

    # Logger.warning path must also be scrubbed — the raised ExtractionError
    # is one channel, the WARNING log is another, and a regression that only
    # hardens one of them must fail.
    log_text = caplog.text
    assert "sk-or-v1-abcdef" not in log_text
    assert secret_bearer not in log_text
    assert "[key]" in log_text
