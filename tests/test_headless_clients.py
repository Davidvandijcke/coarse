"""Regression tests for headless CLI-backed JSON parsing."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from coarse.headless_clients import (
    _SUBSCRIPTION_BILLING_KEYS,
    ClaudeCodeClient,
    CodexClient,
    GeminiClient,
    _classify_cli_error,
    _clean_subprocess_env,
)


@pytest.fixture(autouse=True)
def _reset_probe_caches():
    """Reset the per-class probe caches between tests.

    Each client caches its ``--help`` probe result on the class so it
    runs once per process. Tests set the cache directly to simulate
    old/new CLI versions, which would otherwise leak between tests
    and break later cases that expect a clean probe slate.
    """
    ClaudeCodeClient._effort_flag_probed = False
    ClaudeCodeClient._effort_flag_supported = False
    CodexClient._config_override_probed = False
    CodexClient._config_override_supported = False
    GeminiClient._flag_probed = False
    GeminiClient._approval_mode_flag_supported = False
    GeminiClient._output_format_flag_supported = False
    yield
    ClaudeCodeClient._effort_flag_probed = False
    ClaudeCodeClient._effort_flag_supported = False
    CodexClient._config_override_probed = False
    CodexClient._config_override_supported = False
    GeminiClient._flag_probed = False
    GeminiClient._approval_mode_flag_supported = False
    GeminiClient._output_format_flag_supported = False


def _mark_claude_effort_supported(supported: bool) -> None:
    """Skip the real probe by pre-setting the class cache."""
    ClaudeCodeClient._effort_flag_probed = True
    ClaudeCodeClient._effort_flag_supported = supported


def _mark_codex_config_override_supported(supported: bool) -> None:
    CodexClient._config_override_probed = True
    CodexClient._config_override_supported = supported


def _mark_gemini_flags_supported(approval_mode: bool, output_format: bool) -> None:
    GeminiClient._flag_probed = True
    GeminiClient._approval_mode_flag_supported = approval_mode
    GeminiClient._output_format_flag_supported = output_format


class _ResponseModel(BaseModel):
    quote: str
    feedback: str


def _raw_json_with_invalid_latex_escapes() -> str:
    return (
        '{"quote": "Equation uses '
        + "\\"
        + "left"
        + " and "
        + "\\"
        + "omega"
        + '.", "feedback": "Rewrite '
        + "\\"
        + "mathbb"
        + ' carefully."}'
    )


def test_complete_repairs_invalid_latex_backslashes(monkeypatch) -> None:
    """Single backslashes from verbatim LaTeX quotes should parse as literals."""
    client = CodexClient(codex_bin="codex")

    monkeypatch.setattr(
        client, "_run", lambda prompt, timeout=None: _raw_json_with_invalid_latex_escapes()
    )

    result = client.complete(
        messages=[{"role": "user", "content": "Return JSON only."}],
        response_model=_ResponseModel,
    )

    assert result.quote == r"Equation uses \left and \omega."
    assert result.feedback == r"Rewrite \mathbb carefully."


def test_complete_keeps_valid_json_escapes(monkeypatch) -> None:
    """Repair fallback must not corrupt already-valid JSON escapes."""
    client = CodexClient(codex_bin="codex")
    raw = r'{"quote": "tab\tvalue", "feedback": "line1\nline2"}'

    monkeypatch.setattr(client, "_run", lambda prompt, timeout=None: raw)

    result = client.complete(
        messages=[{"role": "user", "content": "Return JSON only."}],
        response_model=_ResponseModel,
    )

    assert result.quote == "tab\tvalue"
    assert result.feedback == "line1\nline2"


def test_codex_low_effort_avoids_minimal_mode() -> None:
    _mark_codex_config_override_supported(True)
    client = CodexClient(codex_bin="codex", codex_model="gpt-5.4-mini", effort="low")

    cmd = client._build_cmd()

    assert cmd[:4] == ["codex", "exec", "-m", "gpt-5.4-mini"]
    assert "model_reasoning_effort='low'" in cmd
    assert "minimal" not in " ".join(cmd)


def test_codex_high_effort_maps_directly_to_high() -> None:
    _mark_codex_config_override_supported(True)
    client = CodexClient(codex_bin="codex", codex_model="gpt-5.4-mini", effort="high")

    cmd = client._build_cmd()

    assert "model_reasoning_effort='high'" in cmd


def test_codex_medium_effort_maps_directly_to_medium() -> None:
    _mark_codex_config_override_supported(True)
    client = CodexClient(codex_bin="codex", codex_model="gpt-5.4-mini", effort="medium")

    cmd = client._build_cmd()

    assert "model_reasoning_effort='medium'" in cmd


def test_codex_max_effort_caps_at_high() -> None:
    _mark_codex_config_override_supported(True)
    client = CodexClient(codex_bin="codex", codex_model="gpt-5.4-mini", effort="max")

    cmd = client._build_cmd()

    assert "model_reasoning_effort='high'" in cmd


def test_codex_old_version_drops_config_override_and_injects_text() -> None:
    """Old Codex versions without ``-c KEY=VALUE`` get text-level effort."""
    _mark_codex_config_override_supported(False)
    client = CodexClient(codex_bin="codex", codex_model="gpt-5.4-mini", effort="high")

    cmd = client._build_cmd()
    prompt = client._prepare_prompt("[USER]\nReview.")

    # No -c flag in cmd.
    assert "-c" not in cmd
    assert not any("model_reasoning_effort" in part for part in cmd)
    # Text injection instead.
    assert "Reasoning effort: high." in prompt
    assert prompt.endswith("[USER]\nReview.")


def test_claude_effort_passes_through_unchanged() -> None:
    _mark_claude_effort_supported(True)
    client = ClaudeCodeClient(claude_bin="claude", claude_model="claude-opus-4-6", effort="max")

    cmd = client._build_cmd()

    assert cmd == [
        "claude",
        "-p",
        "--model",
        "claude-opus-4-6",
        "--output-format",
        "text",
        "--effort",
        "max",
    ]


def test_claude_old_version_drops_effort_flag_and_injects_text() -> None:
    """Old Claude Code versions without ``--effort`` get text-level
    effort guidance injected into the prompt instead.

    This is the Florian-v1.3.0-preview bug: pre-``--effort`` Claude
    Code versions die with ``error: unknown option '--effort'`` on
    every pipeline stage and produce no review.
    """
    _mark_claude_effort_supported(False)
    client = ClaudeCodeClient(claude_bin="claude", claude_model="claude-opus-4-6", effort="max")

    cmd = client._build_cmd()
    prompt = client._prepare_prompt("[USER]\nReview.")

    # Cmd must NOT contain --effort at all, so old claude doesn't choke.
    assert "--effort" not in cmd
    assert cmd == [
        "claude",
        "-p",
        "--model",
        "claude-opus-4-6",
        "--output-format",
        "text",
    ]
    # Text-level guidance instead.
    assert "Reasoning effort: max." in prompt
    assert "deepest" in prompt
    assert prompt.endswith("[USER]\nReview.")


def test_claude_probe_caches_result_across_instances() -> None:
    """Two clients in the same process share the probe result so
    ``--help`` only runs once per process.
    """
    _mark_claude_effort_supported(False)
    first = ClaudeCodeClient(claude_bin="claude")
    second = ClaudeCodeClient(claude_bin="claude")

    assert "--effort" not in first._build_cmd()
    assert "--effort" not in second._build_cmd()
    # The probe cache persists on the class, not the instance.
    assert ClaudeCodeClient._effort_flag_probed is True


def test_gemini_effort_injects_advisory_prompt_budget() -> None:
    _mark_gemini_flags_supported(approval_mode=True, output_format=True)
    client = GeminiClient(gemini_bin="gemini", gemini_model="gemini-3.1-pro-preview", effort="max")

    prompt = client._prepare_prompt("[USER]\nReview this section.")

    assert "Reasoning effort: max." in prompt
    assert "32768-token thinking budget" in prompt
    assert prompt.endswith("[USER]\nReview this section.")


def test_gemini_new_version_uses_approval_mode_and_output_format() -> None:
    _mark_gemini_flags_supported(approval_mode=True, output_format=True)
    client = GeminiClient(gemini_bin="gemini", gemini_model="gemini-3.1-pro-preview", effort="high")

    cmd = client._build_cmd()

    assert cmd[:5] == ["gemini", "--approval-mode", "yolo", "--output-format", "text"]
    assert "--model" in cmd
    assert "--yolo" not in cmd


def test_gemini_old_version_falls_back_to_legacy_yolo_flag() -> None:
    """Old Gemini CLI without --approval-mode uses the legacy
    ``--yolo`` toggle and drops --output-format entirely."""
    _mark_gemini_flags_supported(approval_mode=False, output_format=False)
    client = GeminiClient(gemini_bin="gemini", gemini_model="gemini-3.1-pro-preview", effort="high")

    cmd = client._build_cmd()

    assert cmd == ["gemini", "--yolo", "--model", "gemini-3.1-pro-preview"]
    assert "--approval-mode" not in cmd
    assert "--output-format" not in cmd


def test_gemini_mixed_version_uses_new_approval_but_no_output_format() -> None:
    """Some intermediate Gemini CLI versions have --approval-mode but
    not --output-format. Pick each flag independently based on the
    probe, not in a lockstep all-or-nothing.
    """
    _mark_gemini_flags_supported(approval_mode=True, output_format=False)
    client = GeminiClient(gemini_bin="gemini", gemini_model="gemini-3.1-pro-preview", effort="high")

    cmd = client._build_cmd()

    assert "--approval-mode" in cmd
    assert "yolo" in cmd
    assert "--output-format" not in cmd
    assert "--yolo" not in cmd


def test_clean_subprocess_env_strips_anthropic_api_key(monkeypatch) -> None:
    """Critical billing guard: `claude -p` must not see ANTHROPIC_API_KEY.

    If the launching shell has ANTHROPIC_API_KEY set, Claude Code's
    documented behavior is to bill the API key instead of the
    subscription. That silently turns every call in a subscription
    handoff into a pay-per-token API charge on the user's Anthropic
    account — the exact failure mode reported against this repo.

    The subprocess env must not contain ANTHROPIC_API_KEY (or the
    alternate ANTHROPIC_AUTH_TOKEN) when we spawn `claude -p`.
    """
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-secret-do-not-forward")
    monkeypatch.setenv("ANTHROPIC_AUTH_TOKEN", "alt-billing-token")

    env = _clean_subprocess_env()

    assert "ANTHROPIC_API_KEY" not in env, (
        "ANTHROPIC_API_KEY must be stripped from the subprocess env so "
        "`claude -p` falls back to subscription OAuth billing instead of "
        "the API key."
    )
    assert "ANTHROPIC_AUTH_TOKEN" not in env


def test_clean_subprocess_env_strips_codex_and_gemini_billing_keys(monkeypatch) -> None:
    """Symmetric billing guard for Codex (OPENAI_API_KEY) and Gemini
    (GOOGLE_API_KEY / GEMINI_API_KEY). The subscription handoff exists
    specifically to bill the user's CLI subscription, not their
    pay-per-token provider API account.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-secret")
    monkeypatch.setenv("GOOGLE_API_KEY", "AIza-google-secret")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-secret")

    env = _clean_subprocess_env()

    assert "OPENAI_API_KEY" not in env
    assert "GOOGLE_API_KEY" not in env
    assert "GEMINI_API_KEY" not in env


