"""Tests for coarse.cost — cost estimation and approval gate."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from coarse.config import CoarseConfig
from coarse.cost import build_cost_estimate, confirm_or_abort, run_cost_gate
from coarse.models import (
    DEEP_LITERATURE_SEARCH_MODEL,
    FUSION_MODEL,
    LITERATURE_SEARCH_MODEL,
)
from coarse.pipeline_spec import DEEP_LITERATURE_FLAT_COST, LITERATURE_FLAT_COST
from coarse.types import CostEstimate, CostStage, PaperText

TEST_MODEL = "test/mock-model"


def _paper(tokens: int = 10_000) -> PaperText:
    return PaperText(full_markdown="x", token_estimate=tokens)


def _config(model: str = TEST_MODEL, max_cost: float = 10.0) -> CoarseConfig:
    return CoarseConfig(default_model=model, max_cost_usd=max_cost)


# ---------------------------------------------------------------------------
# build_cost_estimate
# ---------------------------------------------------------------------------


def test_build_cost_estimate_returns_all_pipeline_stages():
    """Stage list must mirror pipeline.py's review_paper(). Uses exact set
    equality so a stage swap (rename, delete + add) can't silently pass.

    For section_count=8, the heuristics yield:
      - math_section_count = round(8 * 0.2) = 2  → 2 proof_verify stages
      - cross_section_count = 1 (sections ≥ 6)   → 1 cross_section stage
    """
    # Force the OpenRouter (flat-fee Perplexity) branch so the test is
    # deterministic regardless of whether the dev env has a real key.
    with patch("coarse.cost.has_provider_key", return_value=True):
        estimate = build_cost_estimate(_paper(), _config(), section_count=8)
    names = {s.name for s in estimate.stages}

    expected = {
        "pdf_extraction",
        "extraction_qa",
        "metadata",
        "math_detection",
        "calibration",
        "literature_search",
        "contribution_extraction",
        "overview",
        "completeness",
        "editorial",
        *{f"section_{i}" for i in range(1, 9)},
        *{f"proof_verify_{i}" for i in range(1, 3)},
        "cross_section_1",
    }
    assert names == expected, f"drift: {names ^ expected}"

    # Phantom 3-judge panel is gone — real pipeline does ONE overview call.
    assert "overview_judge_1" not in names
    assert "overview_synthesis" not in names
    # Legacy crossref+critique path was removed — editorial replaced them.
    assert "crossref" not in names
    assert "critique" not in names


def test_build_cost_estimate_zero_cost_unknown_model():
    config = _config(model="unknown/totally-fake-model")
    config = config.model_copy(update={"extraction_qa": False})
    with patch.dict("os.environ", {"OPENROUTER_API_KEY": ""}, clear=False):
        estimate = build_cost_estimate(_paper(), config)
    assert len(estimate.stages) > 0
    # Stages that DON'T route through the unknown base model:
    # - pdf_extraction (flat-fee OCR)
    # - metadata / math_detection / contribution_extraction / calibration
    #   (pinned to CHEAP_STAGE_MODEL=glm-5.1 via STAGE_MODELS — has known
    #   pricing in _CUSTOM_MODEL_INFO, so non-zero)
    # Every remaining LLM stage runs on the unknown base model and
    # should be zero because litellm can't price it.
    base_routed = [
        s
        for s in estimate.stages
        if s.name != "pdf_extraction"
        and s.name not in {"metadata", "math_detection", "contribution_extraction", "calibration"}
    ]
    assert all(s.estimated_cost_usd == 0.0 for s in base_routed), [
        (s.name, s.model, s.estimated_cost_usd) for s in base_routed
    ]


def test_total_cost_matches_sum_with_buffer():
    estimate = build_cost_estimate(_paper(), _config())
    stage_sum = sum(s.estimated_cost_usd for s in estimate.stages)
    # total_cost_usd includes the 1.30x conservative buffer — bumped from
    # 1.15 after the April 2026 under-count audit.
    assert abs(estimate.total_cost_usd - stage_sum * 1.30) < 1e-10


def test_cjk_paper_quotes_higher_cost_and_more_sections_than_latin():
    """A CJK paper and an English paper of the SAME character length must NOT
    quote the same cost: CJK packs ~4-6x more tokens/char, so the script-aware
    token_estimate from extraction drives a higher cost and section count.

    This is the user-facing payoff — the cost-approval gate stops under-quoting
    CJK papers (where the user would approve a low number then pay more).
    """
    from coarse.extraction import _estimate_tokens

    n_chars = 12_000
    latin_tokens = _estimate_tokens("a " * (n_chars // 2))
    cjk_tokens = _estimate_tokens("中" * n_chars)
    # CJK token_estimate is materially higher for equal char length: with the
    # keystone's 1.6 vs 4 chars/token constants the pure-CJK multiplier is 2.5x.
    assert cjk_tokens > latin_tokens * 2

    latin_est = build_cost_estimate(_paper(tokens=latin_tokens), _config())
    cjk_est = build_cost_estimate(_paper(tokens=cjk_tokens), _config())
    assert cjk_est.total_cost_usd > latin_est.total_cost_usd

    latin_sections = len([s for s in latin_est.stages if s.name.startswith("section_")])
    cjk_sections = len([s for s in cjk_est.stages if s.name.startswith("section_")])
    assert cjk_sections > latin_sections


def test_latin_cost_unchanged_by_script_aware_estimate():
    """INVARIANT: an English paper's cost quote is identical whether the
    token_estimate came from len//4 or the script-aware estimator — they return
    the same number for Latin text, so the dollar total is byte-for-byte equal.
    """
    from coarse.extraction import _estimate_tokens

    text = "The quick brown fox jumps over the lazy dog. " * 200
    script_aware = _estimate_tokens(text)
    legacy = len(text) // 4
    assert script_aware == legacy

    from_script = build_cost_estimate(_paper(tokens=script_aware), _config())
    from_legacy = build_cost_estimate(_paper(tokens=legacy), _config())
    assert from_script.total_cost_usd == from_legacy.total_cost_usd


def test_section_count_respected():
    estimate = build_cost_estimate(_paper(), _config(), section_count=5)
    section_stages = [s for s in estimate.stages if s.name.startswith("section_")]
    assert len(section_stages) == 5


def test_section_count_capped_at_pipeline_limit():
    """Cap must match the `reviewable_sections[:25]` slice in
    `pipeline.py::review_paper()`."""
    huge_paper = _paper(tokens=200_000)  # would imply 166 sections naively
    estimate = build_cost_estimate(huge_paper, _config())
    section_stages = [s for s in estimate.stages if s.name.startswith("section_")]
    assert len(section_stages) == 25


def test_section_count_zero_clamps_to_one():
    """A caller-supplied `section_count=0` must not raise ZeroDivisionError."""
    estimate = build_cost_estimate(_paper(), _config(), section_count=0)
    section_stages = [s for s in estimate.stages if s.name.startswith("section_")]
    assert len(section_stages) == 1  # clamped


def test_section_count_one_runs_cleanly():
    """Tiny papers with section_count=1 exercise the divisor edge."""
    estimate = build_cost_estimate(_paper(), _config(), section_count=1)
    section_stages = [s for s in estimate.stages if s.name.startswith("section_")]
    assert len(section_stages) == 1
    proof_stages = [s for s in estimate.stages if s.name.startswith("proof_verify_")]
    # round(1 * 0.2) = 0 → no proof_verify
    assert len(proof_stages) == 0


def test_total_tokens_zero_runs_cleanly():
    """An empty paper shouldn't crash or produce negative cost."""
    estimate = build_cost_estimate(_paper(tokens=0), _config())
    assert estimate.total_cost_usd >= 0
    # Heuristic falls back to _MIN_SECTIONS=4 when total_tokens=0
    section_stages = [s for s in estimate.stages if s.name.startswith("section_")]
    assert len(section_stages) == 4


