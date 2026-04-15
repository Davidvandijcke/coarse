"""Regression tests for headless CLI-backed JSON parsing."""

from __future__ import annotations

import pytest
from pydantic import BaseModel

from coarse.headless_clients import (
    _SUBSCRIPTION_BILLING_KEYS,
    ClaudeCodeClient,
    CodexClient,
    GeminiClient,
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