def test_clean_subprocess_env_preserves_openrouter_key(monkeypatch) -> None:
    """OPENROUTER_API_KEY stays in the subprocess env.

    The parent Python process uses it for extraction and literature
    search (OpenRouter-backed, paid, documented). The subprocess is
    `claude -p` / `codex` / `gemini` and never uses it, but there is
    also no harm in leaving it visible — stripping it would break
    the common developer pattern of a single OPENROUTER_API_KEY in
    `~/.coarse/config.toml` driving every coarse code path.
    """
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-keep-this")

    env = _clean_subprocess_env()

    assert env.get("OPENROUTER_API_KEY") == "sk-or-v1-keep-this"


def test_subscription_billing_keys_list_includes_all_three_hosts() -> None:
    """Drift guard: adding a new host CLI should add the billing key
    to `_SUBSCRIPTION_BILLING_KEYS`. Pin the current set so a
    refactor can't silently drop one and re-introduce the billing
    redirect bug.
    """
    assert "ANTHROPIC_API_KEY" in _SUBSCRIPTION_BILLING_KEYS
    assert "ANTHROPIC_AUTH_TOKEN" in _SUBSCRIPTION_BILLING_KEYS
    assert "OPENAI_API_KEY" in _SUBSCRIPTION_BILLING_KEYS
    assert "GOOGLE_API_KEY" in _SUBSCRIPTION_BILLING_KEYS
    assert "GEMINI_API_KEY" in _SUBSCRIPTION_BILLING_KEYS


