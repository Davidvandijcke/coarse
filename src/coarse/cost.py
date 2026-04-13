"""Cost estimation and user approval gate for coarse.

No LLM calls here — purely heuristic token budgets + pricing lookup.
Stage heuristics are sourced from `coarse.pipeline_spec`, which is also used
to generate the web estimator's shared constants.
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from coarse.config import CoarseConfig, has_provider_key
from coarse.llm import estimate_call_cost, estimate_reasoning_overhead_tokens
from coarse.models import LITERATURE_SEARCH_MODEL, OCR_MODEL, is_reasoning_model
from coarse.pipeline_spec import (
    AVG_COMMENTS_PER_SECTION,
    COST_BUFFER,
    EDITORIAL_OVERHEAD,
    EXTRACTION_QA_IMAGE_OVERHEAD,
    FIXED_STAGE_INPUT_TOKENS,
    LITERATURE_FLAT_COST,
    OCR_COST_PER_PAGE,
    OVERVIEW_CONTEXT_OVERHEAD,
    OVERVIEW_INPUT_OVERHEAD,
    SECTION_PROMPT_OVERHEAD,
    STAGE_OUTPUT_TOKENS,
    TOKENS_PER_COMMENT,
    TOKENS_PER_PAGE,
    clamp_section_count,
    estimate_cross_section_count,
    estimate_math_section_count,
    estimate_section_count,
)
from coarse.types import CostEstimate, CostStage, PaperText


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
) -> CostEstimate:
    """Return a CostEstimate with per-stage breakdowns using heuristic token budgets.

    Args:
        paper_text: Extracted paper content; only `token_estimate` is read.
        config: Review config (default model, vision model, extraction_qa flag).
        section_count: Override for estimated reviewable sections. Defaults to
            a heuristic based on paper length, capped at the runtime section limit.
            Values < 1 are clamped to 1 to prevent divide-by-zero.
        is_pdf: Whether the input is a PDF. The pipeline only runs
            extraction QA on PDFs (see pipeline.py:226), so non-PDFs skip
            that stage in the estimate even when ``config.extraction_qa``
            is True.
        model: Explicit model override for the review model. Defaults to
            ``config.default_model``. Callers that received a ``--model``
            CLI flag should pass it here so the quoted cost reflects the
            model the user actually asked for, not the config default.
    """
    model = model or config.default_model
    total_tokens = max(0, paper_text.token_estimate)
    if section_count is None:
        section_count = estimate_section_count(total_tokens)
    # Clamp defensively: section_count=0 would crash the divisions below.
    section_count = clamp_section_count(section_count)
    # Both derivations depend on section_count after clamping.
    math_section_count = estimate_math_section_count(section_count)
    cross_section_count = estimate_cross_section_count(section_count)

    section_text_tokens = max(1, total_tokens // section_count)
    section_input = section_text_tokens + SECTION_PROMPT_OVERHEAD
    est_pages = max(1, total_tokens // TOKENS_PER_PAGE)

    # Editorial agent reads all downstream comments plus the full paper for
    # quote/absence verification. Downstream comments include section,
    # completeness, proof_verify, and cross_section outputs — not just
    # the raw section agent count — so this is the sum across all stages
    # that feed editorial.
    n_editorial_comments = (
        section_count * AVG_COMMENTS_PER_SECTION  # section agents
        + AVG_COMMENTS_PER_SECTION  # completeness (1 agent run)
        + math_section_count * AVG_COMMENTS_PER_SECTION  # proof_verify
        + cross_section_count * 2  # cross-section synthesis comments
    )
    editorial_in = n_editorial_comments * TOKENS_PER_COMMENT + EDITORIAL_OVERHEAD + total_tokens

    stages: list[CostStage] = []

    # PDF extraction (Mistral OCR via OpenRouter, or format-specific
    # fallback for DOCX/HTML/EPUB/etc.). Flat fee per page.
    stages.append(
        CostStage(
            name="pdf_extraction",
            model=OCR_MODEL,
            estimated_tokens_in=0,
            estimated_tokens_out=0,
            estimated_cost_usd=est_pages * OCR_COST_PER_PAGE,
        )
    )

    # Extraction QA (vision LLM spot-check). PDF-only in the pipeline,
    # so non-PDF inputs skip it even when config.extraction_qa is set.
    # Uses its own vision model — reasoning overhead is evaluated per
    # that model, not the review default.
    if config.extraction_qa and is_pdf:
        # Input: full markdown + ~10 rendered page images encoded as
        # multimodal tokens. Output budget comes from pipeline_spec.
        _append_model_stage(
            stages,
            "extraction_qa",
            config.vision_model,
            total_tokens + EXTRACTION_QA_IMAGE_OVERHEAD,
            STAGE_OUTPUT_TOKENS["extraction_qa"],
        )

    # Structure analysis (metadata + math detection) — both cheap.
    _append_model_stage(
        stages,
        "metadata",
        model,
        FIXED_STAGE_INPUT_TOKENS["metadata"],
        STAGE_OUTPUT_TOKENS["metadata"],
    )
    _append_model_stage(
        stages,
        "math_detection",
        model,
        FIXED_STAGE_INPUT_TOKENS["math_detection"],
        STAGE_OUTPUT_TOKENS["math_detection"],
    )

    # Parallel trio: calibration, literature search, contribution
    # extraction. All use the default model except Perplexity literature
    # search, which is flat-fee.
    _append_model_stage(
        stages,
        "calibration",
        model,
        FIXED_STAGE_INPUT_TOKENS["calibration"],
        STAGE_OUTPUT_TOKENS["calibration"],
    )

    if has_provider_key("openrouter", config):
        stages.append(
            CostStage(
                name="literature_search",
                model=LITERATURE_SEARCH_MODEL,
                estimated_tokens_in=0,
                estimated_tokens_out=0,
                estimated_cost_usd=LITERATURE_FLAT_COST,
            )
        )
    else:
        # arXiv fallback: query-gen (512 out) + ranking (2048 out) —
        # two LLM calls on the default model.
        _append_model_stage(
            stages,
            "literature_query_gen",
            model,
            FIXED_STAGE_INPUT_TOKENS["literature_query_gen"],
            STAGE_OUTPUT_TOKENS["literature_query_gen"],
        )
        _append_model_stage(
            stages,
            "literature_ranking",
            model,
            FIXED_STAGE_INPUT_TOKENS["literature_ranking"],
            STAGE_OUTPUT_TOKENS["literature_ranking"],
        )

    _append_model_stage(
        stages,
        "contribution_extraction",
        model,
        FIXED_STAGE_INPUT_TOKENS["contribution_extraction"],
        STAGE_OUTPUT_TOKENS["contribution_extraction"],
    )

    # Overview: a single agent call. There is NO 3-judge panel — the
    # `OverviewAgent.run()` at src/coarse/agents/overview.py:80 makes
    # one `client.complete(..., max_tokens=8192)` call and returns.
    _append_model_stage(
        stages,
        "overview",
        model,
        total_tokens + OVERVIEW_INPUT_OVERHEAD,
        STAGE_OUTPUT_TOKENS["overview"],
    )

    # Completeness agent. Reads the full paper via `_build_sections_text`
    # plus overview + contribution context — so input is `total_tokens`,
    # not a tiny prompt. See src/coarse/agents/completeness.py:44.
    _append_model_stage(
        stages,
        "completeness",
        model,
        total_tokens + OVERVIEW_CONTEXT_OVERHEAD,
        STAGE_OUTPUT_TOKENS["completeness"],
    )

    # Section agents (parallel, one per reviewable section). max_tokens=
    # 16384 but most runs use 8–12k; budget at 10k and let the buffer
    # cover the tail.
    for i in range(section_count):
        _append_model_stage(
            stages,
            f"section_{i + 1}",
            model,
            section_input,
            STAGE_OUTPUT_TOKENS["section"],
        )

    # Proof verify (chained after section agents for math sections only).
    # max_tokens=16384. Input = section text + section's own comments +
    # overview/calibration context.
    for i in range(math_section_count):
        _append_model_stage(
            stages,
            f"proof_verify_{i + 1}",
            model,
            section_input + OVERVIEW_CONTEXT_OVERHEAD,
            STAGE_OUTPUT_TOKENS["proof_verify"],
        )

    # Cross-section synthesis (up to 3 calls — main results × top-3
    # discussion sections — only when both section types are present and
    # the results section has math). max_tokens=8192.
    for i in range(cross_section_count):
        _append_model_stage(
            stages,
            f"cross_section_{i + 1}",
            model,
            section_text_tokens * 2 + OVERVIEW_CONTEXT_OVERHEAD,
            STAGE_OUTPUT_TOKENS["cross_section"],
        )

    # Editorial pass (single merged dedup+contradiction+quality+ordering
    # agent). Reads all downstream comments plus the full paper markdown
    # for quote verification. max_tokens=32768 but most runs use 20–25k;
    # budget at 24k.
    _append_model_stage(stages, "editorial", model, editorial_in, STAGE_OUTPUT_TOKENS["editorial"])

    total = sum(s.estimated_cost_usd for s in stages) * COST_BUFFER
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
) -> CostEstimate:
    """Build estimate, display it, prompt for confirmation. Returns CostEstimate."""
    estimate = build_cost_estimate(
        paper_text,
        config,
        section_count=section_count,
        is_pdf=is_pdf,
        model=model,
    )
    display_cost_estimate(estimate)
    confirm_or_abort(estimate, config.max_cost_usd)
    return estimate
