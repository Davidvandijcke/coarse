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


# ---------------------------------------------------------------------------
# _sanitize_error — instructor retry envelope (#55)
# ---------------------------------------------------------------------------


def test_sanitize_error_extracts_instructor_exception_block(modal_worker) -> None:
    """Instructor wraps retry failures in <last_exception><failed_attempts>...
    The old last-non-empty-line heuristic picked up the bare closing tag, so
    every instructor retry failure was stored in Supabase as the single
    string '</last_exception>'. The fix extracts the first <exception>
    payload instead.
    """
    raw = (
        "<last_exception>\n"
        "<failed_attempts>\n"
        '<generation number="1">\n'
        "<exception>\n"
        "    The output is incomplete due to a max_tokens length limit.\n"
        "</exception>\n"
        "<completion>\n"
        "    ModelResponse(id='gen-xxx', finish_reason='length', ...)\n"
        "</completion>\n"
        "</generation>\n"
        "</failed_attempts>\n"
        "</last_exception>"
    )
    cleaned = modal_worker._sanitize_error(raw)
    assert "max_tokens" in cleaned
    assert "incomplete" in cleaned
    # The outer closing tag must NOT be what we kept
    assert cleaned.strip() != "</last_exception>"
    assert not cleaned.startswith("</")


def test_sanitize_error_closing_tag_only_fallback(modal_worker) -> None:
    """If someone hands us a message whose last line is a bare closing XML tag
    and there is no <exception> block to extract, fall back to the whole
    message rather than keeping just '</last_exception>'.
    """
    raw = "something went wrong upstream\n</last_exception>"
    cleaned = modal_worker._sanitize_error(raw)
    assert cleaned.strip() != "</last_exception>"
    assert "something went wrong upstream" in cleaned


def test_sanitize_error_single_line_unchanged(modal_worker) -> None:
    """A plain single-line error message must pass through unchanged (modulo
    secret scrubbing)."""
    raw = "RateLimitError: too many requests"
    cleaned = modal_worker._sanitize_error(raw)
    assert cleaned == "RateLimitError: too many requests"


def test_sanitize_error_multiline_traceback_still_takes_last_line(
    modal_worker,
) -> None:
    """Classic Python tracebacks (no instructor envelope) still collapse to
    their final exception line, which is the most useful one."""
    raw = (
        "Traceback (most recent call last):\n"
        '  File "foo.py", line 1, in <module>\n'
        "    bar()\n"
        "ValueError: something specific"
    )
    cleaned = modal_worker._sanitize_error(raw)
    assert cleaned == "ValueError: something specific"


def test_sanitize_error_instructor_envelope_keeps_secret_scrubbing(
    modal_worker,
) -> None:
    """Extracting the <exception> block must still run the secret scrubbers on
    the extracted text — a user's key pasted into a retry envelope must not
    leak through."""
    # security: ignore — synthetic fake key for the scanner regression test
    fake_key = "sk-or-v1-abcdefghijklmnopqrstuvwxyz0123"
    raw = (
        "<last_exception><failed_attempts>"
        f"<exception>bad request for {fake_key}</exception>"
        "</failed_attempts></last_exception>"
    )
    cleaned = modal_worker._sanitize_error(raw)
    assert "sk-or-v1-abcdef" not in cleaned
    assert "[key]" in cleaned


# ---------------------------------------------------------------------------
# _classify_hosted_key_error — issue #106 wrong-key-type guidance
# ---------------------------------------------------------------------------


def test_classify_hosted_key_error_accepts_openrouter_key(modal_worker) -> None:
    key = "sk-or-v1-abcdefghijklmnopqrstuvwxyz0123"  # security: ignore
    assert modal_worker._classify_hosted_key_error(key) is None


@pytest.mark.parametrize(
    ("provider", "key"),
    [
        ("OpenAI", "sk-abcdefghijklmnopqrstuvwxyz0123"),  # security: ignore
        ("Anthropic", "sk-ant-abcdefghijklmnopqrstuvwxyz0123"),  # security: ignore
        ("Groq", "gsk_abcdefghijklmnopqrstuvwxyz0123"),  # security: ignore
        ("Perplexity", "pplx-abcdefghijklmnopqrstuvwxyz"),  # security: ignore
        ("Google", "AIzaSyabcdefghijklmnopqrstuvwxyz0123456789"),  # security: ignore
    ],
)
def test_classify_hosted_key_error_flags_direct_provider_keys(
    modal_worker, provider: str, key: str
) -> None:
    msg = modal_worker._classify_hosted_key_error(key)
    assert msg is not None
    assert provider in msg
    assert "OpenRouter API key" in msg
    assert "https://openrouter.ai/keys" in msg