# ─────────────────────────────────────────────────────────────────
# Commit 1 fixes: UTF-8, missing binary, auth detection
# ─────────────────────────────────────────────────────────────────


def test_run_decodes_utf8_subprocess_output_without_crashing() -> None:
    """Windows non-UTF-8 locale regression: academic papers contain
    Greek letters, math symbols, and em-dashes. Without explicit
    `encoding="utf-8"` in subprocess.run, Python decodes stdout with
    `locale.getpreferredencoding(False)` which is cp1252 on default
    Windows and crashes on any non-ASCII byte. This test verifies
    the _run path passes those characters through cleanly.
    """
    _mark_claude_effort_supported(True)
    client = ClaudeCodeClient(claude_bin="claude")

    unicode_stdout = "Section review: uses λ, ∫, and — in theorem 3. 🎓"
    fake_proc = MagicMock()
    fake_proc.returncode = 0
    fake_proc.stdout = unicode_stdout
    fake_proc.stderr = ""

    with patch("coarse.headless_clients.subprocess.run", return_value=fake_proc) as mock_run:
        result = client._run("some prompt with ∂ and π")

    assert result == unicode_stdout
    # The subprocess.run call must pass encoding="utf-8" so Windows
    # non-UTF-8 locales don't crash here.
    kwargs = mock_run.call_args.kwargs
    assert kwargs.get("encoding") == "utf-8"
    assert kwargs.get("errors") == "replace"


