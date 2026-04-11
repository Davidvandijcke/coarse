"""Tests for the per-stage model router (src/coarse/routing.py)."""

from __future__ import annotations

import pytest

from coarse.config import CoarseConfig
from coarse.models import CHEAP_STAGE_MODEL, CHEAP_STAGE_PROVIDERS
from coarse.routing import STAGE_NAMES, StageRouter

_BASE = "openrouter/fake-base-model"


def _router(**kwargs) -> StageRouter:
    """Construct a router with a dummy config and a fake base model."""
    kwargs.setdefault("base_model", _BASE)
    kwargs.setdefault("config", CoarseConfig())
    return StageRouter(**kwargs)


def test_stage_names_covers_all_review_model_stages():
    """STAGE_NAMES should document every review-model stage the pipeline
    actually routes through the router. Regression guard against adding a
    stage to pipeline.py and forgetting to register it here."""
    expected = {
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
    }
    assert set(STAGE_NAMES) == expected


def test_router_returns_same_client_for_stages_without_overrides():
    """Two stages that resolve to the same model share a single LLMClient
    (and its cumulative cost counter)."""
    router = _router()
    c1 = router.client_for("metadata")
    c2 = router.client_for("section")
    assert c1 is c2
    assert c1.model.endswith("fake-base-model")


def test_router_caches_one_client_per_unique_model():
    """Distinct override models get distinct clients, same overrides share."""
    router = _router(
        overrides={
            "metadata": "openrouter/fake-cheap",
            "math_detection": "openrouter/fake-cheap",  # shares with metadata
            "editorial": "openrouter/fake-premium",  # distinct
        }
    )
    meta = router.client_for("metadata")
    math = router.client_for("math_detection")
    editorial = router.client_for("editorial")
    section = router.client_for("section")  # base

    assert meta is math  # cached — same resolved model
    assert meta is not editorial  # different model
    assert section is not meta  # base vs. cheap override
    assert section is not editorial

    # 3 unique models total: fake-cheap, fake-premium, fake-base-model
    assert len(router._clients) == 3


def test_router_raises_on_unknown_stage_at_construction():
    """Unknown stage names in overrides fail eagerly at __init__, not
    lazily at first client_for() call. Catches CLI typos early."""
    with pytest.raises(ValueError, match="Unknown stage name"):
        _router(overrides={"metadadta": "x/y"})  # typo


def test_router_raises_on_unknown_stage_at_client_for():
    """client_for() rejects stage names not in STAGE_NAMES even if they
    weren't in overrides."""
    router = _router()
    with pytest.raises(ValueError, match="Unknown stage"):
        router.client_for("not_a_real_stage")


def test_router_wires_allowlist_for_cheap_stage_model():
    """When a stage resolves to CHEAP_STAGE_MODEL, the constructed client
    gets provider_allowlist=CHEAP_STAGE_PROVIDERS so request data stays
    on US-HQ providers even though the model weights are Chinese."""
    router = _router(overrides={"metadata": CHEAP_STAGE_MODEL})
    client = router.client_for("metadata")
    assert client._provider_allowlist == CHEAP_STAGE_PROVIDERS


def test_router_wires_kimi_fallback_for_cheap_stage_model():
    """The cheap-tier primary gets a fallback_client pointing at
    CHEAP_STAGE_FALLBACK_MODEL (kimi-k2.5), also restricted to the
    CHEAP_STAGE_PROVIDERS allowlist."""
    from coarse.models import CHEAP_STAGE_FALLBACK_MODEL

    router = _router(overrides={"metadata": CHEAP_STAGE_MODEL})
    primary = router.client_for("metadata")
    assert primary._fallback_client is not None
    fallback = primary._fallback_client
    # The fallback's model is CHEAP_STAGE_FALLBACK_MODEL, possibly with
    # an openrouter/ prefix added by _normalize_model.
    assert CHEAP_STAGE_FALLBACK_MODEL.split("/")[-1] in fallback.model
    assert fallback._provider_allowlist == CHEAP_STAGE_PROVIDERS
    # The fallback should NOT itself have a fallback (no infinite chain).
    assert fallback._fallback_client is None


