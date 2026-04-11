from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel, ValidationError

from coarse.config import CoarseConfig
from coarse.llm import (
    LLMClient,
    _inject_openrouter_privacy,
    _sanitized_completion,
    estimate_call_cost,
    estimate_reasoning_overhead_tokens,
    model_cost_per_token,
)
from coarse.models import REASONING_EFFORT_DEFAULT, REASONING_MAX_TOKENS_MULTIPLIER

TEST_MODEL = "test/mock-model"


class _SimpleModel(BaseModel):
    value: str


def _make_mock_completion():
    completion = MagicMock()
    completion.usage.prompt_tokens = 100
    completion.usage.completion_tokens = 50
    completion.model = "openai/gpt-4o"
    return completion


@pytest.fixture()
def mock_instructor_client():
    """Patch the instructor module used by LLMClient."""
    with patch("coarse.llm.instructor") as mock_instructor:
        mock_client = MagicMock()
        mock_instructor.from_litellm.return_value = mock_client
        yield mock_client


def test_complete_returns_parsed_model(mock_instructor_client):
    expected = _SimpleModel(value="hello")
    mock_completion = _make_mock_completion()
    mock_instructor_client.chat.completions.create_with_completion.return_value = (
        expected,
        mock_completion,
    )

    with patch("coarse.llm.litellm.completion_cost", return_value=0.001):
        client = LLMClient(model=TEST_MODEL, config=CoarseConfig())
        result = client.complete(
            messages=[{"role": "user", "content": "hello"}],
            response_model=_SimpleModel,
        )

    assert isinstance(result, _SimpleModel)
    assert result.value == "hello"


def test_cost_accumulates_across_calls(mock_instructor_client):
    model_instance = _SimpleModel(value="x")
    mock_completion = _make_mock_completion()
    mock_instructor_client.chat.completions.create_with_completion.return_value = (
        model_instance,
        mock_completion,
    )

    with patch("coarse.llm.litellm.completion_cost", return_value=0.005):
        client = LLMClient(model=TEST_MODEL, config=CoarseConfig())
        client.complete(messages=[{"role": "user", "content": "a"}], response_model=_SimpleModel)
        client.complete(messages=[{"role": "user", "content": "b"}], response_model=_SimpleModel)

    assert abs(client.cost_usd - 0.010) < 1e-9


def test_model_cost_per_token_known_model():
    in_cost, out_cost = model_cost_per_token("openai/gpt-4o")
    assert in_cost > 0
    assert out_cost > 0


def test_model_cost_per_token_unknown_model():
    result = model_cost_per_token("bogus/nonexistent-model-xyz-999")
    assert result == (0.0, 0.0)


def test_estimate_call_cost():
    in_cost, out_cost = model_cost_per_token("gpt-4o")
    expected = in_cost * 1000 + out_cost * 500
    result = estimate_call_cost("gpt-4o", 1000, 500)
    assert result > 0
    assert abs(result - expected) < 1e-12


def test_client_uses_config_model(mock_instructor_client):
    cfg = CoarseConfig(default_model="anthropic/claude-3-5-sonnet")
    client = LLMClient(config=cfg)
    assert client.model == "anthropic/claude-3-5-sonnet"


def test_openrouter_privacy_injected_for_openrouter_models():
    result = _inject_openrouter_privacy("openrouter/qwen/qwen3.5-plus", {})
    assert result["extra_body"]["provider"]["data_collection"] == "deny"


def test_openrouter_privacy_skipped_for_direct_provider_calls():
    # Direct Anthropic/OpenAI/Google calls — flag is OpenRouter-specific
    result = _inject_openrouter_privacy("anthropic/claude-sonnet-4.6", {"model": "x"})
    assert "extra_body" not in result


def test_openrouter_privacy_preserves_existing_provider_config():
    existing = {"extra_body": {"provider": {"order": ["Fireworks"]}}}
    result = _inject_openrouter_privacy("openrouter/foo/bar", existing)
    assert result["extra_body"]["provider"]["order"] == ["Fireworks"]
    assert result["extra_body"]["provider"]["data_collection"] == "deny"