def test_clean_subprocess_env_forces_utf8_locale_on_unix(monkeypatch) -> None:
    """Force `LANG=C.UTF-8` / `LC_ALL=C.UTF-8` (or en_US.UTF-8 on
    macOS) so Node-based child CLIs write UTF-8 to stdout regardless
    of the user's shell locale. On Windows this is a no-op.
    """
    monkeypatch.delenv("LANG", raising=False)
    monkeypatch.delenv("LC_ALL", raising=False)

    env = _clean_subprocess_env()

    import os as _os

    if _os.name == "nt":
        # Windows path — Node picks up the console codepage, so we
        # don't need to set these. Just verify we don't crash.
        pytest.skip("LANG/LC_ALL forcing is Unix-only")
    assert "UTF-8" in env.get("LANG", "")
    assert "UTF-8" in env.get("LC_ALL", "")


def test_clean_subprocess_env_preserves_caller_lang_override(monkeypatch) -> None:
    """Don't stomp on a LANG the user deliberately set. Our default
    only kicks in when LANG is unset."""
    monkeypatch.setenv("LANG", "fr_FR.UTF-8")
    monkeypatch.delenv("LC_ALL", raising=False)

    env = _clean_subprocess_env()

    import os as _os

    if _os.name == "nt":
        pytest.skip("LANG/LC_ALL forcing is Unix-only")
    assert env["LANG"] == "fr_FR.UTF-8"


def test_run_raises_friendly_error_when_claude_binary_missing() -> None:
    """If `claude` isn't on PATH, subprocess.run raises
    FileNotFoundError. Users should see an install hint, not an
    opaque traceback buried 10 pipeline stages deep.
    """
    _mark_claude_effort_supported(True)
    client = ClaudeCodeClient(claude_bin="claude")

    with patch(
        "coarse.headless_clients.subprocess.run",
        side_effect=FileNotFoundError(2, "No such file or directory", "claude"),
    ):
        with pytest.raises(RuntimeError, match="claude -p binary not found"):
            client._run("any prompt")


def test_run_missing_binary_error_includes_install_hint() -> None:
    """The error must name the install command so users can fix it
    without grepping the docs."""
    _mark_claude_effort_supported(True)
    client = ClaudeCodeClient(claude_bin="claude")

    with patch(
        "coarse.headless_clients.subprocess.run",
        side_effect=FileNotFoundError(2, "No such file or directory", "claude"),
    ):
        try:
            client._run("any prompt")
        except RuntimeError as exc:
            assert "npm install -g @anthropic-ai/claude-code" in str(exc)
        else:
            pytest.fail("RuntimeError not raised")


