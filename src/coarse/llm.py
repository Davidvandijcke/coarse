"""LLM client for coarse.

Wraps litellm + instructor for structured output. Tracks cumulative cost across calls.
API keys are set in env vars by the caller; litellm picks them up automatically.
"""
from __future__ import annotations

import logging
import os
import re

import instructor
import litellm
from pydantic import BaseModel

from coarse.config import CoarseConfig, load_config
from coarse.models import JSON_MODE_PREFIXES

logger = logging.getLogger(__name__)

# Suppress litellm noise
litellm.suppress_debug_info = True

# Register models missing from litellm's registry.
# litellm.model_cost is the lookup used by _clamp_max_tokens.
# Values from OpenRouter /api/v1/models (verified 2026-03-04).
_CUSTOM_MODEL_INFO: dict[str, dict] = {
    "qwen/qwen3.5-plus-02-15": {
        "max_tokens": 1_000_000,
        "max_output_tokens": 65_536,
        "input_cost_per_token": 0.26e-6,
        "output_cost_per_token": 1.56e-6,
    },
}
for _model_id, _info in _CUSTOM_MODEL_INFO.items():
    litellm.model_cost[_model_id] = _info
    litellm.model_cost[f"openrouter/{_model_id}"] = _info


_CTRL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def _sanitized_completion(*args, **kwargs):
    """Wrap litellm.completion to strip control characters from response content.

    Some models (e.g. MiMo) emit control characters in JSON output that break
    Pydantic parsing.  Stripping \x00-\x1f (except \t and \n) is safe for JSON.
    """
    response = litellm.completion(*args, **kwargs)
    for choice in getattr(response, "choices", []):
        msg = getattr(choice, "message", None)
        if msg and hasattr(msg, "content") and isinstance(msg.content, str):
            msg.content = _CTRL_CHAR_RE.sub("", msg.content)
    return response


class LLMClient:
    """Wraps litellm + instructor for structured output. Tracks cumulative cost."""

    def __init__(self, model: str | None = None, config: CoarseConfig | None = None) -> None:
        if config is None:
            config = load_config()
        self._model = model or config.default_model
        self._model = _normalize_model(self._model)
        mode = _select_instructor_mode(self._model)
        self._client = instructor.from_litellm(_sanitized_completion, mode=mode)
        self._cost_usd: float = 0.0

    def complete(
        self,
        messages: list[dict],
        response_model: type[BaseModel],
        max_tokens: int = 4096,
        temperature: float = 0.3,
        timeout: int = 600,
        **kwargs,
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
            timeout=timeout,
            max_retries=3,
            **kwargs,
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

    @property
    def supports_prompt_caching(self) -> bool:
        """Whether the model supports Anthropic-style prompt caching.

        Only True for direct Anthropic API calls (not OpenRouter-proxied),
        since OpenRouter does not forward cache_control to Anthropic.
        """
        lower = self._model.lower()
        return "anthropic" in lower and not lower.startswith("openrouter/")


def _normalize_model(model: str) -> str:
    """Ensure model string has the right provider prefix for litellm routing.

    If OPENROUTER_API_KEY is set and model looks like 'qwen/qwen3.5-plus'
    (third-party model without 'openrouter/' prefix), prepend 'openrouter/'.
    """
    if model.startswith("openrouter/"):
        return model
    # Direct provider models — keep as-is only if the provider's API key is set.
    # Otherwise, fall through to OpenRouter routing below.
    # Maps prefix -> list of env vars to check (first match wins)
    direct_providers: dict[str, list[str]] = {
        "anthropic": ["ANTHROPIC_API_KEY"],
        "openai": ["OPENAI_API_KEY"],
        "google": ["GOOGLE_API_KEY"],
        "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
        "groq": ["GROQ_API_KEY"],
        "azure": ["AZURE_API_KEY"],
        "cohere": ["COHERE_API_KEY"],
    }
    prefix = model.split("/")[0].lower() if "/" in model else ""
    if prefix in direct_providers:
        if any(os.environ.get(v) for v in direct_providers[prefix]):
            return model
        # No direct key — fall through to OpenRouter routing
    # If OPENROUTER_API_KEY is set and model has a slash (like qwen/qwen3.5-plus),
    # route through OpenRouter
    if "/" in model and os.environ.get("OPENROUTER_API_KEY"):
        # litellm uses gemini/ for Google AI Studio, but OpenRouter uses google/
        if model.startswith("gemini/"):
            model = "google/" + model.removeprefix("gemini/")
        return f"openrouter/{model}"
    return model


def _select_instructor_mode(model: str) -> instructor.Mode:
    """Select the best instructor mode for the model."""
    lower = model.lower()
    # OpenRouter-proxied models
    if lower.startswith("openrouter/"):
        return instructor.Mode.JSON
    # Known model families that work better with JSON mode
    for prefix in JSON_MODE_PREFIXES:
        if prefix in lower:
            return instructor.Mode.JSON
    return instructor.Mode.TOOLS


def _lookup_model_cost(model: str) -> dict | None:
    """Look up model info in litellm's cost registry, trying prefix variants."""
    info = litellm.model_cost.get(model)
    if info is None and "/" in model:
        info = litellm.model_cost.get(model.split("/", 1)[1])
    if info is None and model.startswith("openrouter/"):
        info = litellm.model_cost.get(model.removeprefix("openrouter/"))
    return info


def _clamp_max_tokens(model: str, requested: int) -> int:
    """Clamp max_tokens to the model's known output limit.

    Many models error on max_tokens > their actual output window.
    Falls back to a safe default of 4096 if model isn't in litellm's registry.
    """
    info = _lookup_model_cost(model)

    if info is not None:
        model_max = info.get("max_output_tokens") or info.get("max_tokens") or 4096
        return min(requested, model_max)

    # Unknown model — use a conservative default
    logger.debug("Unknown model %s, clamping max_tokens %d -> 16384", model, requested)
    return min(requested, 16384)


def model_cost_per_token(model: str) -> tuple[float, float]:
    """Return (input_cost_per_token, output_cost_per_token) for a given model.

    Accepts litellm model strings (e.g. 'openai/gpt-4o' or 'gpt-4o').
    Returns (0.0, 0.0) if model not found.
    """
    costs = _lookup_model_cost(model)
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
