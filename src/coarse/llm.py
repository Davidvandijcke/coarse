"""LLM client for coarse.

Wraps litellm + instructor for structured output. Tracks cumulative cost across calls.
API keys are set in env vars by the caller; litellm picks them up automatically.
"""

from __future__ import annotations

import json
import logging
import re
import threading
from collections.abc import Callable

import instructor
import litellm
from instructor.core.exceptions import InstructorRetryException
from pydantic import BaseModel

from coarse.config import (
    PROVIDER_ENV_VARS,
    CoarseConfig,
    has_provider_key,
    load_config,
    resolve_api_key,
)
from coarse.model_registry import register_model_costs
from coarse.models import (
    DIRECT_RESPONSES_MODEL_ALIASES,
    JSON_MODE_PREFIXES,
    MARKDOWN_JSON_PREFIXES,
    OPENROUTER_NAMESPACE_MODELS,
    REASONING_EFFORT_DEFAULT,
    REASONING_MAX_TOKENS_MULTIPLIER,
    is_reasoning_model,
    supports_temperature,
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

# Register model metadata before any client clamps tokens or estimates cost.
register_model_costs()


_CTRL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
_DEGENERATE_RE = re.compile(r"(.)\1{50,}")  # 50+ consecutive identical chars
_MARKDOWN_JSON_FENCE_RE = re.compile(
    r"^\s*```(?:json)?\s*(.*?)\s*```\s*$",
    flags=re.DOTALL | re.IGNORECASE,
)


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
    # Model is normally in kwargs because LLMClient calls instructor with
    # `model=...` as a keyword. Fall back to args[0] as a safety net in case
    # a future upstream (or a test double) passes it positionally — if the
    # fallback isn't here, `_inject_openrouter_privacy` silently no-ops and
    # every subsequent call hits OpenRouter with no Authorization header.
    model_arg = kwargs.get("model")
    if not model_arg and args:
        model_arg = args[0] if isinstance(args[0], str) else ""
    kwargs = _inject_openrouter_privacy(model_arg or "", kwargs)
    response = litellm.completion(*args, **kwargs)
    _check_degenerate_reasoning(response)
    for choice in getattr(response, "choices", []):
        msg = getattr(choice, "message", None)
        if msg and hasattr(msg, "content") and isinstance(msg.content, str):
            msg.content = _CTRL_CHAR_RE.sub("", msg.content)
            msg.content = msg.content.replace("\\u0000", "")
    return response


def _responses_completion(*, messages: list[dict], **kwargs):
    """Adapt Instructor's chat-shaped call to LiteLLM's Responses API."""
    return litellm.responses(input=messages, **kwargs)


def _build_responses_create() -> Callable[..., BaseModel]:
    """Build an Instructor-patched Responses API callable."""
    return instructor.patch(
        create=_responses_completion,
        mode=instructor.Mode.RESPONSES_TOOLS,
    )


def _extract_completion_text(completion: object) -> str | None:
    """Best-effort extraction of the first assistant content string."""
    for choice in getattr(completion, "choices", []) or []:
        msg = getattr(choice, "message", None)
        content = getattr(msg, "content", None)
        if isinstance(content, str) and content.strip():
            return content
    return None


def _unwrap_markdown_json(text: str) -> str:
    """Strip a surrounding ```json code fence when present."""
    match = _MARKDOWN_JSON_FENCE_RE.match(text.strip())
    return match.group(1) if match else text.strip()


def _retry_exception_has_json_parse_failure(exc: InstructorRetryException) -> bool:
    """Return True for malformed/truncated JSON failures, not generic schema issues."""
    candidates: list[str] = [str(exc)]
    for attempt in exc.failed_attempts or []:
        candidates.append(str(attempt.exception))
    lowered = "\n".join(candidates).lower()
    return "invalid json" in lowered or "json_invalid" in lowered or "eof while parsing" in lowered


def _extract_json_string_field(blob: str, field: str) -> str:
    """Extract and decode a JSON string field from a partially valid object."""
    pattern = rf'"{re.escape(field)}"\s*:\s*"((?:\\.|[^"\\])*)"'
    match = re.search(pattern, blob, flags=re.DOTALL)
    if not match:
        return ""
    return json.loads(f'"{match.group(1)}"')


def _extract_complete_json_objects(blob: str, field: str) -> list[dict[str, str]]:
    """Extract fully closed JSON objects from a possibly truncated array field."""
    match = re.search(rf'"{re.escape(field)}"\s*:\s*\[', blob)
    if not match:
        return []

    array_text = blob[match.end() :]
    objs: list[dict[str, str]] = []
    depth = 0
    start: int | None = None
    in_string = False
    escape = False

    for i, ch in enumerate(array_text):
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
            continue
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
            continue
        if ch == "}":
            if depth == 0:
                continue
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    parsed = json.loads(array_text[start : i + 1])
                except json.JSONDecodeError:
                    start = None
                    continue
                if isinstance(parsed, dict):
                    objs.append(parsed)
                start = None
    return objs


def _extract_json_string_list_field(blob: str, field: str) -> list[str]:
    """Extract a fully closed top-level JSON string list when present."""
    match = re.search(rf'"{re.escape(field)}"\s*:\s*\[(.*?)\]', blob, flags=re.DOTALL)
    if not match:
        return []
    values = []
    for item in re.finditer(r'"((?:\\.|[^"\\])*)"', match.group(1), flags=re.DOTALL):
        values.append(json.loads(f'"{item.group(1)}"'))
    return values


def _salvage_overview_feedback(completion: object) -> BaseModel | None:
    """Recover OverviewFeedback from truncated markdown-JSON by dropping partial tail data."""
    from coarse.types import OverviewFeedback, OverviewIssue

    raw = _extract_completion_text(completion)
    if not raw:
        return None

    blob = _unwrap_markdown_json(raw)
    summary = _extract_json_string_field(blob, "summary")
    assessment = _extract_json_string_field(blob, "assessment")
    recommendation = _extract_json_string_field(blob, "recommendation")
    issue_dicts = _extract_complete_json_objects(blob, "issues")
    revision_targets = _extract_json_string_list_field(blob, "revision_targets")

    issues = []
    for issue in issue_dicts:
        title = issue.get("title")
        body = issue.get("body")
        if isinstance(title, str) and title.strip() and isinstance(body, str) and body.strip():
            issues.append(OverviewIssue(title=title, body=body))

    if not issues:
        return None

    return OverviewFeedback(
        summary=summary,
        assessment=assessment,
        issues=issues,
        recommendation=recommendation,
        revision_targets=revision_targets,
    )


def _salvage_instructor_retry(
    response_model: type[BaseModel],
    exc: InstructorRetryException,
) -> tuple[BaseModel, object] | None:
    """Best-effort recovery from known malformed-JSON provider failures."""
    if response_model.__name__ != "OverviewFeedback":
        return None
    if not _retry_exception_has_json_parse_failure(exc):
        return None

    completions: list[object] = []
    if exc.last_completion is not None:
        completions.append(exc.last_completion)
    for attempt in exc.failed_attempts or []:
        if attempt.completion is not None:
            completions.append(attempt.completion)

    for completion in completions:
        recovered = _salvage_overview_feedback(completion)
        if recovered is not None:
            return recovered, completion
    return None


def _is_openrouter_kimi_model(model: str) -> bool:
    """Return True for Kimi routed through OpenRouter."""
    lower = model.lower()
    return lower.startswith("openrouter/") and any(p in lower for p in MARKDOWN_JSON_PREFIXES)


def _append_openrouter_plugin(extra_body: dict[str, object], plugin_id: str) -> None:
    """Append an OpenRouter plugin id unless the caller already set it."""
    plugins = list(extra_body.get("plugins") or [])
    for plugin in plugins:
        if isinstance(plugin, dict) and plugin.get("id") == plugin_id:
            extra_body["plugins"] = plugins
            return
    plugins.append({"id": plugin_id})
    extra_body["plugins"] = plugins


def _prepare_openrouter_kimi_structured_kwargs(kwargs: dict) -> dict:
    """Add OpenRouter structured-output knobs that improve Kimi JSON reliability.

    - `provider.require_parameters=True` ensures OpenRouter only routes to
      providers that actually support the requested JSON-mode parameter.
    - `response-healing` repairs malformed JSON syntax on non-streaming
      structured requests before the payload reaches Instructor.
    """
    prepared = dict(kwargs)
    extra_body = dict(prepared.get("extra_body") or {})
    provider_cfg = dict(extra_body.get("provider") or {})
    provider_cfg.setdefault("require_parameters", True)
    extra_body["provider"] = provider_cfg
    _append_openrouter_plugin(extra_body, "response-healing")
    prepared["extra_body"] = extra_body
    return prepared


def _should_retry_with_md_json(exc: Exception) -> bool:
    """Return True when OpenRouter rejected JSON mode and MD_JSON should be tried."""
    text = str(exc).lower()
    signals = (
        "response_format",
        "json_object",
        "json_schema",
        "unsupported parameter",
        "unsupported params",
        "require_parameters",
        "no endpoints found",
        "support all parameters",
    )
    return any(signal in text for signal in signals)


class LLMClient:
    """Wraps litellm + instructor for structured output. Tracks cumulative cost."""

    def __init__(
        self,
        model: str | None = None,
        config: CoarseConfig | None = None,
        *,
        cost_callback: Callable[[float], None] | None = None,
    ) -> None:
        if config is None:
            config = load_config()
        self._model = model or config.default_model
        self._model = _normalize_model(self._model, config)
        # Some OpenRouter variant IDs don't exist on the provider's own API
        # (e.g. openai/gpt-5.6-sol-pro → OpenAI 404s). On the direct route,
        # rewrite to the provider's real model ID and use the Responses API
        # with the variant's request defaults. The lookup is keyed on bare
        # IDs, so OpenRouter-proxied models — already `openrouter/`-prefixed by
        # _normalize_model — never match.
        self._responses_request_body: dict[str, object] | None = None
        alias = DIRECT_RESPONSES_MODEL_ALIASES.get(self._model)
        if alias is not None:
            self._model, self._responses_request_body = alias[0], dict(alias[1])
        self._mode = _select_instructor_mode(self._model)
        self._client = instructor.from_litellm(_sanitized_completion, mode=self._mode)
        self._structured_fallback_mode = _select_fallback_instructor_mode(self._model, self._mode)
        self._structured_fallback_client = (
            instructor.from_litellm(_sanitized_completion, mode=self._structured_fallback_mode)
            if self._structured_fallback_mode is not None
            else None
        )
        self._responses_create = (
            _build_responses_create() if self._responses_request_body is not None else None
        )
        self._cost_usd: float = 0.0
        self._lock = threading.Lock()
        self._is_reasoning = is_reasoning_model(self._model)
        self._cost_callback = cost_callback
        # Resolve the API key eagerly and stash it so every call can pass
        # `api_key=self._api_key` explicitly. Historically we relied on
        # `_inject_openrouter_privacy` running inside `_sanitized_completion`
        # to read the OpenRouter key from the env at call time, but in
        # production (Modal worker) that path has been landing with
        # "Missing Authentication header" even when the env var is set at
        # construction time. Resolving the key once, here, and forwarding
        # it through call_kwargs removes every call-time read from the
        # dependency chain and closes the race.
        self._api_key: str | None = resolve_api_key(self._model, config)

    def _prepare_responses_kwargs(self, call_kwargs: dict) -> dict:
        """Merge direct-route defaults into Responses API kwargs."""
        if self._responses_request_body is None:
            return call_kwargs
        prepared = dict(call_kwargs)
        requested_effort = prepared.pop("reasoning_effort", None)
        caller_reasoning = dict(prepared.pop("reasoning", None) or {})
        defaults = dict(self._responses_request_body)
        default_reasoning = dict(defaults.pop("reasoning", {}) or {})
        for key, value in defaults.items():
            prepared.setdefault(key, value)
        # The selected alias owns its mode ("-pro" must remain pro), while
        # effort stays independently caller-configurable as OpenAI documents.
        reasoning = {**caller_reasoning, **default_reasoning}
        if requested_effort is not None:
            reasoning["effort"] = requested_effort
        else:
            reasoning.setdefault("effort", REASONING_EFFORT_DEFAULT)
        prepared["reasoning"] = reasoning
        return prepared

    def _complete_with_client(
        self,
        client,
        messages: list[dict],
        response_model: type[BaseModel],
        max_tokens: int,
        timeout: int,
        call_kwargs: dict,
    ) -> tuple[BaseModel, object]:
        """Execute one structured call against a specific instructor client.

        Centralizes the malformed-JSON salvage path so both the primary JSON-mode
        call and the MD_JSON fallback recover partial `OverviewFeedback` the same
        way instead of only the first branch doing so.

        ``temperature`` is carried on ``call_kwargs`` (set by ``complete()``
        only when the target model supports it) rather than as an explicit
        parameter here — Anthropic's Claude Opus 4.7 rejects the parameter
        outright and the wrapper must be able to omit it entirely, not
        just send ``None``.
        """
        try:
            if self._responses_create is not None:
                response = self._responses_create(
                    model=self._model,
                    messages=messages,
                    response_model=response_model,
                    max_tokens=max_tokens,
                    timeout=timeout,
                    max_retries=3,
                    **call_kwargs,
                )
                return response, getattr(response, "_raw_response", None)
            return client.chat.completions.create_with_completion(
                model=self._model,
                messages=messages,
                response_model=response_model,
                max_tokens=max_tokens,
                timeout=timeout,
                max_retries=3,
                **call_kwargs,
            )
        except InstructorRetryException as exc:
            salvaged = _salvage_instructor_retry(response_model, exc)
            if salvaged is None:
                raise
            response, completion = salvaged
            logger.warning(
                "Recovered %s from malformed structured output on %s after %d failed attempts",
                response_model.__name__,
                self._model,
                exc.n_attempts,
            )
            return response, completion

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
        if self._responses_create is not None:
            call_kwargs = self._prepare_responses_kwargs(call_kwargs)
        elif self._is_reasoning and call_kwargs.get("reasoning_effort") is None:
            call_kwargs["reasoning_effort"] = REASONING_EFFORT_DEFAULT
        if _is_openrouter_kimi_model(self._model):
            call_kwargs = _prepare_openrouter_kimi_structured_kwargs(call_kwargs)
        # Forward the eagerly-resolved API key on every call so the litellm
        # request boundary never has to reach for os.environ mid-flight.
        if self._api_key and "api_key" not in call_kwargs:
            call_kwargs["api_key"] = self._api_key
        # Temperature is omitted entirely (not sent as None) for models
        # whose providers reject it outright — e.g. Anthropic's Claude
        # Opus 4.7, which 400s on temperature. See
        # ``supports_temperature`` in ``coarse.models`` for the allowlist.
        if supports_temperature(self._model):
            call_kwargs.setdefault("temperature", temperature)

        try:
            response, completion = self._complete_with_client(
                self._client,
                messages,
                response_model,
                clamped,
                timeout,
                call_kwargs,
            )
        except Exception as exc:
            if self._structured_fallback_client is None or not _should_retry_with_md_json(exc):
                raise
            else:
                logger.warning(
                    "Structured JSON mode rejected on %s (%s); retrying with %s",
                    self._model,
                    type(exc).__name__,
                    self._structured_fallback_mode,
                )
                response, completion = self._complete_with_client(
                    self._structured_fallback_client,
                    messages,
                    response_model,
                    clamped,
                    timeout,
                    call_kwargs,
                )
        try:
            # Pass model=self._model explicitly so completion_cost uses the
            # ID registered in model_registry instead of whatever
            # concrete version the provider stamped onto the response.
            # OpenRouter maps aliases like ``qwen/qwen3.5-plus-02-15`` to
            # date-stamped versions (e.g. ``qwen/qwen3.5-plus-20260216``)
            # which aren't in litellm's registry, so the default cost
            # lookup raises ``This model isn't mapped yet``.
            cost = _completion_cost_with_long_context_pricing(completion, self._model)
            if cost is not None:
                self.add_cost(cost)
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
        Cost is tracked like complete(); control characters are stripped on
        both the Chat Completions and Responses API paths.
        """
        clamped = _clamp_max_tokens(self._model, max_tokens)
        call_kwargs = dict(kwargs)
        if self._responses_create is not None:
            call_kwargs = self._prepare_responses_kwargs(call_kwargs)
        # Forward the eagerly-resolved API key on every call (same rationale
        # as complete() — avoids the env-var-at-call-time race that was
        # landing "Missing Authentication header" 401s in prod).
        if self._api_key and "api_key" not in call_kwargs:
            call_kwargs["api_key"] = self._api_key
        # Omit temperature entirely for providers that reject it (see
        # ``supports_temperature`` in ``coarse.models``).
        if supports_temperature(self._model):
            call_kwargs.setdefault("temperature", temperature)
        if self._responses_create is not None:
            response = _responses_completion(
                model=self._model,
                messages=messages,
                max_output_tokens=clamped,
                timeout=timeout,
                **call_kwargs,
            )
        else:
            response = _sanitized_completion(
                model=self._model,
                messages=messages,
                max_tokens=clamped,
                timeout=timeout,
                **call_kwargs,
            )
        try:
            cost = _completion_cost_with_long_context_pricing(response, self._model)
            if cost is not None:
                self.add_cost(cost)
        except Exception:
            logger.debug("Cost tracking failed for model %s", self._model, exc_info=True)

        content = (
            response.output_text
            if self._responses_create is not None
            else response.choices[0].message.content
        )
        if not content or not content.strip():
            raise ValueError(f"Model {self._model} returned empty response")
        return _CTRL_CHAR_RE.sub("", content).replace("\\u0000", "").strip()

    def add_cost(self, cost_usd: float) -> None:
        """Register an external cost (e.g. from a direct litellm.completion call)."""
        with self._lock:
            self._cost_usd += cost_usd
            total_cost = self._cost_usd
        if self._cost_callback is None:
            return
        try:
            self._cost_callback(total_cost)
        except Exception:
            logger.debug("Cost callback failed for model %s", self._model, exc_info=True)

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
        """Whether the model's provider requires explicit cache_control blocks.

        Covers every provider that (per OpenRouter's prompt-caching docs,
        verified 2026-04-11) requires the caller to emit Anthropic-style
        ``cache_control: {type: "ephemeral"}`` blocks to enable caching:

        - **Anthropic Claude** (``anthropic/claude-*``,
          ``openrouter/anthropic/claude-*``, direct/Bedrock/Vertex
          routing — matched by either the ``anthropic`` or ``claude``
          substring to catch ``vertex_ai/claude-*`` forms).
        - **Google Gemini** (``gemini/*``, ``google/gemini-*``,
          ``openrouter/google/gemini-*``). Per
          https://openrouter.ai/docs/guides/best-practices/prompt-caching:
          "Gemini caching in OpenRouter requires you to insert
          cache_control breakpoints explicitly within message content."

        NOT covered (deliberately):

        - **OpenAI** — auto-caches prompt prefixes >=1024 tokens on its
          side. Emitting ``cache_control`` blocks is harmless but
          unnecessary, so we keep the signal False for OpenAI models
          to avoid cluttering requests with no-op metadata.
        - **DeepSeek** — auto-caches server-side, same story.
        - Other providers (Qwen, Mistral, Moonshot, z-ai, x-ai, etc.)
          are undocumented; we don't emit blocks to untested providers.

        Cost impact when enabled: cache writes bill at 1.25× input,
        reads at 0.1× (90% off). Break-even at 0.28 reads per write.
        Section-agent system prompts are shared across N parallel
        calls (N=8-25 typically), so one cache_control block per
        section-agent system + paper-context prefix clears break-even
        on the first cache read.
        """
        lower = self._model.lower()
        return any(p in lower for p in ("anthropic", "claude", "gemini"))


def _normalize_model(model: str, config: CoarseConfig | None = None) -> str:
    """Ensure model string has the right provider prefix for litellm routing.

    If the named direct provider has no key (env or config) and an OpenRouter
    key is available, rewrite to 'openrouter/<model>' so the call goes through
    OpenRouter. Config-file keys count — not just env vars.
    """
    # OpenRouter's own meta-models (e.g. openrouter/fusion) live under the
    # `openrouter/` vendor namespace, which collides with litellm's
    # provider-routing prefix: litellm strips the leading `openrouter/` and
    # would POST a bare `fusion`, which OpenRouter 502s on. Double the slug so
    # litellm forwards the canonical id intact. Idempotent — the doubled form
    # already starts with `openrouter/` and falls through the guard below.
    if model in OPENROUTER_NAMESPACE_MODELS:
        return "openrouter/" + model
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
        # Kimi works better via OpenRouter's native json_object path than
        # markdown-fenced JSON prompts. If the route rejects structured
        # params, complete() falls back to MD_JSON.
        if _is_openrouter_kimi_model(lower):
            return instructor.Mode.JSON
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


def _select_fallback_instructor_mode(
    model: str,
    primary_mode: instructor.Mode,
) -> instructor.Mode | None:
    """Return a structured-output fallback mode for models with flaky JSON support."""
    if _is_openrouter_kimi_model(model) and primary_mode == instructor.Mode.JSON:
        return instructor.Mode.MD_JSON
    return None


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
    candidates: list[str] = [model]

    if "/" in model:
        candidates.append(model.split("/", 1)[1])

    if model.startswith("openrouter/"):
        deproxied = model.removeprefix("openrouter/")
        candidates.append(deproxied)
        if "/" in deproxied:
            candidates.append(deproxied.split("/", 1)[1])
    elif "/" in model:
        # Some entries only exist under the openrouter/ form in litellm's
        # registry, so try that variant for bare provider/model strings.
        candidates.append("openrouter/" + model)

    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        info = litellm.model_cost.get(candidate)
        if info is not None:
            return info
    return None


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


def model_cost_per_token(model: str, prompt_tokens: int = 0) -> tuple[float, float]:
    """Return (input_cost_per_token, output_cost_per_token) for a given model.

    Accepts litellm model strings (e.g. 'openai/gpt-4o' or 'gpt-4o'). When
    ``prompt_tokens`` crosses a registered long-context threshold, returns that
    tier's rates. Returns (0.0, 0.0) if model not found.
    """
    costs = _lookup_model_cost(model)
    if costs is None:
        return (0.0, 0.0)
    input_cost = costs.get("input_cost_per_token", 0.0)
    output_cost = costs.get("output_cost_per_token", 0.0)
    selected_threshold = -1
    for key, tier_input_cost in costs.items():
        match = re.fullmatch(r"input_cost_per_token_above_(\d+)k_tokens", key)
        if match is None:
            continue
        threshold = int(match.group(1)) * 1_000
        if prompt_tokens < threshold or threshold <= selected_threshold:
            continue
        tier_output_cost = costs.get(f"output_cost_per_token_above_{match.group(1)}k_tokens")
        if tier_output_cost is None:
            continue
        selected_threshold = threshold
        input_cost = tier_input_cost
        output_cost = tier_output_cost
    return (input_cost, output_cost)


def _completion_cost_with_long_context_pricing(response, model: str) -> float | None:
    """Return LiteLLM's actual cost, corrected for prompt-length price tiers.

    LiteLLM applies several provider-specific long-context fields, but not all
    OpenRouter thresholds (notably Qwen's 256k tier). Use the response usage to
    compute a conservative tier-aware floor, while retaining any higher cost
    LiteLLM reports for cache, routing, or provider-specific charges.
    """
    standard_cost = litellm.completion_cost(completion_response=response, model=model)
    usage = getattr(response, "usage", None)
    prompt_tokens = max(
        0,
        int(getattr(usage, "prompt_tokens", getattr(usage, "input_tokens", 0)) or 0),
    )
    completion_tokens = max(
        0,
        int(getattr(usage, "completion_tokens", getattr(usage, "output_tokens", 0)) or 0),
    )
    base_rates = model_cost_per_token(model)
    tier_rates = model_cost_per_token(model, prompt_tokens=prompt_tokens)
    if tier_rates == base_rates:
        return standard_cost
    tier_cost_floor = prompt_tokens * tier_rates[0] + completion_tokens * tier_rates[1]
    return max(float(standard_cost or 0.0), tier_cost_floor)


# Reasoning-token overhead multiplier for cost estimation.
#
# Reasoning models bill hidden reasoning tokens at the *output* rate, and
# those tokens do not show up in the `tokens_out` budget the caller asked
# for. This multiplier adds that overhead so the pre-flight gate doesn't
# under-quote reasoning models.
#
# Calibrated against the per-stage output budgets in pipeline_spec, which are
# now *expected* output (not max_tokens ceilings). With realistic output
# budgets, 1.5x is a sensible billable overhead for reasoning_effort="medium".
# The previous 4x — calibrated when the budgets WERE the ceilings — compounded
# into a large over-quote for expensive reasoning models (GPT-5.5 ~$81/paper).
# Keep in lockstep with pipeline_spec.REASONING_OVERHEAD_MULTIPLIER.
#
# Note: this is the *cost overhead* multiplier. The request-budget
# multiplier is 8x and lives in `models.py::REASONING_MAX_TOKENS_MULTIPLIER` —
# they're intentionally asymmetric because reasoning_effort="medium" is
# expected to cap actual usage well below the raised ceiling. If you change
# one, check the other.
_REASONING_OVERHEAD_MULTIPLIER: float = 1.5


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
    input_cost, output_cost = model_cost_per_token(model, prompt_tokens=tokens_in)
    reasoning_overhead = estimate_reasoning_overhead_tokens(model, tokens_out)
    return input_cost * tokens_in + output_cost * (tokens_out + reasoning_overhead)
