"""LLM client for coarse.

Wraps litellm + instructor for structured output. Tracks cumulative cost across calls.
API keys are set in env vars by the caller; litellm picks them up automatically.
"""

from __future__ import annotations

import logging
import re
import threading

import instructor
import litellm
from pydantic import BaseModel

from coarse.config import (
    PROVIDER_ENV_VARS,
    CoarseConfig,
    has_provider_key,
    load_config,
    resolve_api_key,
)
from coarse.models import (
    CHEAP_STAGE_MODEL,
    DEFAULT_MODEL,
    JSON_MODE_PREFIXES,
    KIMI_K2_5_MODEL,
    MARKDOWN_JSON_PREFIXES,
    REASONING_EFFORT_DEFAULT,
    REASONING_MAX_TOKENS_MULTIPLIER,
    is_reasoning_model,
)

logger = logging.getLogger(__name__)

# Suppress litellm noise
litellm.suppress_debug_info = True

# Silently drop provider-specific params (like reasoning_effort) when the
# target provider doesn't support them, instead of raising. This lets us
# pass reasoning_effort for every reasoning model without having to
# maintain a per-provider allow-list — litellm drops it for providers
# that don't accept it (Qwen thinking, DeepSeek R1, etc.) and forwards
# it where it matters (OpenAI o-series, GPT-5 Pro).
litellm.drop_params = True

# Register models missing from litellm's registry.
# litellm.model_cost is the lookup used by _clamp_max_tokens.
# Values from OpenRouter /api/v1/models (verified 2026-03-04 and 2026-04-11
# for the glm-5.1 cheap-tier entry).
_CUSTOM_MODEL_INFO: dict[str, dict] = {
    DEFAULT_MODEL: {
        "max_tokens": 1_000_000,
        "max_output_tokens": 65_536,
        "input_cost_per_token": 0.26e-6,
        "output_cost_per_token": 1.56e-6,
    },
    KIMI_K2_5_MODEL: {
        "max_tokens": 131_072,
        "max_output_tokens": 32_768,
        "input_cost_per_token": 0.35e-6,
        "output_cost_per_token": 0.7e-6,
    },
    CHEAP_STAGE_MODEL: {
        # glm-5.1 on DeepInfra (the primary provider in CHEAP_STAGE_PROVIDERS).
        # Without this entry, cost.py::build_cost_estimate under-quotes the
        # 4 cheap-tier stages to $0.00 because litellm's default registry
        # has no entry for z-ai/glm-5.1.
        "max_tokens": 202_752,
        "max_output_tokens": 65_535,
        "input_cost_per_token": 1.40e-6,
        "output_cost_per_token": 4.40e-6,
    },
}
for _model_id, _info in _CUSTOM_MODEL_INFO.items():
    litellm.model_cost[_model_id] = _info
    litellm.model_cost[f"openrouter/{_model_id}"] = _info


_CTRL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
_DEGENERATE_RE = re.compile(r"(.)\1{50,}")  # 50+ consecutive identical chars


class DegenerateReasoningError(RuntimeError):
    """Raised when a model produces degenerate reasoning (e.g. repeated chars)."""


def _check_degenerate_reasoning(response) -> None:
    """Detect reasoning models stuck in repetition loops and fail fast.

    Some reasoning models (e.g. Kimi k2.5) occasionally enter a degenerate
    state where reasoning_content is just repeated characters, consuming all
    tokens and producing no useful content. Detecting this early prevents
    wasting retries and money.
    """
    for choice in getattr(response, "choices", []):
        msg = getattr(choice, "message", None)
        if msg is None:
            continue
        reasoning = getattr(msg, "reasoning_content", None)
        if not reasoning or msg.content is not None:
            continue
        # content is None and reasoning exists — check if reasoning is degenerate
        if _DEGENERATE_RE.search(reasoning):
            raise DegenerateReasoningError(
                f"Model produced degenerate reasoning ({len(reasoning)} chars of "
                f"repeated characters) with no content output. This is a known "
                f"failure mode of some reasoning models. Try a different model."
            )