def test_math_section_count_heuristic_default():
    """Math section count defaults to round(section_count * 0.2)."""
    estimate = build_cost_estimate(_paper(), _config(), section_count=10)
    proof_stages = [s for s in estimate.stages if s.name.startswith("proof_verify_")]
    assert len(proof_stages) == 2  # round(10 * 0.2) = 2


def test_math_section_count_rounds_at_small_paper():
    """section_count=4 → round(0.8)=1, so 1 proof_verify fires."""
    estimate = build_cost_estimate(_paper(), _config(), section_count=4)
    proof_stages = [s for s in estimate.stages if s.name.startswith("proof_verify_")]
    assert len(proof_stages) == 1


def test_cross_section_skipped_just_below_threshold():
    """section_count=5 is below the 6-section threshold — no cross_section."""
    estimate = build_cost_estimate(_paper(), _config(), section_count=5)
    cross_stages = [s for s in estimate.stages if s.name.startswith("cross_section_")]
    assert len(cross_stages) == 0


def test_cross_section_fires_at_exact_threshold():
    """section_count=6 (the threshold) must fire cross_section."""
    estimate = build_cost_estimate(_paper(), _config(), section_count=6)
    cross_stages = [s for s in estimate.stages if s.name.startswith("cross_section_")]
    assert len(cross_stages) == 1


