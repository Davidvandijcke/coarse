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
    """Install minimal stand-ins for `modal` and `fastapi` in sys.modules.

    Unconditionally replaces `sys.modules['modal']` and
    `sys.modules['fastapi']` so this test file always sees a known
    no-op Modal + FastAPI surface regardless of what's already in
    `sys.modules`. The old MCP server test suite had an import-order
    dependency that bit every time tests ran in a certain order;
    unconditional stubbing kills the dependency. (The MCP server
    itself was removed in v1.3.0.)
    """
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
# _classify_api_error — worker-side terminal classifier
# ---------------------------------------------------------------------------
#
# This is the classifier that writes into reviews.error_message on the
# status page (see do_review's except BaseException branch). It must
# stay in lockstep with coarse.extraction_openrouter._classify_api_error
# because one catches the error at the extraction stage and the other
# catches it at the Modal worker's outer boundary — a fix in only one
# leaves the user-facing message wrong on the status page.


def test_classify_api_error_detects_management_key_user_not_found(modal_worker) -> None:
    """Worker classifier must match the extraction-side management-key
    detection. Regression guard for PR #173's two-classifier split."""
    from unittest.mock import MagicMock

    resp = MagicMock()
    resp.status_code = 401
    resp.json.return_value = {"error": {"message": "User not found.", "code": 401}}
    exc = RuntimeError("401 Unauthorized")
    exc.response = resp  # type: ignore[attr-defined]

    msg = modal_worker._classify_api_error(exc) or ""
    assert "provisioning" in msg.lower() or "management" in msg.lower()
    assert "openrouter.ai/settings/keys" in msg


def test_classify_api_error_generic_401_keeps_invalid_key_message(modal_worker) -> None:
    """Plain 401s without 'User not found' still return the generic copy."""
    from unittest.mock import MagicMock

    resp = MagicMock()
    resp.status_code = 401
    resp.json.return_value = {"error": {"message": "Unauthorized", "code": 401}}
    exc = RuntimeError("401 Unauthorized")
    exc.response = resp  # type: ignore[attr-defined]

    msg = modal_worker._classify_api_error(exc) or ""
    assert msg == "Invalid API key. Check that your key is correct and active."


def test_classify_api_error_survives_unparseable_body(modal_worker) -> None:
    """resp.json() raising must not crash the classifier — falls through
    to the generic branch."""
    from unittest.mock import MagicMock

    resp = MagicMock()
    resp.status_code = 401
    resp.json.side_effect = ValueError("not JSON")
    resp.text = "<html>Bad Gateway</html>"
    exc = RuntimeError("401 Unauthorized")
    exc.response = resp  # type: ignore[attr-defined]

    msg = modal_worker._classify_api_error(exc) or ""
    assert msg == "Invalid API key. Check that your key is correct and active."


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
# _fetch_user_key / _delete_user_key — issue #49 (review_secrets ferry),
# split idempotently in #175 so Modal preemption retries still find a key.
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


def test_fetch_user_key_returns_key_without_deleting_row(modal_worker) -> None:
    """Happy path: SELECT returns a row; DELETE is NOT called (issue #175). The
    row stays around so a Modal preemption retry can read the same key."""
    table = _FakeSupabaseTable(
        row={"user_api_key": "sk-or-v1-fakefakefakefakefakefakefake"}  # security: ignore
    )
    db = _FakeSupabase(table)

    key = modal_worker._fetch_user_key(db, "job-1")
    assert key == "sk-or-v1-fakefakefakefakefakefakefake"  # security: ignore
    # SELECT only — no DELETE call on the fetch path.
    assert db.table_names == ["review_secrets"]
    assert table.deleted == []


def test_fetch_user_key_returns_none_when_row_missing(modal_worker) -> None:
    """No row → return None → caller falls back to req.user_api_key."""
    table = _FakeSupabaseTable(row=None)
    db = _FakeSupabase(table)

    key = modal_worker._fetch_user_key(db, "job-missing")
    assert key is None
    assert table.deleted == []


def test_fetch_user_key_returns_none_on_select_error(modal_worker) -> None:
    """SELECT failure is swallowed; caller still falls back to backward-compat."""
    table = _FakeSupabaseTable(row=None, raise_on="select")
    db = _FakeSupabase(table)

    key = modal_worker._fetch_user_key(db, "job-boom")
    assert key is None
    assert table.deleted == []