def test_run_missing_binary_error_is_per_host() -> None:
    """Each client returns the right install hint — codex points at
    @openai/codex, gemini at @google/gemini-cli."""
    _mark_codex_config_override_supported(True)
    _mark_gemini_flags_supported(approval_mode=True, output_format=True)

    codex = CodexClient(codex_bin="codex")
    gemini = GeminiClient(gemini_bin="gemini")

    with patch(
        "coarse.headless_clients.subprocess.run",
        side_effect=FileNotFoundError(2, "missing", "codex"),
    ):
        try:
            codex._run("x")
        except RuntimeError as exc:
            assert "@openai/codex" in str(exc)

    with patch(
        "coarse.headless_clients.subprocess.run",
        side_effect=FileNotFoundError(2, "missing", "gemini"),
    ):
        try:
            gemini._run("x")
        except RuntimeError as exc:
            assert "@google/gemini-cli" in str(exc)


def test_run_detects_auth_expiry_from_stderr() -> None:
    """When `claude -p` exits non-zero with 'not authenticated' in
    stderr, the wrapper prepends a friendly 'Run claude login'
    message instead of surfacing the raw exit code."""
    _mark_claude_effort_supported(True)
    client = ClaudeCodeClient(claude_bin="claude")

    fake_proc = MagicMock()
    fake_proc.returncode = 1
    fake_proc.stdout = ""
    fake_proc.stderr = "Error: not authenticated. Please log in with `claude login`."

    with patch("coarse.headless_clients.subprocess.run", return_value=fake_proc):
        with pytest.raises(RuntimeError) as excinfo:
            client._run("any prompt")

    msg = str(excinfo.value)
    assert "auth failure" in msg
    assert "claude login" in msg
    # Raw stderr should still be included for debugging.
    assert "not authenticated" in msg


def test_classify_cli_error_recognizes_common_auth_patterns() -> None:
    """The classifier is substring-based, not regex — loose matching
    tolerates version drift in stderr formatting."""
    assert _classify_cli_error("Error: not authenticated") is not None
    assert _classify_cli_error("unauthorized request") is not None
    assert _classify_cli_error("Session expired. Please log in again.") is not None
    assert _classify_cli_error("Run `codex login` to continue") is not None
    assert _classify_cli_error("gemini auth required") is not None
    # False-positive guard: don't match arbitrary errors.
    assert _classify_cli_error("ENOENT: file not found") is None
    assert _classify_cli_error("") is None
    assert _classify_cli_error("rate limit exceeded") is None


def test_run_preserves_generic_errors_without_auth_hint() -> None:
    """Non-auth failures fall through to the normal RuntimeError
    path — no spurious 'Run login' hint."""
    _mark_claude_effort_supported(True)
    client = ClaudeCodeClient(claude_bin="claude")

    fake_proc = MagicMock()
    fake_proc.returncode = 2
    fake_proc.stdout = ""
    fake_proc.stderr = "Syntax error in prompt template"

    with patch("coarse.headless_clients.subprocess.run", return_value=fake_proc):
        with pytest.raises(RuntimeError) as excinfo:
            client._run("any")

    msg = str(excinfo.value)
    assert "exited 2" in msg
    assert "Syntax error" in msg
    # No auth hint should be injected.
    assert "login" not in msg.lower()


# ─────────────────────────────────────────────────────────────────
# Commit 2: retry loop, model fallback, semaphore, transient
# ─────────────────────────────────────────────────────────────────


def _make_fake_proc(returncode: int, stdout: str = "", stderr: str = ""):
    p = MagicMock()
    p.returncode = returncode
    p.stdout = stdout
    p.stderr = stderr
    return p


def test_classify_transient_error_recognizes_rate_limits() -> None:
    from coarse.headless_clients import _is_transient_cli_error

    assert _is_transient_cli_error("Error: rate limit exceeded", 1) is True
    assert _is_transient_cli_error("429 Too Many Requests", 1) is True
    assert _is_transient_cli_error("503 Service Unavailable", 1) is True
    assert _is_transient_cli_error("connection reset by peer", 1) is True
    assert _is_transient_cli_error("please try again later", 1) is True
    # GNU timeout(1) exit code, no stderr.
    assert _is_transient_cli_error("", 124) is True


def test_classify_transient_error_rejects_permanent() -> None:
    from coarse.headless_clients import _is_transient_cli_error

    assert _is_transient_cli_error("Syntax error in prompt", 1) is False
    assert _is_transient_cli_error("Unknown argument: --effort", 2) is False
    assert _is_transient_cli_error("", 1) is False
    assert _is_transient_cli_error("authentication failed", 1) is False


