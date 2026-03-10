"""Tests for coarse.cost — cost estimation and approval gate."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from coarse.config import CoarseConfig
from coarse.cost import build_cost_estimate, confirm_or_abort, run_cost_gate
from coarse.types import CostEstimate, CostStage, PaperText


def _paper(tokens: int = 10_000) -> PaperText:
    return PaperText(full_markdown="x", token_estimate=tokens)


def _config(model: str = "openai/gpt-4o", max_cost: float = 10.0) -> CoarseConfig:
    return CoarseConfig(default_model=model, max_cost_usd=max_cost)


# ---------------------------------------------------------------------------
# build_cost_estimate
# ---------------------------------------------------------------------------

def test_build_cost_estimate_returns_all_stages():
    estimate = build_cost_estimate(_paper(), _config(), section_count=8)
    names = [s.name for s in estimate.stages]
    assert "metadata" in names
    # 3 overview judges + synthesis
    overview_stages = [n for n in names if n.startswith("overview_")]
    assert len(overview_stages) == 4  # 3 judges + 1 synthesis
    assert "crossref" in names
    assert "critique" in names
    section_stages = [n for n in names if n.startswith("section_")]
    assert len(section_stages) == 8
    assert "extraction_qa" in names
    assert "pdf_extraction" in names
    assert "calibration" in names
    assert "literature_search" in names
    # Total: pdf_extraction + metadata + calibration + literature_search + 3 overview judges + overview_synthesis + 8 sections + crossref + critique + extraction_qa = 19
    assert len(estimate.stages) == 19


def test_build_cost_estimate_zero_cost_unknown_model():
    config = _config(model="unknown/totally-fake-model")
    config = config.model_copy(update={"extraction_qa": False})
    with patch.dict("os.environ", {"OPENROUTER_API_KEY": ""}, clear=False):
        estimate = build_cost_estimate(_paper(), config)
    assert len(estimate.stages) > 0
    # pdf_extraction stage has fixed cost; all LLM stages should be zero for unknown model
    llm_stages = [s for s in estimate.stages if s.name != "pdf_extraction"]
    assert all(s.estimated_cost_usd == 0.0 for s in llm_stages)


def test_total_cost_matches_sum_with_buffer():
    estimate = build_cost_estimate(_paper(), _config())
    stage_sum = sum(s.estimated_cost_usd for s in estimate.stages)
    # total_cost_usd includes 1.15x conservative buffer
    assert abs(estimate.total_cost_usd - stage_sum * 1.15) < 1e-10


def test_section_count_respected():
    estimate = build_cost_estimate(_paper(), _config(), section_count=5)
    section_stages = [s for s in estimate.stages if s.name.startswith("section_")]
    assert len(section_stages) == 5


# ---------------------------------------------------------------------------
# confirm_or_abort
# ---------------------------------------------------------------------------

def _make_estimate(cost: float) -> CostEstimate:
    stage = CostStage(
        name="test",
        model="openai/gpt-4o",
        estimated_tokens_in=1000,
        estimated_tokens_out=500,
        estimated_cost_usd=cost,
    )
    return CostEstimate(stages=[stage], total_cost_usd=cost)


def test_confirm_or_abort_exceeds_max_raises():
    estimate = _make_estimate(5.0)
    with pytest.raises(SystemExit):
        confirm_or_abort(estimate, max_cost_usd=2.0)


def test_confirm_or_abort_user_declines_raises():
    estimate = _make_estimate(1.0)
    with patch("typer.confirm", return_value=False):
        with pytest.raises(SystemExit):
            confirm_or_abort(estimate, max_cost_usd=10.0)


def test_confirm_or_abort_user_accepts_returns():
    estimate = _make_estimate(1.0)
    with patch("typer.confirm", return_value=True):
        confirm_or_abort(estimate, max_cost_usd=10.0)  # should not raise


def test_confirm_or_abort_negligible_skips_prompt():
    estimate = _make_estimate(0.005)
    # No typer.confirm call expected; should return without raising
    confirm_or_abort(estimate, max_cost_usd=10.0)


def test_confirm_or_abort_non_tty_treated_as_approved():
    estimate = _make_estimate(1.0)
    with patch("typer.confirm", side_effect=Exception("not a tty")):
        confirm_or_abort(estimate, max_cost_usd=10.0)  # should not raise


# ---------------------------------------------------------------------------
# run_cost_gate
# ---------------------------------------------------------------------------

def test_run_cost_gate_returns_estimate():
    paper = _paper(tokens=5000)
    config = _config()
    with (
        patch("coarse.cost.display_cost_estimate"),
        patch("coarse.cost.confirm_or_abort"),
    ):
        result = run_cost_gate(paper, config)
    assert isinstance(result, CostEstimate)
    assert len(result.stages) > 0
    stage_sum = sum(s.estimated_cost_usd for s in result.stages)
    # total_cost_usd includes 1.15x conservative buffer
    assert abs(result.total_cost_usd - stage_sum * 1.15) < 1e-10


# ---------------------------------------------------------------------------
# extraction_qa cost stage
# ---------------------------------------------------------------------------

def test_extraction_qa_stage_present_when_enabled():
    config = CoarseConfig(extraction_qa=True)
    estimate = build_cost_estimate(_paper(), config)
    names = [s.name for s in estimate.stages]
    assert "extraction_qa" in names
    qa_stage = next(s for s in estimate.stages if s.name == "extraction_qa")
    assert qa_stage.model == config.vision_model


def test_extraction_qa_stage_absent_when_disabled():
    config = CoarseConfig(extraction_qa=False)
    estimate = build_cost_estimate(_paper(), config)
    names = [s.name for s in estimate.stages]
    assert "extraction_qa" not in names