def test_classify_hosted_key_error_ignores_unknown_prefix(modal_worker) -> None:
    assert modal_worker._classify_hosted_key_error("custom-key-format-123") is None


# ---------------------------------------------------------------------------
# _strip_nul_bytes — Postgres 22P05 defense (#62)
# ---------------------------------------------------------------------------


def test_strip_nul_bytes_removes_real_nul(modal_worker) -> None:
    assert modal_worker._strip_nul_bytes("before\x00after") == "beforeafter"


def test_strip_nul_bytes_removes_json_escape(modal_worker) -> None:
    assert modal_worker._strip_nul_bytes("before\\u0000after") == "beforeafter"


def test_strip_nul_bytes_safe_on_none(modal_worker) -> None:
    assert modal_worker._strip_nul_bytes(None) is None


def test_strip_nul_bytes_safe_on_empty(modal_worker) -> None:
    assert modal_worker._strip_nul_bytes("") == ""


def test_strip_nul_bytes_leaves_normal_text_alone(modal_worker) -> None:
    text = "Regular paper content with math $x^2 + y^2 = z^2$ and newlines\n."
    assert modal_worker._strip_nul_bytes(text) == text


# ---------------------------------------------------------------------------
# ReviewRequest.author_notes plumbing (#54)
# ---------------------------------------------------------------------------


def test_review_request_accepts_author_notes(modal_worker) -> None:
    """ReviewRequest deserializes an optional author_notes string from the
    webhook payload so the field can flow through to review_paper()."""
    req = modal_worker.ReviewRequest(
        job_id="j1",
        pdf_storage_path="abcd.pdf",
        author_notes="focus on method section",
    )
    assert req.author_notes == "focus on method section"


def test_review_request_author_notes_defaults_to_none(modal_worker) -> None:
    """Older in-flight spawn() payloads (and web submits without notes)
    still deserialize cleanly — author_notes defaults to None so no
    backward-compat break."""
    req = modal_worker.ReviewRequest(job_id="j1", pdf_storage_path="abcd.pdf")
    assert req.author_notes is None


def test_strip_nul_bytes_applies_to_author_notes(modal_worker) -> None:
    """author_notes with NUL bytes must be scrubbed before reaching the LLM.
    Defense against the same failure mode that Supabase 22P05 triggers — some
    LLM providers reject NUL in content strings, and do so in a way that
    surfaces as an opaque 'review failed' at the end of the pipeline.
    author_notes is never persisted, but it IS passed to the prompt builder,
    so the strip must run here."""
    raw = "focus on section 3\x00 and also section 4"
    scrubbed = modal_worker._strip_nul_bytes(raw)
    assert "\x00" not in scrubbed
    assert "focus on section 3" in scrubbed
    assert "section 4" in scrubbed


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
    """Minimal chainable stub that mimics supabase-py's query builder.

    Intentionally narrow: does NOT validate call order. If supabase-py's
    signature drifts (e.g. `.select()` must come before `.eq()`), these tests
    will still pass. The tradeoff is acceptable because the helper under
    test is tiny and the real code path is exercised end-to-end by the
    integration path in production.
    """

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

    def execute(self):
        if self._table.raise_on == self._op:
            # Raise with the configured exception (may contain a secret for
            # the log-leak tests) so _sanitize_error is actually exercised.
            raise RuntimeError(self._table.raise_message or f"fake {self._op} failure")
        if self._op == "select":
            # Real postgrest `maybe_single()` returns None (not a namespace)
            # when the row doesn't exist. Match that when row is None so the
            # `result is None` branch in _fetch_and_consume_user_key is
            # actually covered.
            if self._table.row is None:
                return None
            return types.SimpleNamespace(data=self._table.row)
        if self._op == "delete":
            self._table.deleted.append(self._filter)
            return types.SimpleNamespace(data=None)
        raise AssertionError(f"unknown op {self._op}")


