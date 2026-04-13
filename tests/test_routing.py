"""Tests for the stage-routing kill switch and override precedence."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from coarse.config import CoarseConfig
from coarse.models import CHEAP_STAGE_MODEL, STAGE_MODELS
from coarse.routing import STAGE_NAMES, StageRouter, _stage_routing_disabled


@pytest.fixture()
def fake_llm_client():
    """Replace LLMClient with a MagicMock factory so StageRouter.client_for returns mocks."""

    def factory(**kwargs):
        client = MagicMock()
        client.model = kwargs.get("model", "unknown")
        return client

    with patch("coarse.routing.LLMClient", side_effect=factory) as mock_factory:
        yield mock_factory


def test_stage_routing_disabled_reads_env_truthy(monkeypatch):
    """Any non-falsy value of COARSE_DISABLE_STAGE_ROUTING flips the switch."""
    for truthy in ("1", "true", "TRUE", "yes", "on", "anything-else"):
        monkeypatch.setenv("COARSE_DISABLE_STAGE_ROUTING", truthy)
        assert _stage_routing_disabled() is True, f"{truthy!r} should be truthy"


def test_stage_routing_disabled_reads_env_falsy(monkeypatch):
    """Falsy and unset values leave the legacy cheap-tier routing in place."""
    for falsy in ("", "0", "false", "FALSE", "no", "off"):
        monkeypatch.setenv("COARSE_DISABLE_STAGE_ROUTING", falsy)
        assert _stage_routing_disabled() is False, f"{falsy!r} should be falsy"
    monkeypatch.delenv("COARSE_DISABLE_STAGE_ROUTING", raising=False)
    assert _stage_routing_disabled() is False


def test_kill_switch_unset_uses_cheap_stage_defaults(monkeypatch, fake_llm_client):
    """Baseline: without the kill switch, cheap-safe stages route to CHEAP_STAGE_MODEL."""
    monkeypatch.delenv("COARSE_DISABLE_STAGE_ROUTING", raising=False)
    router = StageRouter(
        base_model="anthropic/claude-opus-4.6",
        config=CoarseConfig(),
    )
    for stage in STAGE_MODELS:
        assert router._resolve_model(stage) == CHEAP_STAGE_MODEL


def test_kill_switch_set_routes_every_stage_to_base_model(monkeypatch, fake_llm_client):
    """Hosted-mode behavior: every stage uses the caller's base_model."""
    monkeypatch.setenv("COARSE_DISABLE_STAGE_ROUTING", "1")
    router = StageRouter(
        base_model="anthropic/claude-opus-4.6",
        config=CoarseConfig(),
    )
    for stage in STAGE_NAMES:
        assert router._resolve_model(stage) == "anthropic/claude-opus-4.6", (
            f"{stage} must fall through to base_model when kill switch is on"
        )


def test_kill_switch_preserves_explicit_cli_overrides(monkeypatch, fake_llm_client):
    """CLI --stage-override values still win over the kill switch's base_model fallback.

    The kill switch exists to stop the *default* cheap-tier rewriting, not
    to stomp on explicit user overrides. A reviewer who passed
    `--stage-override metadata=openai/gpt-5-mini` still gets gpt-5-mini.
    """
    monkeypatch.setenv("COARSE_DISABLE_STAGE_ROUTING", "1")
    router = StageRouter(
        base_model="anthropic/claude-opus-4.6",
        overrides={"metadata": "openai/gpt-5-mini"},
        config=CoarseConfig(),
    )
    assert router._resolve_model("metadata") == "openai/gpt-5-mini"
    # Non-overridden cheap-safe stage still falls through to base_model,
    # not to the old CHEAP_STAGE_MODEL.
    assert router._resolve_model("math_detection") == "anthropic/claude-opus-4.6"


def test_kill_switch_client_for_skips_cheap_tier_client_build(monkeypatch, fake_llm_client):
    """With the switch on, we never construct the cheap-tier primary+fallback pair."""
    monkeypatch.setenv("COARSE_DISABLE_STAGE_ROUTING", "1")
    router = StageRouter(
        base_model="anthropic/claude-opus-4.6",
        config=CoarseConfig(),
    )
    router.client_for("metadata")
    # The cheap-tier branch in _build_client builds a fallback kimi client
    # with provider_allowlist=CHEAP_STAGE_PROVIDERS. If the switch is on,
    # we should never pass provider_allowlist — only a plain base-model
    # client.
    calls = fake_llm_client.call_args_list
    assert all("provider_allowlist" not in c.kwargs for c in calls), (
        "cheap-tier allowlist path ran even with the kill switch on"
    )
    assert all("fallback_client" not in c.kwargs for c in calls), (
        "cheap-tier fallback client got built even with the kill switch on"
    )
