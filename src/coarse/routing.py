"""Per-stage model routing for the review pipeline.

coarse's pipeline has ~10 LLM-backed stages with very different complexity
profiles. Some (metadata classification, math-section detection) are
structured classification calls that an OSS model handles fine; others
(overview, section, editorial) need SOTA reasoning. Historically every
stage used the same `LLMClient`, so passing `--model claude-opus-4.6`
forced opus rates for the trivial stages too.

`StageRouter` resolves a per-stage `LLMClient` at construction time,
caches one instance per unique resolved model, and returns the right
client for each stage name. See gh issue #46 for the stage classification
and src/coarse/models.py::STAGE_MODELS for the default cheap-tier
assignments.

Extraction QA and literature search are intentionally NOT routed through
the router today — both have bespoke model defaults (vision model,
Perplexity) that are plumbed inside their own modules. Adding them to
the router would require refactoring extraction_qa.py and literature.py
and is deferred.
"""

from __future__ import annotations

from typing import Final

from coarse.config import CoarseConfig, load_config
from coarse.llm import LLMClient
from coarse.models import (
    CHEAP_STAGE_FALLBACK_MODEL,
    CHEAP_STAGE_MODEL,
    CHEAP_STAGE_PROVIDERS,
    STAGE_MODELS,
)

# LLM-consuming stages the router is responsible for. Mirrors the stages
# in src/coarse/cost.py::build_cost_estimate that use the review model
# (NOT literature_search or extraction_qa, which have bespoke defaults
# handled in their own modules).
#
# Adding a stage here without also wiring it in pipeline.py via
# router.client_for("<stage>") will result in the override being silently
# ignored at runtime — a test in test_routing.py guards against that
# by round-tripping every stage through both the router and the pipeline
# test-harness.
STAGE_NAMES: Final[tuple[str, ...]] = (
    "metadata",
    "math_detection",
    "contribution_extraction",
    "calibration",
    "overview",
    "completeness",
    "section",
    "cross_section",
    "verify",
    "editorial",
)