class _FakeSupabaseTable:
    def __init__(
        self,
        row: dict | None = None,
        raise_on: str | None = None,
        raise_message: str | None = None,
    ) -> None:
        self.row = row
        self.raise_on = raise_on
        self.raise_message = raise_message
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
    """A delete failure whose exception message literally contains the key is
    still scrubbed before it reaches stdout/stderr. This verifies that
    _sanitize_error is actually applied on the log path, not just trivially."""
    secret = "sk-or-v1-supersecretkey1234567890abcdef"  # security: ignore
    # Inject the secret into the fake exception message so the test actually
    # exercises _sanitize_error (rather than trivially passing because the
    # fake message doesn't contain the key).
    leaky_message = f"upstream 500: Authorization: Bearer {secret}"
    table = _FakeSupabaseTable(
        row={"user_api_key": secret},
        raise_on="delete",
        raise_message=leaky_message,
    )
    db = _FakeSupabase(table)

    modal_worker._fetch_and_consume_user_key(db, "job-log-test")
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    # The raw key must never reach stdout/stderr, even though it was in the
    # exception message that the helper caught and logged.
    assert secret not in combined
    # And the helper must have actually logged something (regression guard
    # against a future refactor that silently drops the log line).
    assert "review_secrets DELETE failed" in combined
    assert "[key]" in combined


# ---------------------------------------------------------------------------
# _resolve_user_api_key — precedence between review_secrets and req payload
# ---------------------------------------------------------------------------


def _make_review_request(modal_worker, user_api_key: str | None = None):
    """Build a real ReviewRequest so the test exercises the actual Pydantic shape."""
    return modal_worker.ReviewRequest(
        job_id="j1",
        pdf_storage_path="papers/j1.pdf",
        user_api_key=user_api_key,
    )


def test_resolve_user_api_key_prefers_review_secrets(modal_worker) -> None:
    """When BOTH sources have a key, review_secrets wins and the row is consumed."""
    ferried = "sk-or-v1-ferried123456789012345678901234"  # security: ignore
    backward = "sk-or-v1-backcompat12345678901234567890"  # security: ignore
    table = _FakeSupabaseTable(row={"user_api_key": ferried})
    db = _FakeSupabase(table)
    req = _make_review_request(modal_worker, user_api_key=backward)

    result = modal_worker._resolve_user_api_key(db, req, "j1")
    assert result == ferried
    # The review_secrets row was consumed (DELETE was called).
    assert table.deleted == [("review_id", "j1")]


def test_resolve_user_api_key_falls_back_to_req_user_api_key(modal_worker) -> None:
    """When review_secrets has no row, fall back to req.user_api_key (backward compat)."""
    backward = "sk-or-v1-backcompat987654321098765432109"  # security: ignore
    table = _FakeSupabaseTable(row=None)
    db = _FakeSupabase(table)
    req = _make_review_request(modal_worker, user_api_key=backward)

    result = modal_worker._resolve_user_api_key(db, req, "j1")
    assert result == backward
    # No row to delete, so DELETE was never called.
    assert table.deleted == []


def test_resolve_user_api_key_returns_none_when_both_sources_empty(modal_worker) -> None:
    """Both sources empty → return None. Caller proceeds without setting the env
    var, and the first LLM call surfaces a 401 handled by _classify_api_error."""
    table = _FakeSupabaseTable(row=None)
    db = _FakeSupabase(table)
    req = _make_review_request(modal_worker, user_api_key=None)

    assert modal_worker._resolve_user_api_key(db, req, "j1") is None


def test_resolve_user_api_key_strips_whitespace_from_review_secrets(modal_worker) -> None:
    """A whitespace-only review_secrets value should NOT be returned (it would
    yield an empty Bearer header). Fall through to req.user_api_key instead.

    The whitespace row IS still deleted by _fetch_and_consume_user_key before
    the strip-check fires, so a stray row can't rot until the TTL cron."""
    backward = "sk-or-v1-backcompat56565656565656565656"  # security: ignore
    table = _FakeSupabaseTable(row={"user_api_key": "   \n"})
    db = _FakeSupabase(table)
    req = _make_review_request(modal_worker, user_api_key=backward)

    result = modal_worker._resolve_user_api_key(db, req, "j1")
    # Whitespace-only DB value is rejected; falls back to req payload.
    assert result == backward
    # But the row was still consumed (the TTL cron doesn't need to clean it up).
    assert table.deleted == [("review_id", "j1")]


