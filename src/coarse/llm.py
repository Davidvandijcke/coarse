"""LLM client for coarse.

Wraps litellm + instructor for structured output. Tracks cumulative cost across calls.
API keys are set in env vars by the caller; litellm picks them up automatically.
"""
from __future__ import annotations

import logging
import os

import instructor
import litellm
from pydantic import BaseModel

from coarse.config import CoarseConfig, load_config

logger = logging.getLogger(__name__)

# Suppress litellm noise
litellm.suppress_debug_info = True

# Models known to need JSON mode (no reliable tool-calling)
_JSON_MODE_PREFIXES = ("qwen", "deepseek", "mistral", "together", "gemini")


class LLMClient:
    """Wraps litellm + instructor for structured output. Tracks cumulative cost."""

    def __init__(self, model: str | None = None, config: CoarseConfig | None = None) -> None:
        if config is None:
            config = load_config()
        self._model = model or config.default_model
        self._model = _normalize_model(self._model)
        mode = instructor.Mode.JSON if _needs_json_mode(self._model) else instructor.Mode.TOOLS
        self._client = instructor.from_litellm(litellm.completion, mode=mode)
        self._cost_usd: float = 0.0

    def complete(
        self,
        messages: list[dict],
        response_model: type[BaseModel],
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> BaseModel:
        """Single structured LLM call. Returns parsed Pydantic model."""
        # Clamp max_tokens to model's known limit
        clamped = _clamp_max_tokens(self._model, max_tokens)

        response, completion = self._client.chat.completions.create_with_completion(
            model=self._model,
            messages=messages,
            response_model=response_model,
            max_tokens=clamped,
            temperature=temperature,
            max_retries=3,
        )
        try:
            cost = litellm.completion_cost(completion_response=completion)
            if cost is not None:
                self._cost_usd += cost
        except Exception:
            # Unknown model pricing — skip cost tracking silently
            pass
        return response

    @property
    def cost_usd(self) -> float:
        """Total USD spent across all complete() calls this session."""
        return self._cost_usd


def _normalize_model(model: str) -> str:
    """Ensure model string has the right provider prefix for litellm routing.

    If OPENROUTER_API_KEY is set and model looks like 'qwen/qwen3.5-plus'
    (third-party model without 'openrouter/' prefix), prepend 'openrouter/'.
    """
    if model.startswith("openrouter/"):
        return model
    # Direct provider models (anthropic/..., openai/..., google/...) — don't touch
    direct_providers = ("anthropic", "openai", "google", "gemini", "groq", "azure", "cohere")
    prefix = model.split("/")[0].lower() if "/" in model else ""
    if prefix in direct_providers:
        return model
    # If OPENROUTER_API_KEY is set and model has a slash (like qwen/qwen3.5-plus),
    # route through OpenRouter
    if "/" in model and os.environ.get("OPENROUTER_API_KEY"):
        return f"openrouter/{model}"
    return model


def _needs_json_mode(model: str) -> bool:
    """Check if the model needs JSON mode instead of tool-calling.

    OpenRouter-proxied models and several open-source model families
    don't reliably support tool-calling / function-calling mode.
    """
    lower = model.lower()
    # Anything routed through OpenRouter
    if lower.startswith("openrouter/"):
        return True
    # Known model families that work better with JSON mode
    for prefix in _JSON_MODE_PREFIXES:
        if prefix in lower:
            return True
    return False


def _clamp_max_tokens(model: str, requested: int) -> int:
    """Clamp max_tokens to the model's known output limit.

    Many models error on max_tokens > their actual output window.
    Falls back to a safe default of 4096 if model isn't in litellm's registry.
    """
    info = litellm.model_cost.get(model)
    if info is None and "/" in model:
        # Try without provider prefix
        info = litellm.model_cost.get(model.split("/", 1)[1])
    if info is None and model.startswith("openrouter/"):
        # Try without openrouter/ prefix
        info = litellm.model_cost.get(model.removeprefix("openrouter/"))

    if info is not None:
        model_max = info.get("max_output_tokens") or info.get("max_tokens") or 4096
        return min(requested, model_max)

    # Unknown model — use a safe default
    if requested > 16384:
        logger.debug("Unknown model %s, clamping max_tokens %d -> 4096", model, requested)
        return 4096
    return requested


def model_cost_per_token(model: str) -> tuple[float, float]:
    """Return (input_cost_per_token, output_cost_per_token) for a given model.

    Accepts litellm model strings (e.g. 'openai/gpt-4o' or 'gpt-4o').
    Returns (0.0, 0.0) if model not found.
    """
    costs = litellm.model_cost.get(model)
    if costs is None and "/" in model:
        costs = litellm.model_cost.get(model.split("/", 1)[1])
    if costs is None:
        return (0.0, 0.0)
    return (
        costs.get("input_cost_per_token", 0.0),
        costs.get("output_cost_per_token", 0.0),
    )


def estimate_call_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    """Deterministic cost estimate in USD given model and token counts."""
    input_cost, output_cost = model_cost_per_token(model)
    return input_cost * tokens_in + output_cost * tokens_out
