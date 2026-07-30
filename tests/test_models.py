"""Tests for coarse.models — model manifest invariants."""

import re
from pathlib import Path

import pytest

from coarse.models import (
    _NON_REASONING_SUBSTRINGS,
    CHEAP_MODELS,
    CLAUDE_FABLE_5_MODEL,
    CLAUDE_OPUS_5_MODEL,
    CLAUDE_SONNET_5_MODEL,
    DEFAULT_MODEL,
    FUSION_INPUT_COST_PER_TOKEN,
    FUSION_MODEL,
    FUSION_OUTPUT_COST_PER_TOKEN,
    GEMINI_3_6_FLASH_MODEL,
    GPT_5_6_LUNA_MODEL,
    GPT_5_6_SOL_MODEL,
    GPT_5_6_TERRA_MODEL,
    GROK_4_5_MODEL,
    HEADLESS_DEFAULT_MODELS,
    JSON_MODE_PREFIXES,
    KIMI_K3_MODEL,
    MARKDOWN_JSON_PREFIXES,
    OCR_MODEL,
    OPENROUTER_NAMESPACE_MODELS,
    QUALITY_MODEL,
    QWEN_3_7_PLUS_MODEL,
    REASONING_EFFORT_DEFAULT,
    REASONING_MAX_TOKENS_MULTIPLIER,
    REASONING_MODEL_PREFIXES,
    REASONING_MODEL_SUBSTRINGS,
    TEMPERATURE_UNSUPPORTED_PREFIXES,
    VISION_MODEL,
    WEB_DEFAULT_MODEL,
    WEB_FEATURED_MODEL_IDS,
    is_reasoning_model,
    model_filename_slug,
    supports_temperature,
)


def test_default_model_has_provider_prefix():
    assert "/" in DEFAULT_MODEL


def test_current_frontier_model_manifest_is_canonical():
    """The runtime registry exposes provider-qualified current model IDs."""
    assert DEFAULT_MODEL == QWEN_3_7_PLUS_MODEL
    for model_id in (
        CLAUDE_FABLE_5_MODEL,
        CLAUDE_OPUS_5_MODEL,
        CLAUDE_SONNET_5_MODEL,
        GPT_5_6_SOL_MODEL,
        GPT_5_6_TERRA_MODEL,
        GPT_5_6_LUNA_MODEL,
        GEMINI_3_6_FLASH_MODEL,
        QWEN_3_7_PLUS_MODEL,
        KIMI_K3_MODEL,
        GROK_4_5_MODEL,
    ):
        assert "/" in model_id


def test_web_picker_tracks_canonical_featured_models_and_default():
    """Fail if the cross-language web picker drifts from the Python manifest."""
    picker_path = Path(__file__).resolve().parents[1] / "web/src/components/ModelPicker.tsx"
    picker = picker_path.read_text(encoding="utf-8")

    default_match = re.search(r'export const DEFAULT_REVIEW_MODEL\s*=\s*"([^"]+)";', picker)
    assert default_match, "DEFAULT_REVIEW_MODEL is missing from ModelPicker.tsx"
    web_default = default_match.group(1)

    models_match = re.search(
        r"const DEFAULT_MODELS:\s*DefaultModel\[\]\s*=\s*\[(.*?)\n\];",
        picker,
        flags=re.DOTALL,
    )
    assert models_match, "DEFAULT_MODELS is missing from ModelPicker.tsx"
    id_expressions = re.findall(r"\{\s*id:\s*([^,]+),", models_match.group(1))
    web_ids: list[str] = []
    for expression in id_expressions:
        expression = expression.strip()
        if expression == "DEFAULT_REVIEW_MODEL":
            web_ids.append(web_default)
            continue
        literal = re.fullmatch(r'"([^"]+)"', expression)
        assert literal, f"unsupported model ID expression in picker: {expression}"
        web_ids.append(literal.group(1))

    assert web_default == WEB_DEFAULT_MODEL
    assert tuple(web_ids) == WEB_FEATURED_MODEL_IDS


def test_headless_defaults_track_current_host_models():
    assert HEADLESS_DEFAULT_MODELS == {
        "claude": CLAUDE_OPUS_5_MODEL.removeprefix("anthropic/"),
        "codex": GPT_5_6_SOL_MODEL.removeprefix("openai/"),
        "gemini": GEMINI_3_6_FLASH_MODEL.removeprefix("google/"),
    }


def test_current_default_reasoning_models_get_hidden_token_headroom():
    for model_id in (
        CLAUDE_FABLE_5_MODEL,
        CLAUDE_OPUS_5_MODEL,
        CLAUDE_SONNET_5_MODEL,
        GEMINI_3_6_FLASH_MODEL,
        QWEN_3_7_PLUS_MODEL,
        KIMI_K3_MODEL,
    ):
        assert is_reasoning_model(model_id), model_id


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