# ---------------------------------------------------------------------------
# do_review — integration test for key installation into os.environ
# ---------------------------------------------------------------------------


def test_do_review_installs_resolved_key_into_environ(modal_worker, monkeypatch) -> None:
    """When _resolve_user_api_key returns a key, do_review must write it into
    OPENROUTER_API_KEY BEFORE the pipeline runs. Regression guard against a
    refactor that reorders the env-var install or drops it entirely.

    Stubs supabase.create_client so do_review can build a `db` object, then
    captures the env var inside a fake `storage.download` call that raises to
    short-circuit the rest of the pipeline before review_paper() runs."""
    import os as _os
    import sys as _sys

    resolved = "sk-or-v1-fromferryintegrationtest12345"  # security: ignore
    captured: dict[str, str | None] = {}

    class _FakeDownload:
        def from_(self, _bucket):
            return self

        def download(self, _path):
            # Capture env var state at the earliest point after key resolution,
            # before the finally block restores the original key.
            captured["env"] = _os.environ.get("OPENROUTER_API_KEY")
            raise RuntimeError("short-circuit before review_paper")

    class _FakeReviewsTable:
        def update(self, _data):
            return self

        def eq(self, _col, _val):
            return self

        def execute(self):
            return types.SimpleNamespace(data=[])

    class _FakeDB:
        def __init__(self):
            self.storage = _FakeDownload()

        def table(self, _name):
            return _FakeReviewsTable()

    def _fake_create_client(_url, _key):
        return _FakeDB()

    # Install a fake supabase module so the lazy `from supabase import
    # create_client` inside do_review resolves to our fake.
    supabase_stub = types.ModuleType("supabase")
    supabase_stub.create_client = _fake_create_client
    monkeypatch.setitem(_sys.modules, "supabase", supabase_stub)

    # Stub _resolve_user_api_key so we don't depend on the fake supabase's
    # review_secrets path — the unit tests above already cover that.
    monkeypatch.setattr(modal_worker, "_resolve_user_api_key", lambda _db, _req, _job: resolved)

    monkeypatch.setenv("SUPABASE_URL", "https://fake.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "fake-service-key")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="short-circuit before review_paper"):
        modal_worker.do_review(
            {
                "job_id": "integration-test-job",
                "pdf_storage_path": "papers/test.pdf",
            }
        )

    # The env var was installed BEFORE the download call that raised.
    # (do_review's finally-block cleanup lives inside a later `try:` block
    # that we short-circuit before reaching, so env-cleanup is out of scope
    # for this test — monkeypatch restores it on teardown.)
    assert captured["env"] == resolved


def test_do_review_skips_environ_write_when_no_key_resolved(modal_worker, monkeypatch) -> None:
    """When _resolve_user_api_key returns None, do_review must NOT write an
    empty string to OPENROUTER_API_KEY (that would produce a `Bearer ` header
    and cascade 401s through every LLM call). Regression guard."""
    import os as _os
    import sys as _sys

    captured: dict[str, str | None] = {}

    class _FakeDownload:
        def from_(self, _bucket):
            return self

        def download(self, _path):
            captured["env"] = _os.environ.get("OPENROUTER_API_KEY", "<unset>")
            raise RuntimeError("short-circuit before review_paper")

    class _FakeReviewsTable:
        def update(self, _data):
            return self

        def eq(self, _col, _val):
            return self

        def execute(self):
            return types.SimpleNamespace(data=[])

    class _FakeDB:
        def __init__(self):
            self.storage = _FakeDownload()

        def table(self, _name):
            return _FakeReviewsTable()

    supabase_stub = types.ModuleType("supabase")
    supabase_stub.create_client = lambda _u, _k: _FakeDB()
    monkeypatch.setitem(_sys.modules, "supabase", supabase_stub)

    monkeypatch.setattr(modal_worker, "_resolve_user_api_key", lambda _db, _req, _job: None)

    monkeypatch.setenv("SUPABASE_URL", "https://fake.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "fake-service-key")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="short-circuit before review_paper"):
        modal_worker.do_review(
            {
                "job_id": "no-key-test-job",
                "pdf_storage_path": "papers/test.pdf",
            }
        )

    # Env var was NOT set to "" — it stays unset.
    assert captured["env"] == "<unset>"