def _inject_openrouter_privacy(model: str, kwargs: dict) -> dict:
    """Prepare kwargs for an OpenRouter-routed call: privacy flag + explicit api_key.

    Privacy: adds provider.data_collection=deny so OpenRouter only routes to
    providers that do not retain or train on user data. See
    https://openrouter.ai/docs/guides/privacy/data-collection.

    Auth: passes OPENROUTER_API_KEY explicitly via api_key. Relying on litellm's
    env-var auto-lookup has bitten us in production (Modal container) with
    'Missing Authentication header' errors even when the env var is set at the
    moment of the call. Passing api_key explicitly removes the ambiguity.

    No-op for direct provider calls (Anthropic/OpenAI/Google APIs) — both
    behaviors are OpenRouter-specific.
    """
    if not model.startswith("openrouter/"):
        return kwargs
    extra_body = dict(kwargs.get("extra_body") or {})
    provider_cfg = dict(extra_body.get("provider") or {})
    provider_cfg.setdefault("data_collection", "deny")
    extra_body["provider"] = provider_cfg
    result = {**kwargs, "extra_body": extra_body}
    # Strip a caller-provided api_key too: a whitespace-only value from any
    # upstream path (e.g. a future helper that plumbs the key explicitly
    # instead of via env) would otherwise still produce a `Bearer ` header.
    caller_key = result.get("api_key")
    if caller_key is not None:
        caller_key = str(caller_key).strip()
        if caller_key:
            result["api_key"] = caller_key
        else:
            result.pop("api_key", None)
    if "api_key" not in result:
        # resolve_api_key() goes through _clean_env internally, so a
        # whitespace-only env value is treated as unset. It also respects
        # ~/.coarse/config.toml keys, which bare env reads would miss.
        or_key = resolve_api_key("openrouter")
        if or_key:
            result["api_key"] = or_key
    return result


def _sanitized_completion(*args, **kwargs):
    """Wrap non-streaming litellm.completion: strip control chars, detect degenerate output.

    Some models (e.g. MiMo) emit literal control characters in JSON output that
    break Pydantic parsing. Stripping \\x00-\\x1f (except \\t and \\n) is safe
    for JSON. We also strip the 6-char ``\\u0000`` escape form because it
    survives _CTRL_CHAR_RE and is reconstituted as a real NUL by json.loads,
    which later crashes the Supabase write with Postgres 22P05.

    Streaming responses (CustomStreamWrapper) are not supported — the choices
    iteration silently no-ops on them.
    """
    kwargs = _inject_openrouter_privacy(kwargs.get("model", ""), kwargs)
    response = litellm.completion(*args, **kwargs)
    _check_degenerate_reasoning(response)
    for choice in getattr(response, "choices", []):
        msg = getattr(choice, "message", None)
        if msg and hasattr(msg, "content") and isinstance(msg.content, str):
            msg.content = _CTRL_CHAR_RE.sub("", msg.content)
            msg.content = msg.content.replace("\\u0000", "")
    return response