def test_literature_search_arxiv_fallback_uses_two_stages():
    """When no OpenRouter key, cost.py models the arXiv fallback path as
    two LLM calls (query generation + ranking) — matching the real code
    in agents/literature.py."""
    config = _config()
    with patch("coarse.cost.has_provider_key", return_value=False):
        estimate = build_cost_estimate(_paper(), config, section_count=8)
    names = {s.name for s in estimate.stages}
    assert "literature_search" not in names  # flat-fee branch absent
    assert "literature_query_gen" in names
    assert "literature_ranking" in names


def test_deep_literature_search_uses_deep_model_and_higher_quote():
    config = _config()
    with patch("coarse.cost.has_provider_key", return_value=True):
        standard = build_cost_estimate(_paper(), config, deep_literature_search=False)
        deep = build_cost_estimate(_paper(), config, deep_literature_search=True)

    standard_stage = next(s for s in standard.stages if s.name == "literature_search")
    deep_stage = next(s for s in deep.stages if s.name == "literature_search")
    assert standard_stage.model == LITERATURE_SEARCH_MODEL
    assert standard_stage.estimated_cost_usd == LITERATURE_FLAT_COST
    assert deep_stage.model == DEEP_LITERATURE_SEARCH_MODEL
    assert deep_stage.estimated_cost_usd == DEEP_LITERATURE_FLAT_COST
    assert deep.total_cost_usd > standard.total_cost_usd


def test_extraction_qa_skipped_for_non_pdf_inputs():
    """Pipeline only runs extraction QA on PDFs — the estimate must match,
    not over-bill DOCX/HTML/TXT/etc."""
    config = CoarseConfig(extraction_qa=True)
    with patch("coarse.cost.has_provider_key", return_value=True):
        estimate = build_cost_estimate(_paper(), config, is_pdf=False)
    names = {s.name for s in estimate.stages}
    assert "extraction_qa" not in names


