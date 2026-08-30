"""Register newly released model metadata with LiteLLM.

LiteLLM's bundled catalog can lag OpenRouter releases. Keeping the adapter in a
small module prevents the main LLM transport from accumulating provider data
and gives cost estimation one deterministic registry at import time.
"""

import litellm

from coarse.models import (
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
    GPT_5_6_SOL_PRO_MODEL,
    GPT_5_6_TERRA_MODEL,
    GROK_4_5_MODEL,
    KIMI_K3_MODEL,
    LITELLM_OPENROUTER_PREFIX,
    LONG_CONTEXT_PRICING_TIERS,
)


def register_model_costs() -> None:
    """Add current featured models and prompt-length price tiers to LiteLLM."""
    custom_model_info: dict[str, dict[str, int | float]] = {
        DEFAULT_MODEL: {
            "max_tokens": 1_000_000,
            "max_output_tokens": 65_536,
            "input_cost_per_token": 0.32e-6,
            "output_cost_per_token": 1.28e-6,
        },
        CLAUDE_OPUS_5_MODEL: {
            "max_tokens": 1_000_000,
            "max_output_tokens": 128_000,
            "input_cost_per_token": 5e-6,
            "output_cost_per_token": 25e-6,
        },
        CLAUDE_SONNET_5_MODEL: {
            "max_tokens": 1_000_000,
            "max_output_tokens": 128_000,
            "input_cost_per_token": 2e-6,
            "output_cost_per_token": 10e-6,
        },
        CLAUDE_FABLE_5_MODEL: {
            "max_tokens": 1_000_000,
            "max_output_tokens": 128_000,
            "input_cost_per_token": 10e-6,
            "output_cost_per_token": 50e-6,
        },
        GPT_5_6_SOL_MODEL: {
            "max_tokens": 1_050_000,
            "max_output_tokens": 128_000,
            "input_cost_per_token": 5e-6,
            "output_cost_per_token": 30e-6,
        },
        # OpenRouter's pro-reasoning variant of Sol — same per-token pricing
        # and limits as base Sol (verified 2026-08-30); pro mode just spends
        # more reasoning tokens. Registered under the variant ID so the
        # pre-flight cost gate prices it before llm.py aliases the wire
        # request to the base model (see DIRECT_REQUEST_MODEL_ALIASES).
        GPT_5_6_SOL_PRO_MODEL: {
            "max_tokens": 1_050_000,
            "max_output_tokens": 128_000,
            "input_cost_per_token": 5e-6,
            "output_cost_per_token": 30e-6,
        },
        GPT_5_6_LUNA_MODEL: {
            "max_tokens": 1_050_000,
            "max_output_tokens": 128_000,
            "input_cost_per_token": 0.5e-6,
            "output_cost_per_token": 3e-6,
        },
        GPT_5_6_TERRA_MODEL: {
            "max_tokens": 1_050_000,
            "max_output_tokens": 128_000,
            "input_cost_per_token": 1.25e-6,
            "output_cost_per_token": 7.5e-6,
        },
        GEMINI_3_6_FLASH_MODEL: {
            "max_tokens": 1_048_576,
            "max_output_tokens": 65_536,
            "input_cost_per_token": 1.5e-6,
            "output_cost_per_token": 7.5e-6,
        },
        KIMI_K3_MODEL: {
            "max_tokens": 1_048_576,
            # OpenRouter does not currently report an explicit completion cap.
            "max_output_tokens": 131_072,
            "input_cost_per_token": 3e-6,
            "output_cost_per_token": 15e-6,
        },
        GROK_4_5_MODEL: {
            "max_tokens": 500_000,
            # OpenRouter does not currently report an explicit completion cap.
            "max_output_tokens": 131_072,
            "input_cost_per_token": 2e-6,
            "output_cost_per_token": 6e-6,
        },
        # Fusion reports dynamic pricing (-1), so use measured representative
        # rates and register both its canonical and normalized routing forms.
        FUSION_MODEL: {
            "max_tokens": 1_000_000,
            "max_output_tokens": 32_768,
            "input_cost_per_token": FUSION_INPUT_COST_PER_TOKEN,
            "output_cost_per_token": FUSION_OUTPUT_COST_PER_TOKEN,
        },
    }

    # LiteLLM understands several threshold-key names. The explicit cost floor
    # in llm.py covers OpenRouter tiers it does not yet apply (notably Qwen 256k).
    for model_id, tier in LONG_CONTEXT_PRICING_TIERS.items():
        threshold_k = int(tier["min_prompt_tokens"]) // 1_000
        custom_model_info[model_id][f"input_cost_per_token_above_{threshold_k}k_tokens"] = tier[
            "input_cost_per_token"
        ]
        custom_model_info[model_id][f"output_cost_per_token_above_{threshold_k}k_tokens"] = tier[
            "output_cost_per_token"
        ]

    for model_id, info in custom_model_info.items():
        litellm.model_cost[model_id] = info
        litellm.model_cost[f"{LITELLM_OPENROUTER_PREFIX}{model_id}"] = info