class LLMClient:
    """Wraps litellm + instructor for structured output. Tracks cumulative cost."""

    def __init__(
        self,
        model: str | None = None,
        config: CoarseConfig | None = None,
        *,
        provider_allowlist: tuple[str, ...] | None = None,
        fallback_client: "LLMClient | None" = None,
    ) -> None:
        if config is None:
            config = load_config()
        self._model = model or config.default_model
        self._model = _normalize_model(self._model, config)
        mode = _select_instructor_mode(self._model)
        self._client = instructor.from_litellm(_sanitized_completion, mode=mode)
        self._cost_usd: float = 0.0
        self._lock = threading.Lock()
        self._is_reasoning = is_reasoning_model(self._model)
        # Per-client provider allowlist (used for strict geographic routing,
        # e.g. "US-HQ only" on the cheap stage tier — see StageRouter in
        # routing.py). Injected as OpenRouter's `provider.only` preference
        # at call time. Layers cleanly over _inject_openrouter_privacy's
        # data_collection=deny setdefault: both are active.
        self._provider_allowlist = provider_allowlist
        # Optional model-level fallback: if this client's complete() or
        # complete_text() raises, the call is retried on the fallback
        # client (which may itself have a different model, instructor
        # mode, and provider_allowlist). Used by StageRouter to build a
        # glm-5.1 → kimi-k2.5 cheap-tier chain where each underlying
        # model needs its own instructor mode (JSON vs MD_JSON) — see
        # CHEAP_STAGE_FALLBACK_MODEL in models.py.
        self._fallback_client = fallback_client

    def _apply_provider_prefs(self, kwargs: dict) -> dict:
        """Merge ``self._provider_allowlist`` into ``extra_body.provider.only``.

        No-op when the client was constructed without an allowlist, so
        non-geo-restricted clients (the common case) are unchanged.
        Preserves any caller-provided ``extra_body.provider`` entries —
        uses ``setdefault`` on the ``only`` key so a caller passing their
        own explicit ``provider.only`` is not clobbered.
        """
        if not self._provider_allowlist:
            return kwargs
        extra_body = dict(kwargs.get("extra_body") or {})
        provider_cfg = dict(extra_body.get("provider") or {})
        provider_cfg.setdefault("only", list(self._provider_allowlist))
        extra_body["provider"] = provider_cfg
        return {**kwargs, "extra_body": extra_body}

    def complete(
        self,
        messages: list[dict],
        response_model: type[BaseModel],
        max_tokens: int = 4096,
        temperature: float = 0.3,
        timeout: int = 600,
        **kwargs,
    ) -> BaseModel:
        """Single structured LLM call. Returns parsed Pydantic model.

        If this client was constructed with ``fallback_client``, a raised
        exception triggers a retry on the fallback (which may use a
        different model and instructor mode). Only the primary's failure
        is retried — the fallback itself is called plain, so a chain
        longer than 2 links requires nesting fallbacks.
        """
        try:
            return self._complete_primary(
                messages,
                response_model,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout,
                **kwargs,
            )
        except Exception:
            if self._fallback_client is None:
                raise
            logger.warning(
                "Primary model %s failed, falling back to %s",
                self._model,
                self._fallback_client.model,
                exc_info=True,
            )
            return self._fallback_client.complete(
                messages,
                response_model,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout,
                **kwargs,
            )

    def _complete_primary(
        self,
        messages: list[dict],
        response_model: type[BaseModel],
        max_tokens: int = 4096,
        temperature: float = 0.3,
        timeout: int = 600,
        **kwargs,
    ) -> BaseModel:
        """Inner complete() without fallback dispatch — used by complete()
        and called directly by tests that need to bypass fallback logic."""
        # Reasoning models (o-series, GPT-5 Pro, DeepSeek R1, thinking
        # variants, etc.) spend most of max_tokens on hidden reasoning
        # before emitting visible output. Bump the ceiling so both fit;
        # _clamp_max_tokens will then cap to the model's true limit.
        # Diagnosed from review 3ee351e6 where GPT-5.4 Pro burned 15k+
        # reasoning tokens before hitting finish_reason='length' with no
        # visible content.
        requested = max_tokens
        if self._is_reasoning:
            requested = max_tokens * REASONING_MAX_TOKENS_MULTIPLIER

        clamped = _clamp_max_tokens(self._model, requested)

        # MD_JSON models (Kimi) need lower temperature and higher max_tokens.
        # Re-clamp after raising the floor so we don't exceed the model ceiling
        # on Kimi variants with smaller output windows.
        if any(p in self._model.lower() for p in MARKDOWN_JSON_PREFIXES):
            temperature = min(temperature, 0.1)
            clamped = _clamp_max_tokens(self._model, max(clamped, 16384))

        # For reasoning models, also cap the thinking budget server-side
        # via litellm's unified `reasoning_effort` param. litellm routes
        # this to the right provider field (e.g. OpenAI's reasoning_effort)
        # and — because we set litellm.drop_params=True — silently drops
        # it for providers that don't accept it.
        #
        # Use an explicit `.get() is None` check rather than `setdefault`
        # so a caller passing `reasoning_effort=None` gets the default
        # instead of silently disabling it (setdefault would treat None
        # as "already set"). A caller can still disable by passing a
        # real string like "low" or by passing a non-None sentinel.
        call_kwargs = dict(kwargs)
        if self._is_reasoning and call_kwargs.get("reasoning_effort") is None:
            call_kwargs["reasoning_effort"] = REASONING_EFFORT_DEFAULT

        call_kwargs = self._apply_provider_prefs(call_kwargs)

        response, completion = self._client.chat.completions.create_with_completion(
            model=self._model,
            messages=messages,
            response_model=response_model,
            max_tokens=clamped,
            temperature=temperature,
            timeout=timeout,
            max_retries=3,
            **call_kwargs,
        )
        try:
            cost = litellm.completion_cost(completion_response=completion)
            if cost is not None:
                with self._lock:
                    self._cost_usd += cost
        except Exception:
            logger.debug("Cost tracking failed for model %s", self._model, exc_info=True)
        return response

    def complete_text(
        self,
        messages: list[dict],
        max_tokens: int = 4096,
        temperature: float = 0.3,
        timeout: int = 600,
        **kwargs,
    ) -> str:
        """Unstructured text completion — returns the raw response string.

        Used for models where instructor's structured output makes no sense
        (e.g. Perplexity Sonar Pro, which returns prose with citations).
        Cost is tracked like complete(); control characters are still
        stripped via _sanitized_completion. Falls back to fallback_client
        on exception, same as complete().
        """
        try:
            return self._complete_text_primary(
                messages,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout,
                **kwargs,
            )
        except Exception:
            if self._fallback_client is None:
                raise
            logger.warning(
                "Primary model %s failed on complete_text, falling back to %s",
                self._model,
                self._fallback_client.model,
                exc_info=True,
            )
            return self._fallback_client.complete_text(
                messages,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout,
                **kwargs,
            )

    def _complete_text_primary(
        self,
        messages: list[dict],
        max_tokens: int = 4096,
        temperature: float = 0.3,
        timeout: int = 600,
        **kwargs,
    ) -> str:
        """Inner complete_text() without fallback dispatch."""
        clamped = _clamp_max_tokens(self._model, max_tokens)
        call_kwargs = self._apply_provider_prefs(dict(kwargs))
        response = _sanitized_completion(
            model=self._model,
            messages=messages,
            max_tokens=clamped,
            temperature=temperature,
            timeout=timeout,
            **call_kwargs,
        )
        try:
            cost = litellm.completion_cost(completion_response=response)
            if cost is not None:
                with self._lock:
                    self._cost_usd += cost
        except Exception:
            logger.debug("Cost tracking failed for model %s", self._model, exc_info=True)

        content = response.choices[0].message.content
        if not content or not content.strip():
            raise ValueError(f"Model {self._model} returned empty response")
        return content.strip()

    def add_cost(self, cost_usd: float) -> None:
        """Register an external cost (e.g. from a direct litellm.completion call)."""
        with self._lock:
            self._cost_usd += cost_usd

    @property
    def model(self) -> str:
        """The resolved model ID for this client."""
        return self._model

    @property
    def cost_usd(self) -> float:
        """Total USD spent across all complete() calls this session."""
        return self._cost_usd

    @property
    def is_reasoning(self) -> bool:
        """Whether the resolved model uses hidden reasoning tokens.

        Fixed at construction from the resolved model ID. Deliberately
        named `is_reasoning` (not `is_reasoning_model`) to avoid a
        readability trap where `self.is_reasoning_model` and the
        module-level `is_reasoning_model(...)` function would look the
        same at a glance without the parentheses.
        """
        return self._is_reasoning

    @property
    def supports_prompt_caching(self) -> bool:
        """Whether the model supports Anthropic-style prompt caching.

        Only True for direct Anthropic API calls (not OpenRouter-proxied),
        since OpenRouter does not forward cache_control to Anthropic.
        """
        lower = self._model.lower()
        return "anthropic" in lower and not lower.startswith("openrouter/")


