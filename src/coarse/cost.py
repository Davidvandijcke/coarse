"""Cost estimation and user approval gate for coarse.

No LLM calls here — purely heuristic token budgets + pricing lookup.

The stage list in `build_cost_estimate()` is a best-effort mirror of
`review_paper()` in `pipeline.py`. It is NOT automatically kept in sync —
when an agent is added, removed, or its `max_tokens` budget changes, the
matching stage here has to be updated by hand. Audit this file against
`pipeline.py` and `src/coarse/agents/*.py` on every pipeline refactor.
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from coarse.config import CoarseConfig, has_provider_key
from coarse.llm import estimate_call_cost, estimate_reasoning_overhead_tokens
from coarse.models import (
    LITERATURE_SEARCH_MODEL,
    OCR_MODEL,
    STAGE_MODELS,
    is_reasoning_model,
)
from coarse.types import CostEstimate, CostStage, PaperText

# ---------------------------------------------------------------------------
# Heuristic pricing constants (verified 2026-04-11, aligned with pipeline.py
# and src/coarse/agents/*.py). Constants are sized to match the real
# `max_tokens` each agent passes — not a guess at average visible output.
# Instructor retries, long outputs, and conditional stages that didn't fire
# are absorbed by `_COST_BUFFER`.
# ---------------------------------------------------------------------------

# Section sizing. `_MAX_REVIEWABLE_SECTIONS` mirrors the `reviewable_sections[:25]`
# slice in `pipeline.py::review_paper()` — both must match.
_TOKENS_PER_SECTION = 1200
_MAX_REVIEWABLE_SECTIONS = 25
_MIN_SECTIONS = 4

# Per-section prompt overhead: system + overview + calibration + notation
# + abstract + (sometimes lit context). Measured on a typical run, not the
# ~5k the previous version assumed.
_SECTION_PROMPT_OVERHEAD = 8000

# PDF extraction (Mistral OCR via OpenRouter file-parser, $2 / 1000 pages)
_TOKENS_PER_PAGE = 250
_OCR_COST_PER_PAGE = 0.002

# Conditional-stage heuristics — the cost gate runs before structure
# analysis so we don't yet know how many math sections exist or whether
# the results/discussion split justifies cross-section synthesis. Math-
# heavy papers will under-estimate relative to these defaults; the 1.30x
# buffer has to carry the slack.
_MATH_SECTION_FRACTION = 0.2  # fraction of sections assumed to have math content
_CROSS_SECTION_MIN_SECTIONS = 6  # below this, assume no cross-section synthesis
_EXPECTED_CROSS_SECTION_CALLS = 1  # expected-value midpoint; up to 3 fire in practice

# Editorial agent (single merged pass that replaced the legacy
# crossref+critique chain — see src/coarse/agents/editorial.py). The
# agent also reads the full paper text for quote/absence verification,
# which dominates the input budget on long papers.
_AVG_COMMENTS_PER_SECTION = 3
_TOKENS_PER_COMMENT = 350
_EDITORIAL_OVERHEAD = 5000  # system + overview + contribution context

# Overview context that proof_verify, completeness, and cross_section all
# receive as part of their user prompt. ~5000 tokens on a typical run
# (overview issues + calibration + abstract + title).
_OVERVIEW_CONTEXT_OVERHEAD = 5000

# Flat-fee stages
_LITERATURE_FLAT_COST = 0.03  # Perplexity Sonar Pro via OpenRouter

# Conservative multiplier applied to the final total. Covers instructor
# retries, occasional long outputs, and the gap between heuristic
# defaults and actual math/cross-section counts. Bumped from 1.15 after
# a systematic under-count audit in April 2026.
_COST_BUFFER = 1.30


def _estimate_section_count(total_tokens: int) -> int:
    """Estimate number of reviewable sections from paper token count."""
    return max(
        _MIN_SECTIONS,
        min(_MAX_REVIEWABLE_SECTIONS, total_tokens // _TOKENS_PER_SECTION),
    )


def _append_model_stage(
    stages: list[CostStage],
    name: str,
    model: str,
    tokens_in: int,
    tokens_out: int,
) -> None:
    """Build a CostStage for a model call and append it to `stages`.

    Applies the reasoning-token overhead per the stage's own model (not
    the review's default), so vision-QA on a non-reasoning vision model
    stays non-reasoning even when the main review model is a reasoning
    one. The `(+reasoning)` suffix is the signal that
    `estimated_tokens_out` is inflated past the visible budget — do not
    re-apply `estimate_reasoning_overhead_tokens` to that field.
    """
    cost = estimate_call_cost(model, tokens_in, tokens_out)
    displayed_out = tokens_out + estimate_reasoning_overhead_tokens(model, tokens_out)
    stage_name = f"{name} (+reasoning)" if is_reasoning_model(model) else name
    stages.append(
        CostStage(
            name=stage_name,
            model=model,
            estimated_tokens_in=tokens_in,
            estimated_tokens_out=displayed_out,
            estimated_cost_usd=cost,
        )
    )


def build_cost_estimate(
    paper_text: PaperText,
    config: CoarseConfig,
    section_count: int | None = None,
    is_pdf: bool = True,
    model: str | None = None,
    stage_overrides: dict[str, str] | None = None,
) -> CostEstimate:
    """Return a CostEstimate with per-stage breakdowns using heuristic token budgets.

    Args:
        paper_text: Extracted paper content; only `token_estimate` is read.
        config: Review config (default model, vision model, extraction_qa flag).
        section_count: Override for estimated reviewable sections. Defaults to
            a heuristic based on paper length, capped at `_MAX_REVIEWABLE_SECTIONS`.
            Values < 1 are clamped to 1 to prevent divide-by-zero.
        is_pdf: Whether the input is a PDF. The pipeline only runs
            extraction QA on PDFs (see pipeline.py:226), so non-PDFs skip
            that stage in the estimate even when ``config.extraction_qa``
            is True.
        model: Explicit model override for the review model. Defaults to
            ``config.default_model``. Callers that received a ``--model``
            CLI flag should pass it here so the quoted cost reflects the
            model the user actually asked for, not the config default.
        stage_overrides: Optional per-stage model overrides merged on top
            of the default ``STAGE_MODELS`` map. Keys must be valid stage
            names. Used so the cost table reflects the same routing the
            pipeline will execute.
    """
    model = model or config.default_model
    # Merge the default STAGE_MODELS routing with any caller-provided
    # overrides. Caller's keys take precedence (same resolution order as
    # pipeline.py's StageRouter).
    effective_overrides: dict[str, str] = {**STAGE_MODELS, **(stage_overrides or {})}

    def _stage_model(name: str) -> str:
        return effective_overrides.get(name, model)

    total_tokens = max(0, paper_text.token_estimate)
    if section_count is None:
        section_count = _estimate_section_count(total_tokens)
    # Clamp defensively: section_count=0 would crash the divisions below.
    # Callers may pass smaller values than the heuristic min (e.g. for
    # very short papers in tests) — clamp to >= 1, not >= _MIN_SECTIONS.
    section_count = max(1, section_count)
    # Both derivations depend on section_count after clamping.
    math_section_count = max(0, round(section_count * _MATH_SECTION_FRACTION))
    cross_section_count = (
        _EXPECTED_CROSS_SECTION_CALLS if section_count >= _CROSS_SECTION_MIN_SECTIONS else 0
    )

    section_text_tokens = max(1, total_tokens // section_count)
    section_input = section_text_tokens + _SECTION_PROMPT_OVERHEAD
    est_pages = max(1, total_tokens // _TOKENS_PER_PAGE)

    # Editorial agent reads all downstream comments plus the full paper for
    # quote/absence verification. Downstream comments include section,
    # completeness, proof_verify, and cross_section outputs — not just
    # the raw section agent count — so this is the sum across all stages
    # that feed editorial.
    n_editorial_comments = (
        section_count * _AVG_COMMENTS_PER_SECTION  # section agents
        + _AVG_COMMENTS_PER_SECTION  # completeness (1 agent run)
        + math_section_count * _AVG_COMMENTS_PER_SECTION  # proof_verify
        + cross_section_count * 2  # cross-section synthesis comments
    )
    editorial_in = n_editorial_comments * _TOKENS_PER_COMMENT + _EDITORIAL_OVERHEAD + total_tokens

    stages: list[CostStage] = []

    # PDF extraction (Mistral OCR via OpenRouter, or format-specific
    # fallback for DOCX/HTML/EPUB/etc.). Flat fee per page.
    stages.append(
        CostStage(
            name="pdf_extraction",
            model=OCR_MODEL,
            estimated_tokens_in=0,
            estimated_tokens_out=0,
            estimated_cost_usd=est_pages * _OCR_COST_PER_PAGE,
        )
    )

    # Extraction QA (vision LLM spot-check). PDF-only in the pipeline,
    # so non-PDF inputs skip it even when config.extraction_qa is set.
    # Uses its own vision model — reasoning overhead is evaluated per
    # that model, not the review default.
    if config.extraction_qa and is_pdf:
        # Input: full markdown + ~10 rendered page images encoded as
        # multimodal tokens. Output: max_tokens=4096 in extraction_qa.py.
        _append_model_stage(
            stages,
            "extraction_qa",
            config.vision_model,
            total_tokens + 5000,
            4096,
        )

    # Structure analysis (metadata + math detection) — both cheap.
    _append_model_stage(stages, "metadata", _stage_model("metadata"), 500, 256)
    _append_model_stage(stages, "math_detection", _stage_model("math_detection"), 2000, 1024)

    # Parallel trio: calibration, literature search, contribution
    # extraction. All use the default model except Perplexity literature
    # search, which is flat-fee.
    _append_model_stage(stages, "calibration", _stage_model("calibration"), 1500, 2048)

    if has_provider_key("openrouter", config):
        stages.append(
            CostStage(
                name="literature_search",
                model=LITERATURE_SEARCH_MODEL,
                estimated_tokens_in=0,
                estimated_tokens_out=0,
                estimated_cost_usd=_LITERATURE_FLAT_COST,
            )
        )
    else:
        # arXiv fallback: query-gen (512 out) + ranking (2048 out) —
        # two LLM calls on the default model. literature_search isn't
        # in STAGE_NAMES today; the arXiv fallback path runs on whatever
        # the main review model is, so we use `model` directly here.
        _append_model_stage(stages, "literature_query_gen", model, 1500, 512)
        _append_model_stage(stages, "literature_ranking", model, 4000, 2048)

    _append_model_stage(
        stages,
        "contribution_extraction",
        _stage_model("contribution_extraction"),
        3000,
        2048,
    )

    # Overview: a single agent call. There is NO 3-judge panel — the
    # `OverviewAgent.run()` at src/coarse/agents/overview.py:80 makes
    # one `client.complete(..., max_tokens=8192)` call and returns.
    _append_model_stage(stages, "overview", _stage_model("overview"), total_tokens + 3000, 8192)

    # Completeness agent. Reads the full paper via `_build_sections_text`
    # plus overview + contribution context — so input is `total_tokens`,
    # not a tiny prompt. See src/coarse/agents/completeness.py:44.
    _append_model_stage(
        stages,
        "completeness",
        _stage_model("completeness"),
        total_tokens + _OVERVIEW_CONTEXT_OVERHEAD,
        4096,
    )

    # Section agents (parallel, one per reviewable section). max_tokens=
    # 16384 but most runs use 8–12k; budget at 10k and let the buffer
    # cover the tail.
    section_model = _stage_model("section")
    for i in range(section_count):
        _append_model_stage(stages, f"section_{i + 1}", section_model, section_input, 10000)

    # Proof verify (chained after section agents for math sections only).
    # max_tokens=16384. Input = section text + section's own comments +
    # overview/calibration context.
    verify_model = _stage_model("verify")
    for i in range(math_section_count):
        _append_model_stage(
            stages,
            f"proof_verify_{i + 1}",
            verify_model,
            section_input + _OVERVIEW_CONTEXT_OVERHEAD,
            16384,
        )

    # Cross-section synthesis (up to 3 calls — main results × top-3
    # discussion sections — only when both section types are present and
    # the results section has math). max_tokens=8192.
    cross_section_model = _stage_model("cross_section")
    for i in range(cross_section_count):
        _append_model_stage(
            stages,
            f"cross_section_{i + 1}",
            cross_section_model,
            section_text_tokens * 2 + _OVERVIEW_CONTEXT_OVERHEAD,
            8192,
        )

    # Editorial pass (single merged dedup+contradiction+quality+ordering
    # agent). Reads all downstream comments plus the full paper markdown
    # for quote verification. max_tokens=32768 but most runs use 20–25k;
    # budget at 24k.
    _append_model_stage(stages, "editorial", _stage_model("editorial"), editorial_in, 24000)

    total = sum(s.estimated_cost_usd for s in stages) * _COST_BUFFER
    return CostEstimate(stages=stages, total_cost_usd=total)


def display_cost_estimate(estimate: CostEstimate) -> None:
    """Print a Rich table showing per-stage cost breakdown."""
    console = Console()
    table = Table(title="Estimated Cost", show_footer=True)
    table.add_column("Stage", footer="Total")
    table.add_column("Model")
    table.add_column("Tokens In", justify="right")
    table.add_column("Tokens Out", justify="right")
    table.add_column("Est. Cost", justify="right", footer=f"${estimate.total_cost_usd:.4f}")

    for stage in estimate.stages:
        table.add_row(
            stage.name,
            stage.model,
            f"{stage.estimated_tokens_in:,}",
            f"{stage.estimated_tokens_out:,}",
            f"${stage.estimated_cost_usd:.4f}",
        )

    console.print(table)


def confirm_or_abort(estimate: CostEstimate, max_cost_usd: float) -> None:
    """Raise SystemExit if cost exceeds cap or user declines. Skip prompt if negligible."""
    if estimate.total_cost_usd > max_cost_usd:
        raise SystemExit(
            f"Estimated cost ${estimate.total_cost_usd:.4f} exceeds max_cost_usd "
            f"${max_cost_usd:.2f}. Aborting."
        )

    if estimate.total_cost_usd <= 0.01:
        return

    try:
        confirmed = typer.confirm(
            f"Proceed with estimated cost ${estimate.total_cost_usd:.4f}?",
            default=True,
        )
    except (EOFError, OSError):
        raise SystemExit(
            f"Non-interactive mode — aborting (estimated cost ${estimate.total_cost_usd:.4f}). "
            "Pass --yes to skip confirmation."
        )

    if not confirmed:
        raise SystemExit("Aborted by user.")


def run_cost_gate(
    paper_text: PaperText,
    config: CoarseConfig,
    section_count: int | None = None,
    is_pdf: bool = True,
    model: str | None = None,
    stage_overrides: dict[str, str] | None = None,
) -> CostEstimate:
    """Build estimate, display it, prompt for confirmation. Returns CostEstimate."""
    estimate = build_cost_estimate(
        paper_text,
        config,
        section_count=section_count,
        is_pdf=is_pdf,
        model=model,
        stage_overrides=stage_overrides,
    )
    display_cost_estimate(estimate)
    confirm_or_abort(estimate, config.max_cost_usd)
    return estimate