def test_classify_unknown_model_error() -> None:
    from coarse.headless_clients import _is_unknown_model_error

    assert _is_unknown_model_error("Error: unknown model 'claude-opus-5-zeta'") is True
    assert _is_unknown_model_error("model not found: gpt-9") is True
    assert _is_unknown_model_error("Invalid model 'x'") is True
    assert _is_unknown_model_error("") is False
    assert _is_unknown_model_error("rate limit") is False


def test_run_retries_transient_failure_then_succeeds(monkeypatch) -> None:
    """First two calls return 429, third succeeds. _run should return
    the third call's stdout, not raise."""
    _mark_claude_effort_supported(True)
    # Zero out the backoff so the test runs fast.
    monkeypatch.setattr("coarse.headless_clients._RUN_BACKOFF_SECONDS", (0, 0))
    client = ClaudeCodeClient(claude_bin="claude")

    call_results = [
        _make_fake_proc(1, stderr="Error: 429 rate limit exceeded"),
        _make_fake_proc(1, stderr="Error: 503 Service Unavailable"),
        _make_fake_proc(0, stdout="final success"),
    ]
    with patch(
        "coarse.headless_clients.subprocess.run",
        side_effect=call_results,
    ) as mock_run:
        result = client._run("prompt")

    assert result == "final success"
    assert mock_run.call_count == 3


def test_run_exhausts_retry_on_persistent_rate_limit(monkeypatch) -> None:
    """All three attempts return 429. _run should raise with the
    stderr from the last attempt."""
    _mark_claude_effort_supported(True)
    monkeypatch.setattr("coarse.headless_clients._RUN_BACKOFF_SECONDS", (0, 0))
    client = ClaudeCodeClient(claude_bin="claude")

    rate_limited = _make_fake_proc(1, stderr="429 rate limit")
    with patch(
        "coarse.headless_clients.subprocess.run",
        return_value=rate_limited,
    ) as mock_run:
        with pytest.raises(RuntimeError, match="exited 1"):
            client._run("prompt")

    assert mock_run.call_count == 3


def test_run_does_not_retry_permanent_failure(monkeypatch) -> None:
    """A syntax error in stderr is permanent — fail fast, no retry."""
    _mark_claude_effort_supported(True)
    monkeypatch.setattr("coarse.headless_clients._RUN_BACKOFF_SECONDS", (0, 0))
    client = ClaudeCodeClient(claude_bin="claude")

    syntax_error = _make_fake_proc(2, stderr="Error: invalid syntax in template")
    with patch(
        "coarse.headless_clients.subprocess.run",
        return_value=syntax_error,
    ) as mock_run:
        with pytest.raises(RuntimeError, match="exited 2"):
            client._run("prompt")

    assert mock_run.call_count == 1


def test_run_does_not_retry_auth_failure(monkeypatch) -> None:
    """Auth failures are permanent — user needs to log in, retrying
    won't help."""
    _mark_claude_effort_supported(True)
    monkeypatch.setattr("coarse.headless_clients._RUN_BACKOFF_SECONDS", (0, 0))
    client = ClaudeCodeClient(claude_bin="claude")

    auth_fail = _make_fake_proc(1, stderr="not authenticated — run `claude login`")
    with patch(
        "coarse.headless_clients.subprocess.run",
        return_value=auth_fail,
    ) as mock_run:
        with pytest.raises(RuntimeError, match="auth failure"):
            client._run("prompt")

    assert mock_run.call_count == 1


def test_run_falls_back_to_default_model_on_unknown_model(monkeypatch) -> None:
    """First call fails with 'unknown model', second call with the
    default model succeeds. _run swaps models and returns."""
    _mark_claude_effort_supported(True)
    monkeypatch.setattr("coarse.headless_clients._RUN_BACKOFF_SECONDS", (0, 0))

    from coarse.models import HEADLESS_DEFAULT_MODELS

    default = HEADLESS_DEFAULT_MODELS["claude"]
    client = ClaudeCodeClient(
        claude_bin="claude",
        claude_model="claude-opus-5-zeta-preview",  # non-existent
    )
    assert client._claude_model != default

    call_results = [
        _make_fake_proc(1, stderr="Error: unknown model 'claude-opus-5-zeta-preview'"),
        _make_fake_proc(0, stdout="ok with default"),
    ]
    with patch(
        "coarse.headless_clients.subprocess.run",
        side_effect=call_results,
    ):
        result = client._run("prompt")

    assert result == "ok with default"
    # Model was swapped to the class default.
    assert client._claude_model == default
    # The fallback flag is set so a second unknown-model error won't
    # loop.
    assert client._model_fallback_attempted is True


