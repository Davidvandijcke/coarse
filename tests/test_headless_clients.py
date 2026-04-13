"""Regression tests for headless CLI-backed JSON parsing."""

from __future__ import annotations

from pydantic import BaseModel

from coarse.headless_clients import ClaudeCodeClient, CodexClient, GeminiClient


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