def test_delete_user_key_deletes_row(modal_worker) -> None:
    """Happy path: DELETE fires against the matching review_id filter."""
    table = _FakeSupabaseTable(
        row={"user_api_key": "sk-or-v1-irrelevantforthiscase012345"}  # security: ignore
    )
    db = _FakeSupabase(table)

    modal_worker._delete_user_key(db, "job-done")
    assert table.deleted == [("review_id", "job-done")]


def test_delete_user_key_tolerates_delete_failure(modal_worker) -> None:
    """DELETE failure is non-fatal — swallowed so a flaky Postgres hop doesn't
    crash the worker's terminal-status path. The TTL cron sweeps the orphan."""
    table = _FakeSupabaseTable(row=None, raise_on="delete")
    db = _FakeSupabase(table)

    # Must not raise — the sentinel to look for is "did not propagate".
    modal_worker._delete_user_key(db, "job-delete-boom")


def test_delete_user_key_does_not_leak_key_into_log_on_failure(modal_worker, capsys) -> None:
    """A delete failure whose exception message literally contains the key is
    still scrubbed before it reaches stdout/stderr. Ported from the old
    _fetch_and_consume test — the log-sanitization contract lives with the
    DELETE, which is now in _delete_user_key."""
    secret = "sk-or-v1-supersecretkey1234567890abcdef"  # security: ignore
    leaky_message = f"upstream 500: Authorization: Bearer {secret}"
    table = _FakeSupabaseTable(row=None, raise_on="delete", raise_message=leaky_message)
    db = _FakeSupabase(table)

    modal_worker._delete_user_key(db, "job-log-test")
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
    """When BOTH sources have a key, review_secrets wins.

    The row is NOT deleted by resolve (#175 — DELETE is deferred to terminal
    status so preemption retries still find a key).
    """
    ferried = "sk-or-v1-ferried123456789012345678901234"  # security: ignore
    backward = "sk-or-v1-backcompat12345678901234567890"  # security: ignore
    table = _FakeSupabaseTable(row={"user_api_key": ferried})
    db = _FakeSupabase(table)
    req = _make_review_request(modal_worker, user_api_key=backward)

    result = modal_worker._resolve_user_api_key(db, req, "j1")
    assert result == ferried
    # The DELETE no longer fires on the resolve path — it's wired into the
    # do_review terminal-status paths instead.
    assert table.deleted == []


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
    """A whitespace-only review_secrets value is rejected (it would yield an
    empty Bearer header) and resolve falls back to req.user_api_key.

    The whitespace row is NOT deleted by resolve (#175 — DELETE is deferred
    to terminal status). If the review ultimately completes it'll get deleted
    then; if it never does, the 3 h cleanup_review_secrets cron sweeps.
    """
    backward = "sk-or-v1-backcompat56565656565656565656"  # security: ignore
    table = _FakeSupabaseTable(row={"user_api_key": "   \n"})
    db = _FakeSupabase(table)
    req = _make_review_request(modal_worker, user_api_key=backward)

    result = modal_worker._resolve_user_api_key(db, req, "j1")
    # Whitespace-only DB value is rejected; falls back to req payload.
    assert result == backward
    # The row is NOT deleted here — the terminal-status path or the cron handles it.
    assert table.deleted == []


# ---------------------------------------------------------------------------
# _download_pdf_with_retry — Supabase Storage download with retry
# ---------------------------------------------------------------------------


