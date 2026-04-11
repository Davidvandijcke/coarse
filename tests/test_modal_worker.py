"""Tests for deploy/modal_worker.py — issue #41 hardening.

deploy/modal_worker.py is not a package; it imports `modal` and
`fastapi` at module load. Neither is a test dependency of coarse, so we
stub them in sys.modules before loading the file with importlib.

We only test the pure helpers (_sanitize_error) and assert that
hmac.compare_digest is wired into run_review at module level — a
mock-based test of run_review itself would require a full FastAPI
request object and is out of scope.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
_MODAL_WORKER = _REPO_ROOT / "deploy" / "modal_worker.py"


def _install_stubs() -> None:
    """Install minimal stand-ins for `modal` and `fastapi` in sys.modules."""
    if "modal" not in sys.modules:
        modal_stub = types.ModuleType("modal")

        class _App:
            def __init__(self, *_a, **_kw):
                pass

            def function(self, *_a, **_kw):
                def _decorator(fn):
                    return fn

                return _decorator

        class _Image:
            @staticmethod
            def debian_slim(*_a, **_kw):
                return _Image()

            def apt_install(self, *_a, **_kw):
                return self

            def pip_install(self, *_a, **_kw):
                return self

            def add_local_dir(self, *_a, **_kw):
                return self

        class _Secret:
            @staticmethod
            def from_name(_name):
                return object()

        modal_stub.App = _App
        modal_stub.Image = _Image
        modal_stub.Secret = _Secret

        def _fastapi_endpoint(*_a, **_kw):
            def _decorator(fn):
                return fn

            return _decorator

        modal_stub.fastapi_endpoint = _fastapi_endpoint
        sys.modules["modal"] = modal_stub

    if "fastapi" not in sys.modules:
        fastapi_stub = types.ModuleType("fastapi")

        class _HTTPException(Exception):
            def __init__(self, status_code: int, detail: str = "") -> None:
                super().__init__(detail)
                self.status_code = status_code
                self.detail = detail

        class _Request:  # noqa: D401
            pass

        fastapi_stub.HTTPException = _HTTPException
        fastapi_stub.Request = _Request
        sys.modules["fastapi"] = fastapi_stub


def _load_modal_worker():
    _install_stubs()
    spec = importlib.util.spec_from_file_location("coarse_deploy_modal_worker", _MODAL_WORKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def modal_worker():
    return _load_modal_worker()


def test_sanitize_error_scrubs_openrouter_key(modal_worker) -> None:
    """OpenRouter keys (sk-or-v1-...) must be redacted (regression guard)."""
    raw = "OpenRouter 401: invalid sk-or-v1-abcdefghijklmnopqrstuvwxyz0123"  # security: ignore
    cleaned = modal_worker._sanitize_error(raw)
    assert "sk-or-v1-abcdef" not in cleaned
    assert "[key]" in cleaned
    assert "OpenRouter 401" in cleaned  # non-secret context preserved


def test_sanitize_error_scrubs_groq_key(modal_worker) -> None:
    """Groq keys (gsk_...) must be redacted."""
    raw = "Groq 401: invalid key gsk_abcdefghijklmnopqrstuvwxyz0123"  # security: ignore
    cleaned = modal_worker._sanitize_error(raw)
    assert "gsk_abcdef" not in cleaned
    assert "[key]" in cleaned
    assert "Groq 401" in cleaned


def test_sanitize_error_scrubs_perplexity_key(modal_worker) -> None:
    """Perplexity keys (pplx-...) must be redacted."""
    raw = "Perplexity 401: pplx-abcdefghijklmnopqrstuvwxyz"  # security: ignore
    cleaned = modal_worker._sanitize_error(raw)
    assert "pplx-abcdef" not in cleaned
    assert "[key]" in cleaned
    assert "Perplexity 401" in cleaned


def test_sanitize_error_scrubs_anthropic_key(modal_worker) -> None:
    """Anthropic keys (sk-ant-...) must be redacted explicitly (before generic sk-)."""
    raw = "Anthropic 401: sk-ant-abcdefghijklmnopqrstuvwxyz0123"  # security: ignore
    cleaned = modal_worker._sanitize_error(raw)
    # The WHOLE match must be replaced — not left with a dangling `ant-...` tail.
    assert "sk-ant-" not in cleaned
    assert "ant-abcdef" not in cleaned
    assert "[key]" in cleaned
    assert "Anthropic 401" in cleaned


def _make_req(job_id: str = "j1"):
    return types.SimpleNamespace(job_id=job_id, model_dump=lambda: {"job_id": job_id})


def _make_request(auth_header: str | None):
    headers: dict[str, str] = {}
    if auth_header is not None:
        headers["Authorization"] = auth_header
    return types.SimpleNamespace(headers=headers)


def _fake_hmac(return_value: bool):
    from unittest.mock import MagicMock

    mock = MagicMock(return_value=return_value)
    return types.SimpleNamespace(compare_digest=mock), mock


def test_run_review_rejects_empty_secret(modal_worker, monkeypatch) -> None:
    """Empty MODAL_WEBHOOK_SECRET must reject without calling compare_digest."""
    from fastapi import HTTPException

    monkeypatch.setenv("MODAL_WEBHOOK_SECRET", "")
    fake, compare_mock = _fake_hmac(return_value=True)
    monkeypatch.setattr(modal_worker, "hmac", fake)

    with pytest.raises(HTTPException) as exc:
        modal_worker.run_review(_make_request("Bearer anything"), _make_req())
    assert exc.value.status_code == 401
    compare_mock.assert_not_called()


def test_run_review_rejects_empty_token(modal_worker, monkeypatch) -> None:
    """Empty/missing Authorization header must reject without calling compare_digest."""
    from fastapi import HTTPException

    monkeypatch.setenv("MODAL_WEBHOOK_SECRET", "realsecret")
    fake, compare_mock = _fake_hmac(return_value=True)
    monkeypatch.setattr(modal_worker, "hmac", fake)

    with pytest.raises(HTTPException) as exc:
        modal_worker.run_review(_make_request(None), _make_req())
    assert exc.value.status_code == 401
    compare_mock.assert_not_called()


def test_run_review_rejects_wrong_token(modal_worker, monkeypatch) -> None:
    """Non-matching token must reject via hmac.compare_digest returning False."""
    from fastapi import HTTPException

    monkeypatch.setenv("MODAL_WEBHOOK_SECRET", "realsecret")
    fake, compare_mock = _fake_hmac(return_value=False)
    monkeypatch.setattr(modal_worker, "hmac", fake)

    with pytest.raises(HTTPException) as exc:
        modal_worker.run_review(_make_request("Bearer wrongtoken"), _make_req())
    assert exc.value.status_code == 401
    compare_mock.assert_called_once_with("wrongtoken", "realsecret")


def test_run_review_accepts_valid_token(modal_worker, monkeypatch) -> None:
    """Matching token routes through hmac.compare_digest and spawns the worker."""
    from unittest.mock import MagicMock

    monkeypatch.setenv("MODAL_WEBHOOK_SECRET", "realsecret")
    fake, compare_mock = _fake_hmac(return_value=True)
    monkeypatch.setattr(modal_worker, "hmac", fake)

    spawn_mock = MagicMock()
    monkeypatch.setattr(modal_worker, "do_review", types.SimpleNamespace(spawn=spawn_mock))

    result = modal_worker.run_review(_make_request("Bearer realsecret"), _make_req("j42"))
    assert result == {"status": "accepted", "job_id": "j42"}
    compare_mock.assert_called_once_with("realsecret", "realsecret")
    spawn_mock.assert_called_once_with({"job_id": "j42"})
