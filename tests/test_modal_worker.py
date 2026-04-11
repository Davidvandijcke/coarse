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


def test_sanitize_error_scrubs_groq_key(modal_worker) -> None:
    """Groq keys (gsk_...) must be redacted."""
    raw = "Groq 401: invalid key gsk_abcdefghijklmnopqrstuvwxyz0123"
    cleaned = modal_worker._sanitize_error(raw)
    assert "gsk_abcdef" not in cleaned
    assert "[key]" in cleaned or "[redacted]" in cleaned


def test_sanitize_error_scrubs_perplexity_key(modal_worker) -> None:
    """Perplexity keys (pplx-...) must be redacted."""
    raw = "Perplexity 401: pplx-abcdefghijklmnopqrstuvwxyz"
    cleaned = modal_worker._sanitize_error(raw)
    assert "pplx-abcdef" not in cleaned
    assert "[key]" in cleaned or "[redacted]" in cleaned


def test_sanitize_error_scrubs_anthropic_key(modal_worker) -> None:
    """Anthropic keys (sk-ant-...) must be redacted explicitly."""
    raw = "Anthropic 401: sk-ant-abcdefghijklmnopqrstuvwxyz0123"  # security: ignore
    cleaned = modal_worker._sanitize_error(raw)
    assert "sk-ant-abcdef" not in cleaned
    assert "[key]" in cleaned or "[redacted]" in cleaned


def test_run_review_uses_constant_time_compare(modal_worker) -> None:
    """run_review must route token comparison through hmac.compare_digest."""
    import hmac as _hmac

    # Module-level `hmac` import is present.
    assert getattr(modal_worker, "hmac", None) is _hmac
    # And the run_review source references compare_digest directly.
    import inspect

    src = inspect.getsource(modal_worker.run_review)
    assert "hmac.compare_digest" in src