def _normalize_model(model: str, config: CoarseConfig | None = None) -> str:
    """Ensure model string has the right provider prefix for litellm routing.

    If the named direct provider has no key (env or config) and an OpenRouter
    key is available, rewrite to 'openrouter/<model>' so the call goes through
    OpenRouter. Config-file keys count — not just env vars.
    """
    if model.startswith("openrouter/"):
        return model
    prefix = model.split("/")[0].lower() if "/" in model else ""
    # has_provider_key() goes through _clean_env and also checks
    # ~/.coarse/config.toml keys, so whitespace-only env values don't flip
    # routing to the direct-provider branch and config-file-only users
    # still get routed correctly.
    if prefix in PROVIDER_ENV_VARS and has_provider_key(prefix, config):
        return model
    if "/" in model and resolve_api_key("openrouter", config):
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
        # Check if it's a markdown-JSON model first (e.g. Kimi via OpenRouter)
        for prefix in MARKDOWN_JSON_PREFIXES:
            if prefix in lower:
                return instructor.Mode.MD_JSON
        return instructor.Mode.JSON
    # Markdown-JSON models (Kimi) — need MD_JSON mode
    for prefix in MARKDOWN_JSON_PREFIXES:
        if prefix in lower:
            return instructor.Mode.MD_JSON
    # Known model families that work better with JSON mode
    for prefix in JSON_MODE_PREFIXES:
        if prefix in lower:
            return instructor.Mode.JSON
    return instructor.Mode.TOOLS


