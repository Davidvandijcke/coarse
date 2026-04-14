"""Regression tests for headless CLI-backed JSON parsing."""

from __future__ import annotations

from pydantic import BaseModel

from coarse.headless_clients import (
    _SUBSCRIPTION_BILLING_KEYS,
    ClaudeCodeClient,
    CodexClient,
    GeminiClient,
    _clean_subprocess_env,
)


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
    client = CodexClient(codex_bin="codex", codex_model="gpt-5.4-mini", effort="low")

    cmd = client._build_cmd()

    assert cmd[:4] == ["codex", "exec", "-m", "gpt-5.4-mini"]
    assert "model_reasoning_effort='low'" in cmd
    assert "minimal" not in " ".join(cmd)


def test_codex_high_effort_maps_directly_to_high() -> None:
    client = CodexClient(codex_bin="codex", codex_model="gpt-5.4-mini", effort="high")

    cmd = client._build_cmd()

    assert "model_reasoning_effort='high'" in cmd


def test_codex_medium_effort_maps_directly_to_medium() -> None:
    client = CodexClient(codex_bin="codex", codex_model="gpt-5.4-mini", effort="medium")

    cmd = client._build_cmd()

    assert "model_reasoning_effort='medium'" in cmd


def test_codex_max_effort_caps_at_high() -> None:
    client = CodexClient(codex_bin="codex", codex_model="gpt-5.4-mini", effort="max")

    cmd = client._build_cmd()

    assert "model_reasoning_effort='high'" in cmd


def test_claude_effort_passes_through_unchanged() -> None:
    client = ClaudeCodeClient(claude_bin="claude", claude_model="claude-opus-4-6", effort="max")

    cmd = client._build_cmd()

    assert cmd == [
        "claude",
        "-p",
        "--model",
        "claude-opus-4-6",
        "--effort",
        "max",
        "--output-format",
        "text",
    ]


def test_gemini_effort_injects_advisory_prompt_budget() -> None:
    client = GeminiClient(gemini_bin="gemini", gemini_model="gemini-3.1-pro-preview", effort="max")

    prompt = client._prepare_prompt("[USER]\nReview this section.")

    assert "Reasoning effort: max." in prompt
    assert "32768-token thinking budget" in prompt
    assert prompt.endswith("[USER]\nReview this section.")


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