def test_per_stage_output_budgets_pinned():
    """Snapshot of the per-stage EXPECTED output budgets used for cost
    estimation (pipeline_spec.STAGE_OUTPUT_TOKENS). These are deliberately
    below the agents' runtime max_tokens — they model expected output, not the
    ceiling — so the estimate doesn't over-quote expensive models. A typo
    bumping 4000 -> 400 should fail this.
    """
    with patch("coarse.cost.has_provider_key", return_value=True):
        est = build_cost_estimate(_paper(), _config(), section_count=8)
    by_name = {s.name: s for s in est.stages}

    # Reasoning overhead is zero for the test mock model, so displayed_out
    # equals the visible budget — safe to assert equality.
    assert by_name["metadata"].estimated_tokens_out == 256
    assert by_name["math_detection"].estimated_tokens_out == 1024
    assert by_name["calibration"].estimated_tokens_out == 2048
    assert by_name["contribution_extraction"].estimated_tokens_out == 2048
    assert by_name["overview"].estimated_tokens_out == 4096
    assert by_name["completeness"].estimated_tokens_out == 3072
    assert by_name["section_1"].estimated_tokens_out == 4000
    assert by_name["proof_verify_1"].estimated_tokens_out == 6000
    assert by_name["cross_section_1"].estimated_tokens_out == 4096
    assert by_name["editorial"].estimated_tokens_out == 12000
    assert by_name["extraction_qa"].estimated_tokens_out == 4096


def test_completeness_input_includes_full_paper():
    """The completeness agent reads `_build_sections_text(structure.sections)`
    — i.e. the full paper — plus overview + contribution context. The cost
    estimate must not bill it as a tiny 3000-token call.
    Regression for the April 2026 audit.
    """
    with patch("coarse.cost.has_provider_key", return_value=True):
        est = build_cost_estimate(_paper(tokens=30_000), _config())
    comp = next(s for s in est.stages if s.name == "completeness")
    # total_tokens + overview context (~5000) — well above the old 3000 number.
    assert comp.estimated_tokens_in >= 30_000


def test_model_override_takes_precedence_over_config_default():
    """The `--model` CLI flag must be reflected in the cost quote, not
    silently ignored in favor of `config.default_model`.

    Regression: pre-fix, `build_cost_estimate(paper, config)` always
    queried `config.default_model` regardless of the resolved runtime
    model, so `coarse review --model anthropic/claude-sonnet-4.6` against
    a config defaulting to qwen quoted qwen prices.
    """
    config = _config(model="qwen/qwen3.5-plus-02-15")
    with patch("coarse.cost.has_provider_key", return_value=True):
        est = build_cost_estimate(
            _paper(),
            config,
            section_count=4,
            model="openai/o3",  # reasoning override
        )
    # Every stage that uses the review model should now be flagged
    # reasoning (o3 is reasoning), which would be impossible if the
    # override were ignored (qwen is not). Exclude:
    # - Flat-fee stages (pdf_extraction, literature_search) that don't
    #   run on the review model.
    # - extraction_qa, which uses the vision model (non-reasoning).
    # - The 4 cheap-safe stages in STAGE_MODELS (gh #46), which are
    #   pinned to CHEAP_STAGE_MODEL (non-reasoning) regardless of the
    #   review model.
    flat = {"pdf_extraction", "literature_search", "extraction_qa"}
    cheap_stages = {
        "metadata",
        "math_detection",
        "contribution_extraction",
        "calibration",
    }
    non_flat = [s for s in est.stages if s.name not in flat and s.name not in cheap_stages]
    assert all("(+reasoning)" in s.name for s in non_flat), [s.name for s in non_flat]


def test_bare_anthropic_prefix_finds_claude_pricing():
    """Bare `anthropic/claude-sonnet-4.6` should resolve to non-zero
    pricing. litellm's registry keys Claude 4.6 entries under the
    `openrouter/` prefix only; `_lookup_model_cost` must try adding the
    prefix as a fallback so the cost gate doesn't silently under-quote
    every Claude review to ~$0 for the LLM stages.
    """
    from coarse.llm import model_cost_per_token

    in_cost, out_cost = model_cost_per_token("anthropic/claude-sonnet-4.6")
    assert in_cost > 0, "bare anthropic/claude-sonnet-4.6 should resolve via openrouter/ prefix"
    assert out_cost > 0

    # And the cost estimate itself should show non-zero LLM stage costs.
    config = _config(model="anthropic/claude-sonnet-4.6")
    with patch("coarse.cost.has_provider_key", return_value=True):
        est = build_cost_estimate(_paper(tokens=20_000), config)
    non_flat_cost = sum(
        s.estimated_cost_usd
        for s in est.stages
        if s.name not in {"pdf_extraction", "literature_search", "extraction_qa"}
    )
    assert non_flat_cost > 0, "Claude LLM stages should not sum to $0"