def test_fusion_model_is_in_openrouter_namespace_set():
    # The double-prefix routing fix in llm._normalize_model keys off this set.
    assert FUSION_MODEL in OPENROUTER_NAMESPACE_MODELS


def test_openrouter_namespace_models_are_single_segment_openrouter_slugs():
    # These need doubling precisely because they are `openrouter/<model>` with
    # no further provider segment (which would already carry the routing prefix).
    for model_id in OPENROUTER_NAMESPACE_MODELS:
        assert model_id.startswith("openrouter/"), model_id
        assert model_id.count("/") == 1, model_id


def test_fusion_representative_pricing_is_positive():
    # OpenRouter reports dynamic (-1) pricing; these are the substitute rates
    # the cost estimators rely on, so they must be real positive numbers.
    assert FUSION_INPUT_COST_PER_TOKEN > 0
    assert FUSION_OUTPUT_COST_PER_TOKEN > 0


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
    "openai/o1-mini",
    "openai/o1-pro",
    "openai/o3",
    "openai/o3-mini",
    "openai/o3-mini-high",
    "openai/o3-pro",
    "openai/o3-deep-research",
    "openai/o4",
    "openai/o4-mini-deep-research",
    # OpenAI GPT-5 family — the entire family reasons except `-chat` variants
    # (verified OpenRouter 2026-05-29). The Pro variant is the original failure
    # from review 3ee351e6; the non-Pro / codex / mini / nano models are #185.
    "openai/gpt-5",
    "openai/gpt-5-mini",
    "openai/gpt-5-codex",
    "openai/gpt-5.1",
    "openai/gpt-5.1-codex",
    "openai/gpt-5.1-codex-mini",
    "openai/gpt-5.1-codex-max",
    "openai/gpt-5.4",
    "openai/gpt-5.4-mini",
    "openai/gpt-5.4-nano",
    "openai/gpt-5.5",
    "openai/gpt-5-pro",
    "openai/gpt-5.2-pro",
    "openai/gpt-5.4-pro",
    "gpt-5.4",  # bare OpenAI SDK form
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
    # Non-gpt-5 `-chat` model carrying a reasoning suffix: the gpt-5-scoped
    # `-chat` carve-out must NOT suppress this (the substring loop catches it).
    "deepseek/deepseek-chat-v3.1-thinking",
    # OpenRouter-prefixed variants still get detected
    "openrouter/openai/gpt-5.4-pro",
    "openrouter/openai/o3",
    "openrouter/deepseek/deepseek-r1",
    # Case-insensitive
    "OPENAI/GPT-5.4-PRO",
]