class StageRouter:
    """Resolve per-stage ``LLMClient`` instances for the review pipeline.

    Construction order:
    1. Start from ``base_model`` (typically the user's ``--model`` choice
       or ``config.default_model``).
    2. Apply the ``STAGE_MODELS`` defaults from ``models.py`` — the
       cheap-tier override for stages that don't need SOTA reasoning.
    3. Apply the caller's ``overrides`` on top (CLI ``--stage-override``
       takes precedence over the default map).
    4. For each resolved model, lazily construct and cache one
       ``LLMClient``. Stages that resolve to the same model share a
       client — there are at most N distinct clients for N distinct
       resolved models.

    Construction is lazy: no ``LLMClient`` is built until
    ``.client_for(stage)`` is called. ``.cost_usd`` sums across all
    currently-cached clients.

    When the resolved model for a stage is ``CHEAP_STAGE_MODEL``, the
    client is constructed with ``provider_allowlist=CHEAP_STAGE_PROVIDERS``
    so request data stays on US-HQ providers (see models.py for why),
    AND a fallback client for ``CHEAP_STAGE_FALLBACK_MODEL`` (kimi-k2.5)
    is pre-built and attached via the primary client's ``fallback_client``
    kwarg. Both primary and fallback are cached so their cumulative costs
    both flow into ``.cost_usd``. Other models get the default client
    with no allowlist and no fallback.
    """

    def __init__(
        self,
        *,
        base_model: str,
        overrides: dict[str, str] | None = None,
        config: CoarseConfig | None = None,
    ) -> None:
        if config is None:
            config = load_config()
        self._base_model = base_model
        self._config = config
        self._clients: dict[str, LLMClient] = {}

        # Validate stage names eagerly — catches typos in the CLI
        # ``--stage-override`` flag at construction time rather than at
        # first use.
        caller_overrides = dict(overrides or {})
        unknown = [s for s in caller_overrides if s not in STAGE_NAMES]
        if unknown:
            raise ValueError(
                f"Unknown stage name(s) in overrides: {sorted(unknown)}. "
                f"Valid stages: {sorted(STAGE_NAMES)}"
            )

        # Merge STAGE_MODELS defaults with caller-supplied overrides. Caller
        # wins. This is the single source of merge truth — callers should
        # NOT pre-merge STAGE_MODELS themselves (it would be a no-op now
        # but would drift the documented contract).
        self._overrides: dict[str, str] = {**STAGE_MODELS, **caller_overrides}

    def _resolve_model(self, stage: str) -> str:
        """Return the effective model ID for a stage (override → base)."""
        return self._overrides.get(stage, self._base_model)

    def client_for(self, stage: str) -> LLMClient:
        """Return the ``LLMClient`` for a named pipeline stage.

        Cached by resolved model ID so two stages routed to the same model
        share a client (and its cumulative cost counter). Raises on
        unknown stage names.
        """
        if stage not in STAGE_NAMES:
            raise ValueError(f"Unknown stage '{stage}'. Valid stages: {sorted(STAGE_NAMES)}")
        model = self._resolve_model(stage)
        cached = self._clients.get(model)
        if cached is not None:
            return cached
        client = self._build_client(model)
        self._clients[model] = client
        return client

    # Disable glm-5.1's default reasoning / thinking. Empirically confirmed
    # on 2026-04-11: glm-5.1 via OpenRouter defaults to thinking-on and
    # emits invisible reasoning preamble that counts against max_tokens.
    # Structured-output calls with max_tokens<=2048 (metadata 256,
    # math_detection 1024, calibration 2048, contribution_extraction
    # 2048) consistently hit IncompleteOutputException because the
    # preamble exhausts the budget before any JSON is emitted. OpenRouter's
    # `reasoning: {effort: "none"}` shape is the documented way to
    # disable reasoning entirely — it stops the model from thinking at
    # all, so those tokens don't eat into the visible-output budget.
    # See https://openrouter.ai/docs/guides/best-practices/reasoning-tokens.
    _CHEAP_STAGE_EXTRA_BODY: Final[dict] = {"reasoning": {"effort": "none"}}

    def _build_client(self, model: str) -> LLMClient:
        """Construct an ``LLMClient`` for ``model`` with the right wrapping.

        The cheap-tier primary model (``CHEAP_STAGE_MODEL``) gets:
        - ``provider_allowlist=CHEAP_STAGE_PROVIDERS`` (US-HQ only routing)
        - ``default_extra_body={"reasoning": {"effort": "none"}}`` so
          glm-5.1's default thinking mode doesn't consume max_tokens
          before any JSON emits
        - ``fallback_client`` pointing at a pre-built kimi-k2.5 client
          that has its own allowlist and uses MD_JSON instructor mode

        Other models get a plain client with no allowlist and no fallback.

        Side effect: when building the cheap-tier primary, we ALSO register
        the fallback client under its own model key in ``self._clients``
        so its cost shows up in ``.cost_usd`` even though it's only
        discovered transitively.
        """
        if model == CHEAP_STAGE_MODEL:
            # Also disable reasoning on the kimi fallback — it's cheaper,
            # faster, and matches the primary's behavior. The fallback
            # uses MD_JSON mode, not JSON mode, but reasoning disable is
            # independent of instructor mode.
            fallback = LLMClient(
                model=CHEAP_STAGE_FALLBACK_MODEL,
                config=self._config,
                provider_allowlist=CHEAP_STAGE_PROVIDERS,
                default_extra_body=self._CHEAP_STAGE_EXTRA_BODY,
            )
            # Cache the fallback so router.cost_usd sums its cost too.
            self._clients[fallback.model] = fallback
            return LLMClient(
                model=model,
                config=self._config,
                provider_allowlist=CHEAP_STAGE_PROVIDERS,
                fallback_client=fallback,
                default_extra_body=self._CHEAP_STAGE_EXTRA_BODY,
            )
        return LLMClient(model=model, config=self._config)

    @property
    def cost_usd(self) -> float:
        """Sum ``cost_usd`` across every cached client."""
        return sum(c.cost_usd for c in self._clients.values())

    @property
    def base_model(self) -> str:
        return self._base_model

    @property
    def base_client(self) -> LLMClient:
        """Return the ``LLMClient`` for the base model, NOT any stage.

        Used by non-stage-routed consumers like ``search_literature`` that
        want a plain client on the user's chosen model without going through
        the stage map. The client is cached under the base model's key, so
        its cost flows into ``.cost_usd`` just like any stage client.
        """
        cached = self._clients.get(self._base_model)
        if cached is not None:
            return cached
        client = self._build_client(self._base_model)
        self._clients[self._base_model] = client
        return client