def _lookup_model_cost(model: str) -> dict | None:
    """Look up model info in litellm's cost registry, trying prefix variants.

    litellm's registry is inconsistent about how it keys provider models:
    some entries live under a bare `provider/model` form, others only
    under `openrouter/provider/model` (this is how the current Claude 4.6
    entries are stored — `openrouter/anthropic/claude-sonnet-4.6` hits
    but `anthropic/claude-sonnet-4.6` doesn't). Try both directions so
    the cost gate returns accurate numbers regardless of which form the
    caller passed.
    """
    info = litellm.model_cost.get(model)
    if info is None and "/" in model:
        info = litellm.model_cost.get(model.split("/", 1)[1])
    if info is None and model.startswith("openrouter/"):
        info = litellm.model_cost.get(model.removeprefix("openrouter/"))
    # Bare provider/model → try with the openrouter/ prefix added.
    # (Some entries, notably anthropic/claude-{sonnet,opus}-4.6, only
    # exist under the openrouter/ form in litellm's registry.)
    if info is None and "/" in model and not model.startswith("openrouter/"):
        info = litellm.model_cost.get("openrouter/" + model)
    return info


_UNKNOWN_MODEL_CEILING = 16_384
# Reasoning models need a larger fallback ceiling so the 8x multiplier
# applied upstream in LLMClient.complete() isn't immediately clamped back
# down to 16k when the model ID isn't in litellm's registry (common case
# for brand-new thinking variants: kimi-k2-thinking, qwen3-*-thinking,
# deepseek-r* distills). 65k accommodates 8 * 8192 = 65536 without
# clamping, which is the typical caller budget for the heavier agent
# stages (overview, sections, crossref, critique).
_UNKNOWN_REASONING_MODEL_CEILING = 65_536


def _clamp_max_tokens(model: str, requested: int) -> int:
    """Clamp max_tokens to the model's known output limit.

    Many models error on max_tokens > their actual output window.
    Falls back to a safe default if the model isn't in litellm's registry;
    the fallback is higher for reasoning models so the reasoning-bump
    multiplier in LLMClient.complete() isn't immediately neutralized.
    """
    info = _lookup_model_cost(model)

    if info is not None:
        model_max = info.get("max_output_tokens") or info.get("max_tokens") or 4096
        return min(requested, model_max)

    # Unknown model — use a conservative default, but give reasoning
    # models enough headroom that the upstream 8x multiplier still works.
    ceiling = (
        _UNKNOWN_REASONING_MODEL_CEILING if is_reasoning_model(model) else _UNKNOWN_MODEL_CEILING
    )
    logger.debug("Unknown model %s, clamping max_tokens %d -> %d", model, requested, ceiling)
    return min(requested, ceiling)


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


# Reasoning-token overhead multiplier for cost estimation.
#
# Reasoning models bill hidden reasoning tokens at the *output* rate, and
# those tokens do not show up in the `tokens_out` budget the caller asked
# for. Empirically, on academic-review tasks a reasoning model spends
# roughly 4x the visible output budget on internal thinking (measured from
# review 3ee351e6: ~2k visible overview output, ~15k reasoning — the
# overview hit max_tokens before emitting any content, but that ratio
# generalizes to the sections/crossref/critique stages once the ceiling
# is raised). reasoning_effort="medium" caps this, so 4x is a reasonable
# billable estimate.
#
# Without this adjustment, the pre-flight cost gate under-quotes reasoning
# models by 3-5x and the user sees a surprise bill post-run.
#
# Note: this is the *cost overhead* multiplier. The request-budget
# multiplier is 8x and lives in `models.py::REASONING_MAX_TOKENS_MULTIPLIER` —
# they're intentionally asymmetric because reasoning_effort="medium" is
# expected to cap actual usage well below the raised ceiling. If you change
# one, check the other.
_REASONING_OVERHEAD_MULTIPLIER: float = 4.0


def estimate_reasoning_overhead_tokens(model: str, tokens_out: int) -> int:
    """Extra billable output tokens contributed by hidden reasoning.

    Returns 0 for non-reasoning models. For reasoning models, returns an
    empirical multiple of the requested visible output so cost estimates
    include the reasoning phase (which bills at the output-token rate).
    """
    if not is_reasoning_model(model):
        return 0
    return int(tokens_out * _REASONING_OVERHEAD_MULTIPLIER)


def estimate_call_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    """Deterministic cost estimate in USD given model and token counts.

    For reasoning models (o-series, GPT-5 Pro, DeepSeek R1, thinking
    variants, etc.), adds a reasoning-token overhead to tokens_out so the
    pre-flight estimate reflects the real cost. See
    estimate_reasoning_overhead_tokens for the multiplier's calibration.
    """
    input_cost, output_cost = model_cost_per_token(model)
    reasoning_overhead = estimate_reasoning_overhead_tokens(model, tokens_out)
    return input_cost * tokens_in + output_cost * (tokens_out + reasoning_overhead)