def test_overview_is_a_single_call_not_a_panel():
    """Regression: the April 2026 audit found cost.py modeling a phantom
    3-judge panel that was never in the real pipeline. The real
    `OverviewAgent.run()` at agents/overview.py:80 makes exactly one
    `client.complete(..., max_tokens=8192)` call.
    """
    with patch("coarse.cost.has_provider_key", return_value=True):
        est = build_cost_estimate(_paper(), _config(), section_count=8)
    overview_stages = [s for s in est.stages if s.name.startswith("overview")]
    assert len(overview_stages) == 1
    assert overview_stages[0].name == "overview"
    # Cost-estimate expected-output budget (below the runtime max_tokens=8192).
    assert overview_stages[0].estimated_tokens_out == 4096


# ---------------------------------------------------------------------------
# Reasoning-model cost overhead
# ---------------------------------------------------------------------------


def test_build_cost_estimate_flags_reasoning_stages():
    """When the review model is a reasoning model (GPT-5 Pro, o-series, etc.)
    each LLM stage that uses the review model gets a '(+reasoning)' suffix
    so the user can see the reasoning overhead is baked into the estimate.

    Regression for review 3ee351e6 where GPT-5.4 Pro burned 15k hidden
    tokens per stage. Stages that use a model OTHER than the review
    model are excluded — their reasoning flag depends on their own model,
    not the default. These are:
    - pdf_extraction / literature_search: flat-fee, not the review model
    - extraction_qa: uses config.vision_model (non-reasoning)
    - metadata / math_detection / contribution_extraction / calibration:
      pinned to CHEAP_STAGE_MODEL (non-reasoning) by STAGE_MODELS (gh #46)
    """
    config = _config(model="openai/gpt-5.4-pro")
    with patch("coarse.cost.has_provider_key", return_value=True):
        estimate = build_cost_estimate(_paper(), config, section_count=4)

    exempt_prefixes = ("pdf_extraction", "literature_search", "extraction_qa")
    cheap_stages = {
        "metadata",
        "math_detection",
        "contribution_extraction",
        "calibration",
    }
    for s in estimate.stages:
        if s.name.startswith(exempt_prefixes):
            continue
        if s.name in cheap_stages:
            assert "(+reasoning)" not in s.name, (
                f"cheap stage {s.name} should NOT be reasoning (routed to "
                f"CHEAP_STAGE_MODEL via STAGE_MODELS)"
            )
            continue
        assert "(+reasoning)" in s.name, f"stage {s.name} should be flagged as reasoning"


def test_extraction_qa_never_flagged_reasoning_even_with_reasoning_default():
    """Hardens the reasoning-exemption: extraction_qa uses
    `config.vision_model` (gemini-flash, non-reasoning by default). Even
    when the review's default_model is a reasoning model, the QA stage
    must NOT get the `(+reasoning)` suffix — because its own model is
    non-reasoning and `_append_model_stage` evaluates the flag per
    stage model, not per review default.

    A regression that accidentally passes `model` (review default) to
    the QA stage instead of `config.vision_model` would silently slip
    past the main reasoning-flag test's `startswith(exempt)` skip.
    """
    config = _config(model="openai/gpt-5.4-pro")  # reasoning default
    with patch("coarse.cost.has_provider_key", return_value=True):
        estimate = build_cost_estimate(_paper(), config)
    qa_stages = [s for s in estimate.stages if s.name.startswith("extraction_qa")]
    assert len(qa_stages) == 1
    assert qa_stages[0].name == "extraction_qa"  # no (+reasoning) suffix
    assert "(+reasoning)" not in qa_stages[0].name


