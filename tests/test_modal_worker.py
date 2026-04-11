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


# ---------------------------------------------------------------------------
# _fetch_and_consume_user_key — issue #49 (review_secrets ferry)
# ---------------------------------------------------------------------------


class _FakeSupabaseQuery:
    """Minimal chainable stub that mimics supabase-py's query builder."""

    def __init__(self, table_stub: "_FakeSupabaseTable", op: str) -> None:
        self._table = table_stub
        self._op = op
        self._filter: tuple[str, str] | None = None

    def select(self, _columns: str) -> "_FakeSupabaseQuery":
        return self

    def eq(self, column: str, value: str) -> "_FakeSupabaseQuery":
        self._filter = (column, value)
        return self

    def maybe_single(self) -> "_FakeSupabaseQuery":
        return self

    def execute(self) -> types.SimpleNamespace:
        if self._table.raise_on == self._op:
            raise RuntimeError(f"fake supabase {self._op} failure")
        if self._op == "select":
            return types.SimpleNamespace(data=self._table.row)
        if self._op == "delete":
            self._table.deleted.append(self._filter)
            return types.SimpleNamespace(data=None)
        raise AssertionError(f"unknown op {self._op}")


class _FakeSupabaseTable:
    def __init__(self, row: dict | None = None, raise_on: str | None = None) -> None:
        self.row = row
        self.raise_on = raise_on
        self.deleted: list[tuple[str, str] | None] = []

    def select(self, columns: str) -> _FakeSupabaseQuery:
        return _FakeSupabaseQuery(self, "select").select(columns)

    def delete(self) -> _FakeSupabaseQuery:
        return _FakeSupabaseQuery(self, "delete")


class _FakeSupabase:
    def __init__(self, table_stub: _FakeSupabaseTable) -> None:
        self._table_stub = table_stub
        self.table_names: list[str] = []

    def table(self, name: str) -> _FakeSupabaseTable:
        self.table_names.append(name)
        return self._table_stub


def test_fetch_and_consume_user_key_returns_key_and_deletes_row(modal_worker) -> None:
    """Happy path: SELECT returns a row, DELETE runs, key is returned."""
    table = _FakeSupabaseTable(
        row={"user_api_key": "sk-or-v1-fakefakefakefakefakefakefake"}  # security: ignore
    )
    db = _FakeSupabase(table)

    key = modal_worker._fetch_and_consume_user_key(db, "job-1")
    assert key == "sk-or-v1-fakefakefakefakefakefakefake"  # security: ignore
    assert db.table_names == ["review_secrets", "review_secrets"]
    # Delete was called with the matching filter
    assert table.deleted == [("review_id", "job-1")]


def test_fetch_and_consume_user_key_returns_none_when_row_missing(modal_worker) -> None:
    """No row → return None → caller falls back to req.user_api_key."""
    table = _FakeSupabaseTable(row=None)
    db = _FakeSupabase(table)

    key = modal_worker._fetch_and_consume_user_key(db, "job-missing")
    assert key is None
    # Delete should NOT run when there was nothing to read
    assert table.deleted == []


def test_fetch_and_consume_user_key_returns_none_on_select_error(modal_worker) -> None:
    """SELECT failure is swallowed; caller still falls back to backward-compat."""
    table = _FakeSupabaseTable(row=None, raise_on="select")
    db = _FakeSupabase(table)

    key = modal_worker._fetch_and_consume_user_key(db, "job-boom")
    assert key is None
    assert table.deleted == []


def test_fetch_and_consume_user_key_tolerates_delete_failure(modal_worker) -> None:
    """DELETE failure is non-fatal — the key is still returned for the pipeline.
    The TTL cleanup cron sweeps the orphaned row."""
    table = _FakeSupabaseTable(
        row={"user_api_key": "sk-or-v1-abcdefghijklmnopqrstuvwx"},  # security: ignore
        raise_on="delete",
    )
    db = _FakeSupabase(table)

    key = modal_worker._fetch_and_consume_user_key(db, "job-retry-ok")
    # Key is returned despite the delete failing
    assert key == "sk-or-v1-abcdefghijklmnopqrstuvwx"  # security: ignore


def test_fetch_and_consume_does_not_leak_key_into_log_on_delete_failure(
    modal_worker, capsys
) -> None:
    """A delete failure is logged, but the logged string must never contain the key."""
    secret = "sk-or-v1-supersecretkey1234567890abcdef"  # security: ignore
    table = _FakeSupabaseTable(
        row={"user_api_key": secret},
        raise_on="delete",
    )
    db = _FakeSupabase(table)

    modal_worker._fetch_and_consume_user_key(db, "job-log-test")
    captured = capsys.readouterr()
    # The fake exception message does not contain the key, so this is a
    # regression guard: if a future refactor leaks req/response bodies into
    # the exception, the sanitizer must still catch them.
    assert secret not in captured.out
    assert secret not in captured.err