def test_run_fallback_does_not_burn_retry_slot(monkeypatch) -> None:
    """Unknown-model fallback must NOT consume a transient-retry slot.

    Sequence: user model hits unknown-model error → fall back to default
    model → default model hits a 429 → should still have 2 retries
    available (not 1, which was the bug before the while-loop rewrite).
    """
    _mark_claude_effort_supported(True)
    monkeypatch.setattr("coarse.headless_clients._RUN_BACKOFF_SECONDS", (0, 0))

    client = ClaudeCodeClient(
        claude_bin="claude",
        claude_model="claude-opus-5-zeta-preview",
    )

    call_results = [
        # 1. user model → unknown model → fallback (no attempt consumed)
        _make_fake_proc(1, stderr="Error: unknown model 'claude-opus-5-zeta-preview'"),
        # 2. default model, attempt 1 → 429 transient → retry
        _make_fake_proc(1, stderr="429 rate limit exceeded"),
        # 3. default model, attempt 2 → 503 transient → retry
        _make_fake_proc(1, stderr="503 service unavailable"),
        # 4. default model, attempt 3 → success
        _make_fake_proc(0, stdout="final ok"),
    ]
    with patch(
        "coarse.headless_clients.subprocess.run",
        side_effect=call_results,
    ) as mock_run:
        result = client._run("prompt")

    assert result == "final ok"
    # Should be exactly 4 subprocess calls: 1 fallback-trigger + 3
    # full retries on the default model.
    assert mock_run.call_count == 4


def test_run_terminal_error_mentions_original_user_model(monkeypatch) -> None:
    """When fallback is triggered and the default model also fails
    permanently, the raised RuntimeError must name the user's
    originally-selected model so they know which one was rejected."""
    _mark_claude_effort_supported(True)
    monkeypatch.setattr("coarse.headless_clients._RUN_BACKOFF_SECONDS", (0, 0))

    client = ClaudeCodeClient(
        claude_bin="claude",
        claude_model="claude-opus-5-zeta-preview",
    )

    call_results = [
        _make_fake_proc(1, stderr="Error: unknown model 'claude-opus-5-zeta-preview'"),
        _make_fake_proc(2, stderr="Error: some permanent failure on the default model"),
    ]
    with patch(
        "coarse.headless_clients.subprocess.run",
        side_effect=call_results,
    ):
        with pytest.raises(RuntimeError) as excinfo:
            client._run("prompt")

    msg = str(excinfo.value)
    assert "some permanent failure" in msg
    assert "claude-opus-5-zeta-preview" in msg
    assert "user-selected model" in msg


def test_run_only_falls_back_to_default_model_once(monkeypatch) -> None:
    """Both the user model AND the default fail. No infinite loop —
    the fallback triggers once, then the loop treats the second
    unknown-model error as permanent."""
    _mark_claude_effort_supported(True)
    monkeypatch.setattr("coarse.headless_clients._RUN_BACKOFF_SECONDS", (0, 0))

    client = ClaudeCodeClient(claude_bin="claude", claude_model="broken-user-pick")

    persistent_unknown = _make_fake_proc(1, stderr="unknown model")
    with patch(
        "coarse.headless_clients.subprocess.run",
        return_value=persistent_unknown,
    ) as mock_run:
        with pytest.raises(RuntimeError):
            client._run("prompt")

    # At most: first attempt (unknown model, fallback triggered) +
    # second attempt (unknown model, no more fallback, fails).
    # Third would happen only if the classifier treated "unknown
    # model" as transient — verify it doesn't.
    assert mock_run.call_count == 2


def test_codex_model_fallback_noop_when_no_user_model(monkeypatch) -> None:
    """If codex_model=None we're already using codex's built-in
    default — nothing to fall back to, so don't try."""
    _mark_codex_config_override_supported(True)
    client = CodexClient(codex_bin="codex")  # codex_model defaults to None
    assert client._can_fall_back_to_default_model() is False