def test_openrouter_privacy_respects_explicit_user_override():
    # If caller explicitly set data_collection, don't clobber it
    existing = {"extra_body": {"provider": {"data_collection": "allow"}}}
    result = _inject_openrouter_privacy("openrouter/foo/bar", existing)
    assert result["extra_body"]["provider"]["data_collection"] == "allow"


def test_openrouter_api_key_injected_from_env(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-test")
    result = _inject_openrouter_privacy("openrouter/anthropic/claude-sonnet-4.6", {})
    assert result["api_key"] == "sk-or-v1-test"


def test_openrouter_api_key_not_injected_without_env(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    result = _inject_openrouter_privacy("openrouter/qwen/qwen3.5-plus", {})
    assert "api_key" not in result


def test_openrouter_api_key_respects_caller_override(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-from-env")
    result = _inject_openrouter_privacy(
        "openrouter/qwen/qwen3.5-plus", {"api_key": "sk-or-v1-from-caller"}
    )
    assert result["api_key"] == "sk-or-v1-from-caller"


def test_openrouter_api_key_skipped_for_direct_provider_calls(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-test")
    result = _inject_openrouter_privacy("anthropic/claude-sonnet-4.6", {})
    assert "api_key" not in result


# ---------------------------------------------------------------------------
# Reasoning-model path
# ---------------------------------------------------------------------------


def _reasoning_client(model_id: str, mock_instructor_client) -> LLMClient:
    expected = _SimpleModel(value="ok")
    mock_completion = _make_mock_completion()
    mock_instructor_client.chat.completions.create_with_completion.return_value = (
        expected,
        mock_completion,
    )
    return LLMClient(model=model_id, config=CoarseConfig())


def test_is_reasoning_property_true_for_gpt5_pro(mock_instructor_client):
    client = _reasoning_client("openai/gpt-5.4-pro", mock_instructor_client)
    assert client.is_reasoning is True


def test_is_reasoning_property_false_for_regular_gpt5(mock_instructor_client):
    client = _reasoning_client("openai/gpt-5.4", mock_instructor_client)
    assert client.is_reasoning is False


def test_complete_bumps_max_tokens_for_reasoning_model(mock_instructor_client):
    """Regression for review 3ee351e6: GPT-5.4 Pro burned 15k reasoning tokens
    on the overview stage (max_tokens=8192) before emitting any output.
    The client must auto-bump to leave headroom for the reasoning phase."""
    client = _reasoning_client("openai/o3", mock_instructor_client)

    with patch("coarse.llm.litellm.completion_cost", return_value=0.0):
        client.complete(
            messages=[{"role": "user", "content": "x"}],
            response_model=_SimpleModel,
            max_tokens=8192,
        )

    call = mock_instructor_client.chat.completions.create_with_completion.call_args
    passed_max_tokens = call.kwargs["max_tokens"]
    # 8192 * 8 = 65536, but _clamp_max_tokens may cap. Either way, it
    # must be strictly larger than the nominal 8192 the caller asked for.
    assert passed_max_tokens >= 8192 * 2, (
        f"reasoning model did not get headroom: passed max_tokens={passed_max_tokens}"
    )


def test_complete_does_not_bump_max_tokens_for_non_reasoning(mock_instructor_client):
    client = _reasoning_client("openai/gpt-5.4", mock_instructor_client)

    with patch("coarse.llm.litellm.completion_cost", return_value=0.0):
        client.complete(
            messages=[{"role": "user", "content": "x"}],
            response_model=_SimpleModel,
            max_tokens=8192,
        )

    call = mock_instructor_client.chat.completions.create_with_completion.call_args
    # Non-reasoning models get the requested value (possibly clamped to
    # the model's real ceiling, but not bumped UP).
    assert call.kwargs["max_tokens"] <= 8192


def test_complete_passes_reasoning_effort_for_reasoning_model(mock_instructor_client):
    client = _reasoning_client("openai/gpt-5.4-pro", mock_instructor_client)

    with patch("coarse.llm.litellm.completion_cost", return_value=0.0):
        client.complete(
            messages=[{"role": "user", "content": "x"}],
            response_model=_SimpleModel,
        )

    call = mock_instructor_client.chat.completions.create_with_completion.call_args
    assert call.kwargs.get("reasoning_effort") == REASONING_EFFORT_DEFAULT


def test_complete_does_not_pass_reasoning_effort_for_regular_model(
    mock_instructor_client,
):
    client = _reasoning_client("openai/gpt-4o", mock_instructor_client)

    with patch("coarse.llm.litellm.completion_cost", return_value=0.0):
        client.complete(
            messages=[{"role": "user", "content": "x"}],
            response_model=_SimpleModel,
        )

    call = mock_instructor_client.chat.completions.create_with_completion.call_args
    assert "reasoning_effort" not in call.kwargs


def test_complete_respects_caller_reasoning_effort_override(mock_instructor_client):
    """If the caller explicitly passes reasoning_effort, don't clobber it."""
    client = _reasoning_client("openai/o3", mock_instructor_client)

    with patch("coarse.llm.litellm.completion_cost", return_value=0.0):
        client.complete(
            messages=[{"role": "user", "content": "x"}],
            response_model=_SimpleModel,
            reasoning_effort="high",
        )

    call = mock_instructor_client.chat.completions.create_with_completion.call_args
    assert call.kwargs["reasoning_effort"] == "high"


def test_complete_replaces_caller_none_reasoning_effort_with_default(
    mock_instructor_client,
):
    """A caller threading `reasoning_effort=None` (e.g. from a config that
    defaults to None) must NOT silently disable reasoning. The default kicks
    in for None; callers can disable by passing a real string like "low"."""
    client = _reasoning_client("openai/o3", mock_instructor_client)

    with patch("coarse.llm.litellm.completion_cost", return_value=0.0):
        client.complete(
            messages=[{"role": "user", "content": "x"}],
            response_model=_SimpleModel,
            reasoning_effort=None,
        )

    call = mock_instructor_client.chat.completions.create_with_completion.call_args
    assert call.kwargs["reasoning_effort"] == REASONING_EFFORT_DEFAULT


def test_complete_kimi_thinking_gets_both_reasoning_and_md_json_bumps(
    mock_instructor_client,
):
    """moonshotai/kimi-k2-thinking matches BOTH the reasoning path (via
    'thinking' substring) and the MD_JSON path (via 'moonshotai'/'kimi'
    prefix). A future refactor that reorders the two branches could
    regress silently. Pin the composition: the final max_tokens must
    respect the max of both bumps."""
    client = _reasoning_client("moonshotai/kimi-k2-thinking", mock_instructor_client)

    with patch("coarse.llm.litellm.completion_cost", return_value=0.0):
        client.complete(
            messages=[{"role": "user", "content": "x"}],
            response_model=_SimpleModel,
            max_tokens=2048,
        )

    call = mock_instructor_client.chat.completions.create_with_completion.call_args
    # Both bumps should have fired: reasoning 8x = 16384, MD_JSON floor = 16384.
    # The final value must be at least the larger of the two.
    assert call.kwargs["max_tokens"] >= 16384


def test_complete_reasoning_bump_respects_model_ceiling(mock_instructor_client):
    """The bumped value must still be clamped by _clamp_max_tokens to the
    model's registered ceiling. If a future _clamp_max_tokens change drops
    reasoning models, this test catches it."""
    client = _reasoning_client("openai/o3", mock_instructor_client)

    with patch("coarse.llm.litellm.completion_cost", return_value=0.0):
        client.complete(
            messages=[{"role": "user", "content": "x"}],
            response_model=_SimpleModel,
            max_tokens=200_000,  # deliberately above any reasonable ceiling
        )

    call = mock_instructor_client.chat.completions.create_with_completion.call_args
    # Must be clamped below what we asked for, but still well above the
    # nominal 200k (which would be > o3's real output window).
    assert call.kwargs["max_tokens"] < 200_000 * 8
    # And must be strictly larger than the caller's nominal request, proving
    # the bump ran before the clamp.
    assert call.kwargs["max_tokens"] > 0


def test_complete_reasoning_bump_for_unknown_reasoning_model(mock_instructor_client):
    """A reasoning model not in litellm's registry (e.g. brand-new thinking
    variant) should still get the 8x headroom rather than being capped to
    the 16k unknown-model fallback. Regression for the case where the
    headline fix was silently neutralized by _clamp_max_tokens."""
    # Fake model ID that matches REASONING_MODEL_SUBSTRINGS ("thinking")
    # but is NOT in litellm's cost registry.
    client = _reasoning_client("made-up-vendor/new-thinking-model-v1", mock_instructor_client)

    with patch("coarse.llm.litellm.completion_cost", return_value=0.0):
        client.complete(
            messages=[{"role": "user", "content": "x"}],
            response_model=_SimpleModel,
            max_tokens=8192,
        )

    call = mock_instructor_client.chat.completions.create_with_completion.call_args
    # Without the reasoning-aware unknown fallback, this would have been
    # clamped to 16384. With it, the 8x bump (65536) stays intact because
    # _UNKNOWN_REASONING_MODEL_CEILING is 65536.
    assert call.kwargs["max_tokens"] > 16384, (
        f"unknown reasoning model was clamped to {call.kwargs['max_tokens']}, "
        f"defeating the 8x multiplier"
    )


def test_reasoning_multiplier_applies_before_clamp(mock_instructor_client):
    """The multiplier bumps the caller's request; _clamp_max_tokens then
    enforces the model's real ceiling. This test pins the relationship by
    asserting that a small request is bumped by at least the multiplier
    (before clamping would have a chance to bite)."""
    client = _reasoning_client("openai/o3", mock_instructor_client)

    with patch("coarse.llm.litellm.completion_cost", return_value=0.0):
        client.complete(
            messages=[{"role": "user", "content": "x"}],
            response_model=_SimpleModel,
            max_tokens=256,  # small enough to stay well under any model ceiling
        )

    call = mock_instructor_client.chat.completions.create_with_completion.call_args
    assert call.kwargs["max_tokens"] == 256 * REASONING_MAX_TOKENS_MULTIPLIER


# ---------------------------------------------------------------------------
# Reasoning cost overhead
# ---------------------------------------------------------------------------


def test_litellm_drop_params_enabled_at_module_import():
    """Load-bearing for the 'silently drop reasoning_effort on providers
    that don't support it' strategy. If this gets disabled, Qwen thinking
    / DeepSeek R1 / Kimi thinking calls will error on the reasoning_effort
    kwarg at runtime."""
    import litellm

    import coarse.llm  # noqa: F401 — import triggers the module-level set

    assert litellm.drop_params is True


def test_reasoning_overhead_zero_for_regular_model():
    assert estimate_reasoning_overhead_tokens("openai/gpt-4o", 1500) == 0


def test_estimate_call_cost_unknown_reasoning_model_returns_zero():
    """For a reasoning model not in litellm's cost registry,
    model_cost_per_token returns (0, 0), so cost should be 0 even though
    the reasoning overhead multiplier fires. Documents the fallback."""
    cost = estimate_call_cost("made-up-vendor/new-thinking-model-v1", 1000, 500)
    assert cost == 0.0


def test_reasoning_overhead_nonzero_for_reasoning_model():
    overhead = estimate_reasoning_overhead_tokens("openai/gpt-5.4-pro", 1500)
    assert overhead > 0
    # Should be a few times the visible output, not 1x or 100x
    assert 1500 < overhead <= 1500 * 10


def test_estimate_call_cost_reasoning_is_more_expensive_than_regular():
    """Pin the contract: for the same visible token counts, a reasoning
    model's cost estimate must be strictly greater than the non-reasoning
    cost you'd get from the same pricing, because reasoning tokens bill
    at the output rate."""
    # Use a reasoning model that litellm knows the price of.
    reasoning_cost = estimate_call_cost("openai/o3", 1000, 500)
    # Compute what the cost would be WITHOUT the reasoning overhead by
    # calling model_cost_per_token directly.
    in_rate, out_rate = model_cost_per_token("openai/o3")
    naive_cost = in_rate * 1000 + out_rate * 500
    assert reasoning_cost > naive_cost, (
        f"reasoning cost {reasoning_cost} not larger than naive {naive_cost}; "
        f"the reasoning-overhead adjustment is missing"
    )
    # Sanity: the overhead should be meaningful (>20% uplift), not a rounding bump
    assert reasoning_cost >= naive_cost * 1.2


def _sanitizer_response_with(content: str):
    """Build a minimal litellm-style response object for _sanitized_completion."""
    msg = MagicMock()
    msg.content = content
    msg.reasoning_content = None
    choice = MagicMock()
    choice.message = msg
    response = MagicMock()
    response.choices = [choice]
    return response


def test_sanitized_completion_strips_literal_control_chars():
    """Literal \\x00-\\x1f (except tab/newline) in msg.content must be removed."""
    raw = "before\x00middle\x01tab\there\nnewlineOK\x1fend"
    response = _sanitizer_response_with(raw)

    with patch("coarse.llm.litellm.completion", return_value=response):
        result = _sanitized_completion(model="test/mock")

    cleaned = result.choices[0].message.content
    assert "\x00" not in cleaned
    assert "\x01" not in cleaned
    assert "\x1f" not in cleaned
    assert "\t" in cleaned  # tab preserved
    assert "\n" in cleaned  # newline preserved
    assert cleaned == "beforemiddletab\there\nnewlineOKend"


def test_sanitized_completion_strips_json_u0000_escape_before_parse():
    """Regression for production bug: gpt-5.4 emitted JSON with \\u0000 escape
    sequences inside string fields. _CTRL_CHAR_RE only matches literal control
    chars, so the 6-byte \\u0000 escape passed through untouched, and json.loads
    then reconstituted it as a real \\x00 inside the parsed Pydantic field.
    That NUL byte then crashed the Supabase write with Postgres 22P05.

    The fix strips the escape form before Instructor/Pydantic sees the content.
    """
    import json

    # Six printable ASCII bytes, NOT a literal NUL. Must use a raw-ish build
    # so Python's string literal parser doesn't fold \u0000 into \x00.
    raw_json = '{"quote": "text ' + "\\u0000" + ' more", "keep": "tab\\tend"}'
    # Sanity-check the test fixture itself:
    assert "\x00" not in raw_json  # no literal NUL yet
    assert "\\u0000" in raw_json  # escape sequence is present as 6 chars

    response = _sanitizer_response_with(raw_json)
    with patch("coarse.llm.litellm.completion", return_value=response):
        result = _sanitized_completion(model="test/mock")

    cleaned = result.choices[0].message.content
    parsed = json.loads(cleaned)

    # The fix: no \x00 should survive the json.loads round-trip.
    assert "\x00" not in parsed["quote"], f"NUL byte leaked into parsed field: {parsed['quote']!r}"
    assert parsed["quote"] == "text  more"  # space preserved either side
    # Legit escape sequences (\t) must still round-trip correctly.
    assert parsed["keep"] == "tab\tend"


def test_sanitized_completion_strips_multiple_u0000_escapes():
    """Pin global replacement: every \\u0000 occurrence must be stripped,
    not just the first. Guards against a future switch to `.replace(..., 1)`.
    """
    import json

    raw = '{"q": "a' + "\\u0000" + "b" + "\\u0000" + "c" + "\\u0000" + 'd"}'
    response = _sanitizer_response_with(raw)
    with patch("coarse.llm.litellm.completion", return_value=response):
        result = _sanitized_completion(model="test/mock")

    parsed = json.loads(result.choices[0].message.content)
    assert "\x00" not in parsed["q"]
    assert parsed["q"] == "abcd"


def test_sanitized_completion_handles_none_content():
    """The `isinstance(msg.content, str)` guard must no-op on None content
    without raising. Some providers (e.g. reasoning-only responses) return
    a message with content=None.
    """
    response = _sanitizer_response_with(None)
    with patch("coarse.llm.litellm.completion", return_value=response):
        result = _sanitized_completion(model="test/mock")
    assert result.choices[0].message.content is None


def test_complete_instructor_validation_error(mock_instructor_client):
    try:
        _SimpleModel()  # missing required 'value' field -> ValidationError
    except ValidationError as exc:
        mock_instructor_client.chat.completions.create_with_completion.side_effect = exc

    client = LLMClient(model=TEST_MODEL, config=CoarseConfig())
    with pytest.raises(ValidationError):
        client.complete(
            messages=[{"role": "user", "content": "bad"}],
            response_model=_SimpleModel,
        )
