"""Tests for coarse.models — model manifest invariants."""

import pytest

from coarse.models import (
    CHEAP_MODELS,
    DEFAULT_MODEL,
    JSON_MODE_PREFIXES,
    MARKDOWN_JSON_PREFIXES,
    OCR_MODEL,
    QUALITY_MODEL,
    REASONING_EFFORT_DEFAULT,
    REASONING_MAX_TOKENS_MULTIPLIER,
    REASONING_MODEL_PREFIXES,
    REASONING_MODEL_SUBSTRINGS,
    VISION_MODEL,
    is_reasoning_model,
)


def test_default_model_has_provider_prefix():
    assert "/" in DEFAULT_MODEL


def test_all_models_have_provider_prefix():
    for name, model_id in [
        ("VISION_MODEL", VISION_MODEL),
        ("OCR_MODEL", OCR_MODEL),
        ("QUALITY_MODEL", QUALITY_MODEL),
    ]:
        assert "/" in model_id, f"{name} missing provider prefix: {model_id}"


def test_cheap_models_have_provider_prefix():
    for env_var, model_id in CHEAP_MODELS.items():
        assert "/" in model_id, f"CHEAP_MODELS[{env_var}] missing prefix: {model_id}"


def test_json_and_markdown_prefixes_no_overlap():
    overlap = set(JSON_MODE_PREFIXES) & set(MARKDOWN_JSON_PREFIXES)
    assert not overlap, f"Overlap between JSON and MD_JSON prefixes: {overlap}"


def test_all_prefixes_are_lowercase():
    for p in JSON_MODE_PREFIXES:
        assert p == p.lower(), f"JSON prefix not lowercase: {p}"
    for p in MARKDOWN_JSON_PREFIXES:
        assert p == p.lower(), f"MD_JSON prefix not lowercase: {p}"


# ---------------------------------------------------------------------------
# is_reasoning_model detection matrix
# ---------------------------------------------------------------------------


REASONING_POSITIVE_CASES = [
    # OpenAI o-series
    "openai/o1",
    "openai/o1-pro",
    "openai/o3",
    "openai/o3-mini",
    "openai/o3-mini-high",
    "openai/o3-pro",
    "openai/o3-deep-research",
    "openai/o4-mini-deep-research",
    # OpenAI GPT-5 Pro family (the actual failure from review 3ee351e6)
    "openai/gpt-5-pro",
    "openai/gpt-5.2-pro",
    "openai/gpt-5.4-pro",
    # DeepSeek R-series
    "deepseek/deepseek-r1",
    "deepseek/deepseek-r1-0528",
    "deepseek/deepseek-r1-distill-qwen-32b",
    # xAI Grok 4 + Grok 3 mini (both reason by default)
    "x-ai/grok-4",
    "x-ai/grok-4.20",
    "x-ai/grok-4.20-multi-agent",
    "x-ai/grok-3-mini",
    "x-ai/grok-3-mini-beta",
    # Qwen thinking
    "qwen/qwen3-max-thinking",
    "qwen/qwen3-vl-235b-a22b-thinking",
    "qwen/qwen-plus-2025-07-28:thinking",
    # Moonshot thinking
    "moonshotai/kimi-k2-thinking",
    # Baidu, Liquid, Arcee
    "baidu/ernie-4.5-21b-a3b-thinking",
    "liquid/lfm-2.5-1.2b-thinking:free",
    "arcee-ai/trinity-large-thinking",
    "arcee-ai/maestro-reasoning",
    # Anthropic explicit thinking variant
    "anthropic/claude-3.7-sonnet:thinking",
    # Perplexity reasoning
    "perplexity/sonar-reasoning-pro",
    # OpenRouter-prefixed variants still get detected
    "openrouter/openai/gpt-5.4-pro",
    "openrouter/openai/o3",
    "openrouter/deepseek/deepseek-r1",
    # Case-insensitive
    "OPENAI/GPT-5.4-PRO",
]


REASONING_NEGATIVE_CASES = [
    # Regular (non-Pro, non-reasoning) OpenAI models
    "openai/gpt-5.4",
    "openai/gpt-5.4-mini",
    "openai/gpt-5.4-nano",
    "openai/gpt-5.1",
    "openai/gpt-5",
    "openai/gpt-4o",
    "openai/gpt-5.1-codex",
    "openai/gpt-5.1-codex-mini",
    # Claude 4-family without :thinking suffix (optional thinking, off by default)
    "anthropic/claude-opus-4.6",
    "anthropic/claude-sonnet-4.6",
    "anthropic/claude-haiku-4.5",
    "anthropic/claude-3.7-sonnet",  # non-thinking variant
    # Qwen/DeepSeek non-thinking
    "qwen/qwen3.5-plus-02-15",
    "deepseek/deepseek-v3.2",
    "deepseek/deepseek-chat",
    # Gemini (thinking is transparent, no reasoning_effort needed via litellm)
    "gemini/gemini-3-flash-preview",
    "google/gemini-2.5-pro",
    # Grok 3 non-mini (not a reasoning model)
    "x-ai/grok-3",
    "x-ai/grok-3-beta",
    # Mistral, Moonshot non-thinking
    "mistralai/mistral-large",
    "moonshotai/kimi-k2.5",
]


@pytest.mark.parametrize("model_id", REASONING_POSITIVE_CASES)
def test_is_reasoning_model_positive(model_id):
    assert is_reasoning_model(model_id), f"expected {model_id} to be reasoning"


@pytest.mark.parametrize("model_id", REASONING_NEGATIVE_CASES)
def test_is_reasoning_model_negative(model_id):
    assert not is_reasoning_model(model_id), f"expected {model_id} NOT to be reasoning"


def test_reasoning_prefixes_are_lowercase():
    for p in REASONING_MODEL_PREFIXES:
        assert p == p.lower(), f"reasoning prefix not lowercase: {p}"
    for s in REASONING_MODEL_SUBSTRINGS:
        assert s == s.lower(), f"reasoning substring not lowercase: {s}"


def test_reasoning_max_tokens_multiplier_sensible():
    """Calibrated for GPT-5.4 Pro burning ~15k reasoning on overview; an 8x
    multiplier on 8k default gives 64k headroom. Accept 4-16 as reasonable."""
    assert 4 <= REASONING_MAX_TOKENS_MULTIPLIER <= 16


def test_reasoning_effort_default_is_recognized_value():
    assert REASONING_EFFORT_DEFAULT in {"low", "medium", "high"}