def test_gemini_model_fallback_noop_when_no_user_model(monkeypatch) -> None:
    _mark_gemini_flags_supported(approval_mode=True, output_format=True)
    client = GeminiClient(gemini_bin="gemini")  # gemini_model defaults to None
    assert client._can_fall_back_to_default_model() is False


def test_parse_concurrency_env_defaults_on_missing(monkeypatch) -> None:
    from coarse.headless_clients import _CONCURRENCY_DEFAULT, _parse_concurrency_env

    monkeypatch.delenv("COARSE_HEADLESS_CONCURRENCY", raising=False)
    assert _parse_concurrency_env() == _CONCURRENCY_DEFAULT


def test_parse_concurrency_env_accepts_valid_override(monkeypatch) -> None:
    from coarse.headless_clients import _parse_concurrency_env

    monkeypatch.setenv("COARSE_HEADLESS_CONCURRENCY", "7")
    assert _parse_concurrency_env() == 7


def test_parse_concurrency_env_rejects_invalid_and_oor(monkeypatch) -> None:
    from coarse.headless_clients import _CONCURRENCY_DEFAULT, _parse_concurrency_env

    monkeypatch.setenv("COARSE_HEADLESS_CONCURRENCY", "not-an-int")
    assert _parse_concurrency_env() == _CONCURRENCY_DEFAULT

    monkeypatch.setenv("COARSE_HEADLESS_CONCURRENCY", "0")
    assert _parse_concurrency_env() == _CONCURRENCY_DEFAULT

    monkeypatch.setenv("COARSE_HEADLESS_CONCURRENCY", "999")
    assert _parse_concurrency_env() == _CONCURRENCY_DEFAULT


def test_semaphore_caps_concurrent_subprocesses(monkeypatch) -> None:
    """Verify the per-class semaphore actually limits parallelism.
    Spawn more concurrent _run calls than the limit and confirm that
    at any moment, no more than `limit` are inside subprocess.run.
    """
    import threading as _threading

    _mark_claude_effort_supported(True)
    monkeypatch.setenv("COARSE_HEADLESS_CONCURRENCY", "2")
    # Reset any cached semaphore on the class so the env var takes effect.
    if "_semaphore" in ClaudeCodeClient.__dict__:
        del ClaudeCodeClient._semaphore

    active = 0
    max_active = 0
    lock = _threading.Lock()
    gate = _threading.Event()

    def fake_run(*args, **kwargs):
        nonlocal active, max_active
        with lock:
            active += 1
            max_active = max(max_active, active)
        # Hold the subprocess "running" until the gate is tripped so
        # multiple threads stack inside at once.
        gate.wait(timeout=1)
        with lock:
            active -= 1
        return _make_fake_proc(0, stdout="ok")

    with patch("coarse.headless_clients.subprocess.run", side_effect=fake_run):
        client = ClaudeCodeClient(claude_bin="claude")
        threads = [_threading.Thread(target=lambda: client._run("p")) for _ in range(5)]
        for t in threads:
            t.start()
        # Let the first batch land inside subprocess.run.
        import time as _time

        _time.sleep(0.05)
        gate.set()
        for t in threads:
            t.join(timeout=3)

    assert max_active <= 2, f"semaphore did not cap concurrency: saw {max_active}"

    # Cleanup: drop the class-level semaphore so subsequent tests get
    # a fresh one with whatever COARSE_HEADLESS_CONCURRENCY they set.
    if "_semaphore" in ClaudeCodeClient.__dict__:
        del ClaudeCodeClient._semaphore


def test_run_handles_large_prompt_stdin() -> None:
    """500 KB prompts (realistic for big papers) round-trip through
    _run without hanging or truncation."""
    _mark_claude_effort_supported(True)
    client = ClaudeCodeClient(claude_bin="claude")

    large_prompt = "X" * (500 * 1024)
    received_inputs: list[str] = []

    def fake_run(cmd, **kwargs):
        received_inputs.append(kwargs.get("input", ""))
        return _make_fake_proc(0, stdout="ok")

    with patch("coarse.headless_clients.subprocess.run", side_effect=fake_run):
        result = client._run(large_prompt)

    assert result == "ok"
    assert len(received_inputs) == 1
    assert len(received_inputs[0]) == len(large_prompt)