def test_router_caches_fallback_so_cost_usd_includes_it():
    """The router caches the pre-built fallback under its own model key
    so router.cost_usd aggregates both primary and fallback costs even
    when callers never explicitly request the fallback."""
    router = _router(overrides={"metadata": CHEAP_STAGE_MODEL})
    primary = router.client_for("metadata")
    fallback = primary._fallback_client
    assert fallback is not None

    primary.add_cost(0.05)
    fallback.add_cost(0.02)
    # Router sums across all cached clients
    assert abs(router.cost_usd - 0.07) < 1e-9


def test_router_does_not_wire_allowlist_for_other_models():
    """Non-cheap-tier clients don't get a provider_allowlist — they route
    normally via OpenRouter's default provider selection. They also don't
    get a fallback_client — fallback is only wired for the cheap tier."""
    router = _router(overrides={"metadata": "openrouter/some/other-model"})
    client = router.client_for("metadata")
    assert client._provider_allowlist is None
    assert client._fallback_client is None


def test_router_cost_usd_sums_across_cached_clients():
    """Router.cost_usd aggregates per-client costs."""
    router = _router(overrides={"metadata": "openrouter/fake-cheap"})
    meta = router.client_for("metadata")
    section = router.client_for("section")
    # Manually register fake costs (production code uses add_cost from
    # the completion-cost path)
    meta.add_cost(0.01)
    section.add_cost(0.05)
    assert abs(router.cost_usd - 0.06) < 1e-9


def test_router_base_model_property():
    router = _router()
    assert router.base_model == _BASE


# ---------------------------------------------------------------------------
# Phase 1 — STAGE_MODELS policy (cheap-tier routing for 4 classification stages)
# ---------------------------------------------------------------------------


def test_stage_models_values_are_module_constants():
    """Every value in STAGE_MODELS must be IDENTICAL (by id()) to a
    constant declared in coarse.models — not a string literal. Regression
    guard against someone pasting a raw model ID into the dict, which
    would bypass the security scanner's model-id rule and skip the
    versioning discipline documented in CLAUDE.md.
    """
    import coarse.models as models_mod

    constants = {
        id(v)
        for name, v in vars(models_mod).items()
        if isinstance(v, str) and name.isupper() and not name.startswith("_")
    }
    from coarse.models import STAGE_MODELS

    for stage, model in STAGE_MODELS.items():
        assert id(model) in constants, (
            f"STAGE_MODELS[{stage!r}] = {model!r} is not one of models.py's declared "
            f"string constants — use an imported constant, not a literal."
        )


def test_stage_models_covers_cheap_classification_stages():
    """The four cheap-safe stages classified in gh #46 should all map
    to CHEAP_STAGE_MODEL. This is a policy pin, not a mechanism check —
    if the policy changes, update this test alongside STAGE_MODELS."""
    from coarse.models import STAGE_MODELS

    assert set(STAGE_MODELS.keys()) == {
        "metadata",
        "math_detection",
        "contribution_extraction",
        "calibration",
    }
    assert all(model == CHEAP_STAGE_MODEL for model in STAGE_MODELS.values())


def test_router_routes_cheap_stages_with_empty_overrides():
    """Integration check: with STAGE_MODELS populated and no explicit
    overrides, a router built with the default base model still routes
    the 4 cheap stages through CHEAP_STAGE_MODEL when the pipeline
    merges STAGE_MODELS into its effective overrides (mirroring what
    review_paper() does)."""
    from coarse.models import STAGE_MODELS as STAGE_MODELS_LIVE

    router = _router(overrides=dict(STAGE_MODELS_LIVE))

    for cheap_stage in ("metadata", "math_detection", "contribution_extraction", "calibration"):
        client = router.client_for(cheap_stage)
        # Router normalizes the model ID, so check the underlying slug
        # appears in the client's resolved model.
        assert "glm-5.1" in client.model
        # Cheap-tier clients get the US-HQ allowlist.
        assert client._provider_allowlist == CHEAP_STAGE_PROVIDERS