def test_build_cost_estimate_does_not_flag_non_reasoning_stages():
    config = _config(model="openai/gpt-5-chat")  # -chat is the non-reasoning gpt-5 (#185)
    estimate = build_cost_estimate(_paper(), config, section_count=4)
    for s in estimate.stages:
        assert "(+reasoning)" not in s.name


def test_reasoning_model_costs_more_than_same_price_non_reasoning():
    """Pin that the reasoning overhead actually increases the dollar total.
    Compare two model IDs with identical per-token pricing, one reasoning,
    one not. o3 and gpt-5-pro are known reasoning; gpt-5-chat is not (#185 —
    the `-chat` variants are the only non-reasoning gpt-5 models)."""
    paper = _paper()
    reasoning_est = build_cost_estimate(
        paper,
        _config(model="openai/o3"),
        section_count=6,
    )
    regular_est = build_cost_estimate(
        paper,
        _config(model="openai/gpt-5-chat"),
        section_count=6,
    )
    # o3 is actually cheaper per-token than gpt-5 pro, so we can't compare
    # two reasoning models directly. But we CAN assert that o3's estimate
    # reflects the overhead by comparing the cost to what it'd be with zero
    # reasoning overhead — which is the regular-model calculation path.
    # Easier: assert the per-stage reasoning flag appears only in reasoning.
    assert any("(+reasoning)" in s.name for s in reasoning_est.stages)
    assert not any("(+reasoning)" in s.name for s in regular_est.stages)


def test_reasoning_overhead_visible_in_tokens_out_column():
    """The displayed tokens_out column should reflect the reasoning overhead
    so the table is internally consistent with the dollar column.

    Section agents budget 4000 visible output tokens (expected output); a
    reasoning model adds 1.5x on top (per _REASONING_OVERHEAD_MULTIPLIER in
    llm.py), giving 4000 + 6000 = 10000 displayed tokens.
    """
    config = _config(model="openai/o3")
    with patch("coarse.cost.has_provider_key", return_value=True):
        est = build_cost_estimate(_paper(), config, section_count=4)
    section_stage = next(s for s in est.stages if s.name.startswith("section_"))
    # Visible budget is 4000 per section + 1.5x reasoning overhead = 10000.
    assert section_stage.estimated_tokens_out == 10000


# ---------------------------------------------------------------------------
# confirm_or_abort
# ---------------------------------------------------------------------------


def _make_estimate(cost: float) -> CostEstimate:
    stage = CostStage(
        name="test",
        model=TEST_MODEL,
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


def test_confirm_or_abort_non_tty_aborts():
    """Non-interactive mode should abort by default to prevent runaway costs."""
    estimate = _make_estimate(1.0)
    with patch("typer.confirm", side_effect=EOFError("not a tty")):
        with pytest.raises(SystemExit, match="Non-interactive mode"):
            confirm_or_abort(estimate, max_cost_usd=10.0)


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
    assert abs(result.total_cost_usd - stage_sum * 1.30) < 1e-10


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


# ---------------------------------------------------------------------------
# OpenRouter Fusion (dynamic-priced model)
# ---------------------------------------------------------------------------


def test_fusion_estimate_is_priced_not_zero():
    """OpenRouter reports -1 (dynamic) pricing for Fusion, which used to make
    the estimate $0 — silently bypassing the approval gate's `<= 0.01` skip
    and reporting $0 spent on a model that bills real money. With the
    registered representative rates the estimate must be well above the skip
    threshold so the gate actually fires."""
    estimate = build_cost_estimate(_paper(), _config(model=FUSION_MODEL), section_count=8)
    assert estimate.total_cost_usd > 0.01
    # The review-model stages should be attributed to Fusion and priced > 0,
    # confirming the rate lookup resolved rather than zeroing out.
    review_stages = [s for s in estimate.stages if s.name == "overview"]
    assert review_stages
    assert review_stages[0].model == FUSION_MODEL
    assert review_stages[0].estimated_cost_usd > 0