class _FakeStorageDownload:
    """Callable-styled storage stub: each entry in ``responses`` is either a
    bytes payload to return or a BaseException instance to raise."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = 0

    def from_(self, _bucket):
        return self

    def download(self, _path):
        self.calls += 1
        if not self._responses:
            raise RuntimeError("_FakeStorageDownload exhausted responses")
        nxt = self._responses.pop(0)
        # `isinstance(nxt, BaseException)` catches both Exception and the
        # BaseException-but-not-Exception types (KeyboardInterrupt,
        # SystemExit, GeneratorExit) which is important for the
        # propagation test.
        if isinstance(nxt, BaseException):
            raise nxt
        return nxt


class _FakeDBWithStorage:
    def __init__(self, storage):
        self.storage = storage


def test_download_pdf_with_retry_returns_on_first_success(modal_worker, monkeypatch) -> None:
    """Happy path: first call succeeds, no sleeping, no retry logs."""
    monkeypatch.setattr("time.sleep", lambda _s: None)
    storage = _FakeStorageDownload([b"pdf-bytes"])
    db = _FakeDBWithStorage(storage)

    out = modal_worker._download_pdf_with_retry(db, "papers/test.pdf", "job-1")
    assert out == b"pdf-bytes"
    assert storage.calls == 1


def test_download_pdf_with_retry_recovers_from_transient_read_timeout(
    modal_worker, monkeypatch
) -> None:
    """A single transient httpx ReadTimeout should be absorbed silently."""
    sleeps: list[float] = []
    monkeypatch.setattr("time.sleep", lambda s: sleeps.append(s))

    import httpx

    storage = _FakeStorageDownload(
        [
            httpx.ReadTimeout("simulated transient timeout"),
            b"pdf-bytes-2",
        ]
    )
    db = _FakeDBWithStorage(storage)

    out = modal_worker._download_pdf_with_retry(db, "papers/test.pdf", "job-2")
    assert out == b"pdf-bytes-2"
    assert storage.calls == 2
    # One 1-second backoff between attempt 1 and attempt 2.
    assert sleeps == [1]


def test_download_pdf_with_retry_gives_up_after_max_attempts(modal_worker, monkeypatch) -> None:
    """Four back-to-back failures should raise RuntimeError with chained cause
    and have slept 1+2+4 seconds total between attempts."""
    sleeps: list[float] = []
    monkeypatch.setattr("time.sleep", lambda s: sleeps.append(s))

    import httpx

    last_exc = httpx.ReadTimeout("final attempt")
    storage = _FakeStorageDownload(
        [
            httpx.ReadTimeout("attempt 1"),
            httpx.ReadTimeout("attempt 2"),
            httpx.ReadTimeout("attempt 3"),
            last_exc,
        ]
    )
    db = _FakeDBWithStorage(storage)

    with pytest.raises(RuntimeError, match="failed after 4 attempts"):
        modal_worker._download_pdf_with_retry(db, "papers/test.pdf", "job-3")
    assert storage.calls == 4
    # Sleep between attempts 1->2, 2->3, 3->4 (no sleep after final failure).
    assert sleeps == [1, 2, 4]


def test_download_pdf_with_retry_rejects_empty_bytes(modal_worker, monkeypatch) -> None:
    """Supabase returning empty bytes is treated as a retryable failure — the
    old code raised `ValueError` without retry on this, so behaviour is now
    explicit: empty → retry → eventual RuntimeError if it keeps happening."""
    sleeps: list[float] = []
    monkeypatch.setattr("time.sleep", lambda s: sleeps.append(s))

    storage = _FakeStorageDownload([b"", b"", b"", b""])  # 4 empty downloads
    db = _FakeDBWithStorage(storage)

    with pytest.raises(RuntimeError, match="failed after 4 attempts"):
        modal_worker._download_pdf_with_retry(db, "papers/test.pdf", "job-4")
    assert storage.calls == 4


def test_download_pdf_with_retry_propagates_keyboardinterrupt(modal_worker, monkeypatch) -> None:
    """BaseException-but-not-Exception must propagate — KeyboardInterrupt /
    SystemExit / GeneratorExit should not be swallowed by the retry loop."""
    monkeypatch.setattr("time.sleep", lambda _s: None)
    storage = _FakeStorageDownload([KeyboardInterrupt("user pressed ctrl-c")])
    db = _FakeDBWithStorage(storage)

    with pytest.raises(KeyboardInterrupt):
        modal_worker._download_pdf_with_retry(db, "papers/test.pdf", "job-5")
    assert storage.calls == 1  # no retry


# ---------------------------------------------------------------------------
# do_review — integration test for key installation into os.environ
# ---------------------------------------------------------------------------


def test_do_review_installs_resolved_key_into_environ(modal_worker, monkeypatch) -> None:
    """When _resolve_user_api_key returns a key, do_review must write it into
    OPENROUTER_API_KEY BEFORE the pipeline runs. Regression guard against a
    refactor that reorders the env-var install or drops it entirely.

    Stubs supabase.create_client so do_review can build a `db` object, then
    stubs _download_pdf_with_retry itself to capture the env var at the
    earliest point after key resolution and raise to short-circuit the rest
    of the pipeline before review_paper() runs. Stubbing the retry helper
    (rather than the underlying storage.download call) avoids sitting
    through 7s of exponential-backoff sleeps and keeps the test insulated
    from the retry-contract details."""
    import os as _os
    import sys as _sys

    resolved = "sk-or-v1-fromferryintegrationtest12345"  # security: ignore
    captured: dict[str, str | None] = {}

    class _FakeReviewsTable:
        def update(self, _data):
            return self

        def eq(self, _col, _val):
            return self

        def execute(self):
            return types.SimpleNamespace(data=[])

    class _FakeDB:
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

    # Stub the retry helper — captures env right after the key install, then
    # short-circuits with a BaseException subclass (SystemExit) so the
    # helper's `except Exception` never swallows us on a hypothetical
    # retry-path regression.
    def _fake_download(_db, _path, _job, **_kwargs):
        captured["env"] = _os.environ.get("OPENROUTER_API_KEY")
        raise SystemExit("short-circuit before review_paper")

    monkeypatch.setattr(modal_worker, "_download_pdf_with_retry", _fake_download)

    monkeypatch.setenv("SUPABASE_URL", "https://fake.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "fake-service-key")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(SystemExit, match="short-circuit before review_paper"):
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


def test_do_review_fails_fast_when_no_key_resolved(modal_worker, monkeypatch) -> None:
    """When _resolve_user_api_key returns None AND the Modal-baked env has no
    OpenRouter key either, do_review must fail fast with a clear user-facing
    message BEFORE entering the pipeline. The previous behavior (silent
    fall-through) let _normalize_model in src/coarse/llm.py emit a raw
    `anthropic/...` model string, which litellm then routed directly to the
    Anthropic API and died with "Missing Anthropic API Key" on every stage —
    see issue #171."""
    import os as _os
    import sys as _sys

    update_calls: list[dict] = []

    class _FakeReviewsTable:
        def update(self, data):
            update_calls.append(dict(data))
            return self

        def eq(self, _col, _val):
            return self

        def execute(self):
            return types.SimpleNamespace(data=[])

    class _FakeDB:
        def table(self, _name):
            return _FakeReviewsTable()

    supabase_stub = types.ModuleType("supabase")
    supabase_stub.create_client = lambda _u, _k: _FakeDB()
    monkeypatch.setitem(_sys.modules, "supabase", supabase_stub)

    monkeypatch.setattr(modal_worker, "_resolve_user_api_key", lambda _db, _req, _job: None)

    # If fail-fast regresses, do_review will try to download the PDF. Make
    # that raise a distinctive error so the test fails loudly on the wrong
    # code path rather than hanging or succeeding silently.
    def _fake_download(_db, _path, _job, **_kwargs):
        raise AssertionError("fail-fast regression: download should not be called")

    monkeypatch.setattr(modal_worker, "_download_pdf_with_retry", _fake_download)

    monkeypatch.setenv("SUPABASE_URL", "https://fake.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "fake-service-key")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(ValueError, match="couldn't find your OpenRouter API key"):
        modal_worker.do_review(
            {
                "job_id": "no-key-test-job",
                "pdf_storage_path": "papers/test.pdf",
            }
        )

    # Env var is NOT set (do_review never installed one — there was nothing to install).
    assert "OPENROUTER_API_KEY" not in _os.environ

    # The failure message was written to the reviews row BEFORE the raise, so
    # the user sees a clear explanation on the status page instead of a stale
    # "running" spinner or a generic server error.
    failed_updates = [c for c in update_calls if c.get("status") == "failed"]
    assert len(failed_updates) == 1
    assert "OpenRouter API key" in failed_updates[0].get("error_message", "")


def test_do_review_uses_modal_baked_env_key_when_review_secrets_empty(
    modal_worker, monkeypatch
) -> None:
    """Dev/local-runner safety: if OPENROUTER_API_KEY is already set in the
    container's env (e.g. a developer running the worker locally with their
    own key exported), do_review must NOT fail fast even when review_secrets
    is empty. The fail-fast guard only fires when BOTH sources are empty."""
    import sys as _sys

    class _FakeReviewsTable:
        def update(self, _data):
            return self

        def eq(self, _col, _val):
            return self

        def execute(self):
            return types.SimpleNamespace(data=[])

    class _FakeDB:
        def table(self, _name):
            return _FakeReviewsTable()

    supabase_stub = types.ModuleType("supabase")
    supabase_stub.create_client = lambda _u, _k: _FakeDB()
    monkeypatch.setitem(_sys.modules, "supabase", supabase_stub)

    monkeypatch.setattr(modal_worker, "_resolve_user_api_key", lambda _db, _req, _job: None)

    def _fake_download(_db, _path, _job, **_kwargs):
        raise SystemExit("short-circuit before review_paper")

    monkeypatch.setattr(modal_worker, "_download_pdf_with_retry", _fake_download)

    monkeypatch.setenv("SUPABASE_URL", "https://fake.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "fake-service-key")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-localdevkey0123456789")  # security: ignore

    # Reaches download (no ValueError) — that means the fail-fast guard
    # correctly deferred to the env-baked key.
    with pytest.raises(SystemExit, match="short-circuit before review_paper"):
        modal_worker.do_review(
            {
                "job_id": "env-key-test-job",
                "pdf_storage_path": "papers/test.pdf",
            }
        )


# ---------------------------------------------------------------------------
# do_review — preemption-safe key-delete gating (issue #175).
#
# Modal's worker preemption restarts the function on the same input
# regardless of retries=0. The worker used to SELECT + DELETE review_secrets
# at startup, which left preemption retries with an empty row and a broken
# review. The fix defers DELETE to terminal status paths and skips it on
# SystemExit so Modal's automatic restart still finds a usable key.
# ---------------------------------------------------------------------------


def _install_do_review_stubs(
    modal_worker, monkeypatch, *, resolved: str | None, delete_calls: list
) -> None:
    """Shared scaffolding for the three preemption-safety tests below.

    Stubs supabase.create_client, the key-resolve helper, and the
    _delete_user_key helper so the test can assert how many times DELETE
    fired under different do_review exit paths. Each caller still stubs
    _download_pdf_with_retry or review_paper to drive the specific branch
    (SystemExit, regular exception, or success)."""
    import sys as _sys

    class _FakeReviewsTable:
        def update(self, _data):
            return self

        def eq(self, _col, _val):
            return self

        def execute(self):
            return types.SimpleNamespace(data=[])

    class _FakeDB:
        def table(self, _name):
            return _FakeReviewsTable()

        # Storage surface used by do_review on the success path for
        # ``db.storage.from_("papers").remove([...])``. No-op here.
        class _FakeStorage:
            def from_(self, _bucket):
                return self

            def remove(self, _paths):
                return None

            def create_signed_url(self, _path, _ttl):
                return {"signedURL": "https://example.invalid/signed"}

            def download(self, _path):
                return b"%PDF-1.4\nstub\n"

        storage = _FakeStorage()

    supabase_stub = types.ModuleType("supabase")
    supabase_stub.create_client = lambda _u, _k: _FakeDB()
    monkeypatch.setitem(_sys.modules, "supabase", supabase_stub)

    monkeypatch.setattr(modal_worker, "_resolve_user_api_key", lambda _db, _req, _job: resolved)

    def _tracking_delete(_db, job_id):
        delete_calls.append(job_id)

    monkeypatch.setattr(modal_worker, "_delete_user_key", _tracking_delete)

    monkeypatch.setenv("SUPABASE_URL", "https://fake.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "fake-service-key")
    monkeypatch.setenv("REVIEW_ACCESS_SECRET", "fake-review-access-secret-32-chars")


def _install_coarse_stubs(monkeypatch, *, review_paper_behavior) -> None:
    """Stub the coarse submodules that ``do_review`` imports inside its try
    block. ``review_paper_behavior`` is a callable invoked as
    ``review_paper(*args, **kwargs)`` — return a triple for success, or raise
    to exercise the except-branch.

    The except-BaseException branch in do_review only catches exceptions
    raised from INSIDE its try block (which begins at `from coarse import
    review_paper`). A download failure before that try block propagates
    straight through, so the preemption / failure / success tests have to
    drive the branch via review_paper itself.
    """
    import sys as _sys

    coarse_stub = types.ModuleType("coarse")
    coarse_stub.review_paper = review_paper_behavior
    monkeypatch.setitem(_sys.modules, "coarse", coarse_stub)

    config_stub = types.ModuleType("coarse.config")

    class _CoarseConfig:
        def __init__(self, **_kwargs):
            pass

    config_stub.CoarseConfig = _CoarseConfig
    monkeypatch.setitem(_sys.modules, "coarse.config", config_stub)

    extraction_stub = types.ModuleType("coarse.extraction_openrouter")

    class _StubCtx:
        def set(self, _value):
            return object()

        def reset(self, _token):
            return None

    extraction_stub.signed_url_ctx = _StubCtx()
    monkeypatch.setitem(_sys.modules, "coarse.extraction_openrouter", extraction_stub)


def test_do_review_skips_delete_on_systemexit_for_preemption(modal_worker, monkeypatch) -> None:
    """Preemption manifests as SystemExit (Modal SIGTERMs the container). The
    DELETE must NOT fire on that path — Modal will restart on the same input
    and needs the review_secrets row intact (issue #175)."""
    resolved = "sk-or-v1-preemptiontest12345678901234"  # security: ignore
    delete_calls: list[str] = []
    _install_do_review_stubs(
        modal_worker, monkeypatch, resolved=resolved, delete_calls=delete_calls
    )

    def _preempt(*_args, **_kwargs):
        raise SystemExit("simulate modal preemption SIGTERM")

    _install_coarse_stubs(monkeypatch, review_paper_behavior=_preempt)
    monkeypatch.setattr(
        modal_worker, "_download_pdf_with_retry", lambda *_a, **_kw: b"%PDF-1.4\nstub\n"
    )
    monkeypatch.setattr(modal_worker, "_get_review_status", lambda _db, _job: "running")

    with pytest.raises(SystemExit, match="simulate modal preemption"):
        modal_worker.do_review(
            {
                "job_id": "preempt-test-job",
                "pdf_storage_path": "papers/test.pdf",
            }
        )

    assert delete_calls == [], (
        "DELETE fired on SystemExit — this will orphan the Modal preemption retry"
    )


def test_do_review_deletes_on_non_systemexit_failure(modal_worker, monkeypatch) -> None:
    """A regular Exception is a terminal failure — Modal will NOT restart it
    (retries=0). The DELETE should fire so the key isn't left to age out via
    the 3 h TTL cron."""
    resolved = "sk-or-v1-regularfailuretest1234567890"  # security: ignore
    delete_calls: list[str] = []
    _install_do_review_stubs(
        modal_worker, monkeypatch, resolved=resolved, delete_calls=delete_calls
    )

    def _explode(*_args, **_kwargs):
        raise RuntimeError("simulate pipeline failure")

    _install_coarse_stubs(monkeypatch, review_paper_behavior=_explode)
    monkeypatch.setattr(
        modal_worker, "_download_pdf_with_retry", lambda *_a, **_kw: b"%PDF-1.4\nstub\n"
    )
    monkeypatch.setattr(modal_worker, "_get_review_status", lambda _db, _job: "running")

    with pytest.raises(RuntimeError, match="simulate pipeline failure"):
        modal_worker.do_review(
            {
                "job_id": "fail-test-job",
                "pdf_storage_path": "papers/test.pdf",
            }
        )

    assert delete_calls == ["fail-test-job"], (
        "DELETE did not fire on a terminal non-SystemExit failure; the key will "
        "linger until the 3 h cleanup cron sweeps it"
    )


def test_do_review_deletes_on_success(modal_worker, monkeypatch) -> None:
    """Happy path: DELETE fires after the status=done write. This is the only
    path where we positively consume the key, matching the pre-#175 behavior
    for non-preempted reviews."""
    resolved = "sk-or-v1-successpathtest12345678901234"  # security: ignore
    delete_calls: list[str] = []
    _install_do_review_stubs(
        modal_worker, monkeypatch, resolved=resolved, delete_calls=delete_calls
    )

    class _FakeReview:
        title = "Stub Paper"
        domain = "social_sciences"

    class _FakePaperText:
        full_markdown = "# stub"

    def _happy_review_paper(*_args, **_kwargs):
        return _FakeReview(), "## stub review", _FakePaperText()

    _install_coarse_stubs(monkeypatch, review_paper_behavior=_happy_review_paper)
    monkeypatch.setattr(
        modal_worker, "_download_pdf_with_retry", lambda *_a, **_kw: b"%PDF-1.4\nstub\n"
    )
    monkeypatch.setattr(modal_worker, "_get_review_status", lambda _db, _job: "running")

    modal_worker.do_review(
        {
            "job_id": "success-test-job",
            "pdf_storage_path": "papers/test.pdf",
        }
    )

    assert delete_calls == ["success-test-job"], (
        "DELETE did not fire on success; the key will linger until the cron"
    )


# ---------------------------------------------------------------------------
# Deploy-branch guard — incident 2026-04-13.
#
# Production was running a stale `dev` snapshot because there was no
# guardrail against `modal deploy` from a non-main branch. These tests
# pin the guard's behavior across every code path:
#
#   - CI context (GITHUB_ACTIONS=true) with GITHUB_REF_NAME=main → pass.
#   - CI context with GITHUB_REF_NAME=dev → raise.
#   - Local context with git branch=main → pass.
#   - Local context with git branch=dev (no force env) → raise.
#   - Local context with git branch=dev and COARSE_MODAL_DEPLOY_FORCE=1
#     → warn to stderr and pass.
#   - Local context with git unavailable (PyPI install, sdist tarball)
#     → silent no-op (don't block a legitimate import).
#   - Import-time wrapper short-circuits when pytest is loaded (this is
#     how test_modal_worker.py is allowed to import the file at all).
#
# The tests call `_enforce_deploy_branch` directly, which skips the
# pytest and serverless-container short-circuits in
# `_enforce_deploy_branch_at_import_time`. Every local-branch case is
# mocked via `subprocess.check_output` — we never touch the real git
# state and therefore never risk breaking these tests based on what
# branch the contributor happens to be on.
# ---------------------------------------------------------------------------


def test_enforce_deploy_branch_ci_main_passes(modal_worker, monkeypatch):
    """In GitHub Actions on main, the guard is a no-op."""
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_REF_NAME", "main")
    monkeypatch.delenv("COARSE_MODAL_DEPLOY_FORCE", raising=False)

    # Should not raise.
    modal_worker._enforce_deploy_branch()


def test_enforce_deploy_branch_ci_non_main_raises(modal_worker, monkeypatch):
    """In GitHub Actions on a non-main ref, the guard refuses to deploy."""
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_REF_NAME", "dev")
    monkeypatch.delenv("COARSE_MODAL_DEPLOY_FORCE", raising=False)

    with pytest.raises(RuntimeError, match="Refusing to deploy Modal worker from branch 'dev'"):
        modal_worker._enforce_deploy_branch()


def test_enforce_deploy_branch_local_main_passes(modal_worker, monkeypatch):
    """On a local checkout pointing at main, the guard is a no-op."""
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.delenv("COARSE_MODAL_DEPLOY_FORCE", raising=False)
    monkeypatch.setattr("subprocess.check_output", lambda *a, **kw: "main\n")

    modal_worker._enforce_deploy_branch()


def test_enforce_deploy_branch_local_dev_raises(modal_worker, monkeypatch):
    """On a local dev branch (no force env), the guard refuses."""
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.delenv("COARSE_MODAL_DEPLOY_FORCE", raising=False)
    monkeypatch.setattr("subprocess.check_output", lambda *a, **kw: "feat/my-branch\n")

    with pytest.raises(
        RuntimeError,
        match="Refusing to deploy Modal worker from branch 'feat/my-branch'",
    ):
        modal_worker._enforce_deploy_branch()


def test_enforce_deploy_branch_local_dev_force_warns(modal_worker, monkeypatch, capsys):
    """COARSE_MODAL_DEPLOY_FORCE=1 downgrades refusal to a stderr warning."""
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.setenv("COARSE_MODAL_DEPLOY_FORCE", "1")
    monkeypatch.setattr("subprocess.check_output", lambda *a, **kw: "hotfix/emergency\n")

    modal_worker._enforce_deploy_branch()

    err = capsys.readouterr().err
    assert "hotfix/emergency" in err
    assert "COARSE_MODAL_DEPLOY_FORCE=1" in err


def test_enforce_deploy_branch_local_detached_falls_through(modal_worker, monkeypatch):
    """Git failures (detached HEAD, not-a-repo, missing git binary) are silent.

    The guard intentionally does NOT block on git errors — a PyPI
    install or sdist tarball has no git history, and refusing to import
    the module in that case would break every downstream consumer.
    """
    import subprocess as _sub

    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.delenv("COARSE_MODAL_DEPLOY_FORCE", raising=False)

    def _boom(*_a, **_kw):
        raise _sub.CalledProcessError(128, "git")

    monkeypatch.setattr("subprocess.check_output", _boom)

    # Should not raise.
    modal_worker._enforce_deploy_branch()


def test_enforce_deploy_branch_import_time_short_circuits_under_pytest(modal_worker):
    """`_enforce_deploy_branch_at_import_time` is a no-op when pytest is loaded.

    This is the contract that lets `_load_modal_worker()` at the top of
    this test file import the worker at all on a non-main branch. If
    it ever broke, no test in this file would run — so this test is a
    documentation anchor for the short-circuit guarantee.
    """
    import sys as _sys

    assert "pytest" in _sys.modules
    # Should not raise regardless of git / CI state.
    modal_worker._enforce_deploy_branch_at_import_time()


# ---------------------------------------------------------------------------
# _send_email — Resend migration (2026-04-13).
#
# The prior Gmail-SMTP implementation was best-effort-by-accident: it
# was a no-op when credentials were missing, but a Gmail outage during
# the ``with SMTP_SSL(...)`` block would bubble straight out of
# ``_send_email`` and, via ``do_review``, crash the review mid-flight.
# The Resend rewrite pins best-effort as a hard contract: missing key
# is a silent no-op, any exception inside the Resend client is
# swallowed and logged. These tests pin the contract against
# regression.
# ---------------------------------------------------------------------------


class _FakeResendEmails:
    """Captures calls to `resend.Emails.send(...)` for assertion."""

    def __init__(self, response=None, raises: BaseException | None = None):
        self.response = response if response is not None else {"id": "fake-email-id"}
        self.raises = raises
        self.calls: list[dict] = []

    def send(self, params):
        self.calls.append(params)
        if self.raises is not None:
            raise self.raises
        return self.response


def _install_fake_resend(
    modal_worker,
    monkeypatch,
    *,
    response=None,
    raises: BaseException | None = None,
) -> _FakeResendEmails:
    """Install a fake `resend` module so `import resend` inside _send_email
    resolves to the captured test double rather than the real package.
    """
    fake_emails = _FakeResendEmails(response=response, raises=raises)
    resend_stub = types.ModuleType("resend")
    resend_stub.api_key = None
    resend_stub.Emails = fake_emails
    monkeypatch.setitem(sys.modules, "resend", resend_stub)
    return fake_emails


def test_send_email_happy_path_calls_resend_with_from_to_subject_html(
    modal_worker, monkeypatch, capsys
):
    """Happy path: API key present, resend client called with the exact
    from/to/subject/html the caller passed."""
    monkeypatch.setenv("RESEND_API_KEY", "re_testkey123")
    fake = _install_fake_resend(modal_worker, monkeypatch)

    modal_worker._send_email(
        to="user@example.com",
        subject="Your paper is being reviewed",
        html="<p>Hi there</p>",
    )

    assert len(fake.calls) == 1
    call = fake.calls[0]
    assert call["from"] == modal_worker._RESEND_FROM_ADDRESS
    assert call["to"] == "user@example.com"
    assert call["subject"] == "Your paper is being reviewed"
    assert call["html"] == "<p>Hi there</p>"
    # Success log line includes the returned id for traceability
    out = capsys.readouterr().out
    assert "Resend send ok" in out
    assert "fake-email-id" in out


def test_send_email_missing_api_key_is_silent_noop(modal_worker, monkeypatch, capsys):
    """When RESEND_API_KEY is unset, _send_email must return without
    calling the Resend client at all — matching the old "Gmail creds
    missing → no-op" contract that local dev relies on."""
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    fake = _install_fake_resend(modal_worker, monkeypatch)

    # Should not raise.
    modal_worker._send_email(
        to="user@example.com",
        subject="subj",
        html="<p>body</p>",
    )

    assert fake.calls == []
    out = capsys.readouterr().out
    # No-op path logs a drop notice so the operator can see why no mail went out.
    assert "RESEND_API_KEY missing" in out


def test_send_email_swallows_exception_from_resend(modal_worker, monkeypatch, capsys):
    """If `resend.Emails.send(...)` raises, _send_email MUST NOT propagate.
    The original Gmail outage that motivated this migration was caused by
    exactly this class of bug leaking out of the email path and crashing
    do_review mid-review. Regression guard."""
    monkeypatch.setenv("RESEND_API_KEY", "re_testkey123")
    _install_fake_resend(
        modal_worker,
        monkeypatch,
        raises=RuntimeError("resend server is down"),
    )

    # Must not raise.
    modal_worker._send_email(
        to="user@example.com",
        subject="subj",
        html="<p>body</p>",
    )

    out = capsys.readouterr().out
    assert "Resend send failed" in out
    # The error message content is sanitized via _sanitize_error, but the
    # word "down" is a plain English token so it should pass through.
    assert "down" in out


def test_send_email_logs_unknown_id_when_resend_returns_empty_dict(
    modal_worker, monkeypatch, capsys
):
    """A 200 response with no `id` field (unusual but possible if the
    SDK surface shifts) should still log a success line with id=unknown
    rather than crash — best-effort contract."""
    monkeypatch.setenv("RESEND_API_KEY", "re_testkey123")
    _install_fake_resend(modal_worker, monkeypatch, response={})

    modal_worker._send_email(to="user@example.com", subject="s", html="h")

    out = capsys.readouterr().out
    assert "Resend send ok" in out
    assert "unknown" in out


def test_send_email_scrubs_secrets_from_error_message(modal_worker, monkeypatch, capsys):
    """If the Resend client raises with a message containing a bearer
    token or similar secret, the log line must go through _sanitize_error
    before reaching stdout. This is the same contract enforced on the
    Supabase error-log path above."""
    monkeypatch.setenv("RESEND_API_KEY", "re_testkey123")
    secret = "sk-or-v1-abcdefghijklmnopqrstuvwxyz0123"  # security: ignore
    fake_leaky = f"upstream: Authorization: Bearer {secret}"
    _install_fake_resend(
        modal_worker,
        monkeypatch,
        raises=RuntimeError(fake_leaky),
    )

    modal_worker._send_email(to="user@example.com", subject="s", html="h")

    out = capsys.readouterr().out
    assert "sk-or-v1-abcdef" not in out
    assert "[key]" in out
