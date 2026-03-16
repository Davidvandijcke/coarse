"""Cost estimation and user approval gate for coarse.

No LLM calls here — purely heuristic token budgets + pricing lookup.
"""
from __future__ import annotations

import os

import typer
from rich.console import Console
from rich.table import Table

from coarse.config import CoarseConfig
from coarse.llm import estimate_call_cost
from coarse.models import LITERATURE_SEARCH_MODEL, OCR_MODEL
from coarse.types import CostEstimate, CostStage, PaperText


# Heuristic pricing constants (verified 2026-03-04, aligned with models.py)
_TOKENS_PER_SECTION = 1200       # avg tokens per section after OCR extraction
_SECTION_PROMPT_OVERHEAD = 5000  # system prompt + overview + calibration + notation
_TOKENS_PER_PAGE = 250           # OCR token estimate per page
_OCR_COST_PER_PAGE = 0.002       # Mistral OCR cost per page
_AVG_COMMENTS_PER_SECTION = 3    # raw comments per section agent
_TOKENS_PER_COMMENT = 350        # input tokens per comment in crossref/critique
_CROSSREF_OVERHEAD = 3500        # system prompt + overview context for crossref/critique
_DEDUP_SURVIVAL_RATE = 0.6       # fraction surviving dedup
_CRITIQUE_SURVIVAL_RATE = 0.9    # fraction surviving critique
_COMMENT_OUTPUT_TOKENS = 600     # output tokens per surviving comment
_LITERATURE_FLAT_COST = 0.03     # Perplexity flat fee for literature search
_COST_BUFFER = 1.15              # conservative overestimate multiplier


def _estimate_section_count(total_tokens: int) -> int:
    """Estimate number of reviewable sections from paper token count."""
    return max(4, min(40, total_tokens // _TOKENS_PER_SECTION))


def build_cost_estimate(
    paper_text: PaperText,
    config: CoarseConfig,
    section_count: int | None = None,
) -> CostEstimate:
    """Return a CostEstimate with per-stage breakdowns using heuristic token budgets."""
    model = config.default_model
    total_tokens = paper_text.token_estimate
    if section_count is None:
        section_count = _estimate_section_count(total_tokens)
    section_text_tokens = max(1, total_tokens // section_count)
    section_input = section_text_tokens + _SECTION_PROMPT_OVERHEAD

    est_pages = max(1, total_tokens // _TOKENS_PER_PAGE)
    stages: list[CostStage] = [
        CostStage(
            name="pdf_extraction",
            model=OCR_MODEL,
            estimated_tokens_in=0,
            estimated_tokens_out=0,
            estimated_cost_usd=est_pages * _OCR_COST_PER_PAGE,
        ),
    ]

    n_raw_comments = section_count * _AVG_COMMENTS_PER_SECTION

    crossref_in = n_raw_comments * _TOKENS_PER_COMMENT + _CROSSREF_OVERHEAD
    crossref_out = int(n_raw_comments * _DEDUP_SURVIVAL_RATE) * _COMMENT_OUTPUT_TOKENS

    n_deduped = int(n_raw_comments * _DEDUP_SURVIVAL_RATE)
    critique_in = n_deduped * _TOKENS_PER_COMMENT + _CROSSREF_OVERHEAD
    critique_out = int(n_deduped * _CRITIQUE_SURVIVAL_RATE) * _COMMENT_OUTPUT_TOKENS

    # Overview: 3 judges each read full paper, then a synthesis call
    _NUM_OVERVIEW_JUDGES = 3
    # Literature search: Perplexity flat fee if OpenRouter key available, else token-based
    if os.environ.get("OPENROUTER_API_KEY"):
        stages.append(
            CostStage(
                name="literature_search",
                model=LITERATURE_SEARCH_MODEL,
                estimated_tokens_in=0,
                estimated_tokens_out=0,
                estimated_cost_usd=_LITERATURE_FLAT_COST,
            )
        )
        lit_stage: list[tuple[str, int, int]] = []
    else:
        lit_stage = [("literature_search", 2000, 2560)]

    stage_defs: list[tuple[str, int, int]] = [
        ("metadata", 500, 100),
        ("math_detection", 2000, 256),
        ("calibration", 1000, 2000),
        *lit_stage,
        *[
            (f"overview_judge_{i + 1}", total_tokens, 1500)
            for i in range(_NUM_OVERVIEW_JUDGES)
        ],
        ("overview_synthesis", 5000, 1500),
        *[(f"section_{i + 1}", section_input, 3500) for i in range(section_count)],
        ("crossref", crossref_in, crossref_out),
        ("critique", critique_in, critique_out),
    ]

    for name, tokens_in, tokens_out in stage_defs:
        cost = estimate_call_cost(model, tokens_in, tokens_out)
        stages.append(
            CostStage(
                name=name,
                model=model,
                estimated_tokens_in=tokens_in,
                estimated_tokens_out=tokens_out,
                estimated_cost_usd=cost,
            )
        )

    if config.extraction_qa:
        qa_tokens_in = total_tokens + 5000  # markdown chunks + ~10 page images
        qa_cost = estimate_call_cost(config.vision_model, qa_tokens_in, 1000)
        stages.append(
            CostStage(
                name="extraction_qa",
                model=config.vision_model,
                estimated_tokens_in=qa_tokens_in,
                estimated_tokens_out=1000,
                estimated_cost_usd=qa_cost,
            )
        )

    total = sum(s.estimated_cost_usd for s in stages)
    total *= _COST_BUFFER
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
        import logging
        logging.getLogger(__name__).warning(
            "Non-interactive mode — auto-approving cost estimate ($%.4f)",
            estimate.total_cost_usd,
        )
        return

    if not confirmed:
        raise SystemExit("Aborted by user.")


def run_cost_gate(
    paper_text: PaperText,
    config: CoarseConfig,
    section_count: int | None = None,
) -> CostEstimate:
    """Build estimate, display it, prompt for confirmation. Returns CostEstimate."""
    estimate = build_cost_estimate(paper_text, config, section_count=section_count)
    display_cost_estimate(estimate)
    confirm_or_abort(estimate, config.max_cost_usd)
    return estimate