REASONING_NEGATIVE_CASES = [
    # GPT-5 `-chat` variants are the ONLY non-reasoning gpt-5* models
    # (verified OpenRouter 2026-05-29, issue #185).
    "openai/gpt-5-chat",
    "openai/gpt-5.1-chat",
    "openai/gpt-5.2-chat",
    "openai/gpt-5.3-chat",
    "openrouter/openai/gpt-5.3-chat",  # carve-out survives the openrouter/ prefix
    "gpt-5-chat",  # bare OpenAI SDK form of the carve-out
    "gpt-5.1-chat",
    # Pre-GPT-5 OpenAI chat model
    "openai/gpt-4o",
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


def test_non_reasoning_substrings_are_lowercase():
    for s in _NON_REASONING_SUBSTRINGS:
        assert s == s.lower(), f"non-reasoning substring not lowercase: {s}"


def test_reasoning_max_tokens_multiplier_sensible():
    """Calibrated for GPT-5.4 Pro burning ~15k reasoning on overview; an 8x
    multiplier on 8k default gives 64k headroom. Accept 4-16 as reasonable."""
    assert 4 <= REASONING_MAX_TOKENS_MULTIPLIER <= 16


def test_reasoning_effort_default_is_recognized_value():
    assert REASONING_EFFORT_DEFAULT in {"low", "medium", "high"}


def test_model_filename_slug_preserves_common_model_id_characters():
    assert model_filename_slug("anthropic/claude-sonnet-4-6") == "anthropic_claude-sonnet-4-6"
    assert model_filename_slug("gpt-5.4") == "gpt-5.4"


def test_model_filename_slug_normalizes_separators_and_whitespace():
    assert model_filename_slug("  qwen/qwen-plus-2025-07-28:thinking  ") == (
        "qwen_qwen-plus-2025-07-28_thinking"
    )


# ---------------------------------------------------------------------------
# supports_temperature — issue #162
# ---------------------------------------------------------------------------


def test_supports_temperature_false_for_opus_4_7():
    assert supports_temperature("anthropic/claude-opus-4.7") is False


def test_supports_temperature_false_for_openrouter_opus_4_7():
    """Direct and OpenRouter-routed variants must resolve the same."""
    assert supports_temperature("openrouter/anthropic/claude-opus-4.7") is False


def test_supports_temperature_false_for_opus_4_7_hyphen():
    """litellm direct-Anthropic ships the hyphen form — must also gate."""
    assert supports_temperature("anthropic/claude-opus-4-7") is False


def test_supports_temperature_false_for_openrouter_opus_4_7_hyphen():
    """``openrouter/`` prefix is stripped before matching, so the hyphen form
    routed via OpenRouter still resolves to the gated prefix."""
    assert supports_temperature("openrouter/anthropic/claude-opus-4-7") is False


def test_supports_temperature_false_for_vertex_opus_4_7():
    """Vertex AI uses the hyphen form with a ``vertex_ai/`` prefix."""
    assert supports_temperature("vertex_ai/claude-opus-4-7") is False


def test_supports_temperature_false_for_bare_opus_4_7():
    """Bare Anthropic SDK / Bedrock-style ID without a provider prefix."""
    assert supports_temperature("claude-opus-4-7") is False


def test_supports_temperature_false_for_opus_4_8_forms():
    """Opus 4.8 (reasoning-first like 4.7) rejects temperature across ID forms."""
    assert supports_temperature("anthropic/claude-opus-4.8") is False
    assert supports_temperature("anthropic/claude-opus-4.8-fast") is False
    assert supports_temperature("anthropic/claude-opus-4-8") is False
    assert supports_temperature("openrouter/anthropic/claude-opus-4-8") is False
    assert supports_temperature("vertex_ai/claude-opus-4-8") is False
    assert supports_temperature("claude-opus-4-8") is False


def test_supports_temperature_false_for_gpt_5_family():
    """The whole GPT-5 family rejects temperature on the OpenRouter route
    (issue #185), not just 5.5; the prefix covers dot/codex/pro/chat/mini
    variants and the bare OpenAI-SDK form."""
    assert supports_temperature("openai/gpt-5.5") is False
    assert supports_temperature("openrouter/openai/gpt-5.5") is False
    assert supports_temperature("openai/gpt-5.5-pro") is False
    assert supports_temperature("gpt-5.5") is False
    assert supports_temperature("openai/gpt-5.4") is False
    assert supports_temperature("openai/gpt-5-mini") is False
    assert supports_temperature("openai/gpt-5-codex") is False
    assert supports_temperature("openai/gpt-5-chat") is False
    assert supports_temperature("openrouter/openai/gpt-5.4") is False
    assert supports_temperature("gpt-5.4") is False


def test_supports_temperature_false_for_claude_fable_5():
    """Claude Fable 5 drops temperature like the recent Opus models (issue
    #214; verified on OpenRouter — supported_parameters has no temperature).
    The name has no version dot, so all ID forms are identical."""
    assert supports_temperature(CLAUDE_FABLE_5_MODEL) is False
    assert supports_temperature("openrouter/anthropic/claude-fable-5") is False
    assert supports_temperature("vertex_ai/claude-fable-5") is False
    assert supports_temperature("claude-fable-5") is False


def test_supports_temperature_for_claude_5_models():
    """OpenRouter exposes temperature for Opus 5 but not Sonnet 5."""
    assert supports_temperature(CLAUDE_OPUS_5_MODEL) is True
    assert supports_temperature(CLAUDE_SONNET_5_MODEL) is False
    assert supports_temperature(f"openrouter/{CLAUDE_SONNET_5_MODEL}") is False


def test_supports_temperature_true_for_opus_4_6():
    assert supports_temperature("anthropic/claude-opus-4.6") is True


def test_supports_temperature_true_for_default_model():
    assert supports_temperature(DEFAULT_MODEL) is True


@pytest.mark.parametrize(
    "model_id",
    [
        "google/gemini-3-flash-preview",
        "moonshotai/kimi-k2.5",
        "x-ai/grok-4.1-fast",
        "openrouter/anthropic/claude-sonnet-4.6",
    ],
)
def test_supports_temperature_true_for_common_models(model_id):
    assert supports_temperature(model_id) is True


def test_temperature_unsupported_prefixes_are_lowercase():
    for p in TEMPERATURE_UNSUPPORTED_PREFIXES:
        assert p == p.lower(), f"unsupported-temperature prefix not lowercase: {p}"
