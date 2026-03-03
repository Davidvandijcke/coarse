"""LLM client for coarse.

Wraps litellm + instructor for structured output. Tracks cumulative cost across calls.
API keys are set in env vars by the caller; litellm picks them up automatically.
"""
from __future__ import annotations

import instructor
import litellm
from pydantic import BaseModel

from coarse.config import CoarseConfig, load_config


class LLMClient:
    """Wraps litellm + instructor for structured output. Tracks cumulative cost."""

    def __init__(self, model: str | None = None, config: CoarseConfig | None = None) -> None:
        if config is None:
            config = load_config()
        self._model = model or config.default_model
        self._client = instructor.from_litellm(litellm.completion)
        self._cost_usd: float = 0.0

    def complete(
        self,
        messages: list[dict],
        response_model: type[BaseModel],
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> BaseModel:
        """Single structured LLM call. Returns parsed Pydantic model."""
        response, completion = self._client.chat.completions.create_with_completion(
            model=self._model,
            messages=messages,
            response_model=response_model,
            max_tokens=max_tokens,
            temperature=temperature,
            max_retries=2,
        )
        cost = litellm.completion_cost(completion_response=completion)
        if cost is not None:
            self._cost_usd += cost
        return response

    @property
    def cost_usd(self) -> float:
        """Total USD spent across all complete() calls this session."""
        return self._cost_usd


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
