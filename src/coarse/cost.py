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


def _estimate_section_count(total_tokens: int) -> int:
    """Estimate number of reviewable sections from paper token count.

    Academic papers average ~1,200 tokens per section after OCR extraction.
    """
    return max(4, min(40, total_tokens // 1200))


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
    # Each section prompt includes ~5,000 tokens of overhead:
    # system prompt (~1200) + overview context (~2500) + calibration (~500) + notation (~800)
    section_input = section_text_tokens + 5000

    # OCR extraction cost (Mistral OCR: ~$0.002/page)
    est_pages = max(1, total_tokens // 250)
    stages: list[CostStage] = [
        CostStage(
            name="pdf_extraction",
            model=OCR_MODEL,
            estimated_tokens_in=0,
            estimated_tokens_out=0,
            estimated_cost_usd=est_pages * 0.002,
        ),
    ]

    # Estimated raw comments from section agents (each produces 1-5, avg ~3)
    n_raw_comments = section_count * 3

    # Crossref reads all raw comments, emits deduplicated set as JSON
    crossref_in = n_raw_comments * 350 + 3500  # comments + overview + system
    crossref_out = int(n_raw_comments * 0.6) * 600  # ~60% survive dedup, JSON format

    # Critique reads deduped comments, emits revised set as JSON
    n_deduped = int(n_raw_comments * 0.6)
    critique_in = n_deduped * 350 + 3500
    critique_out = int(n_deduped * 0.9) * 600  # ~90% survive critique

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
                estimated_cost_usd=0.03,
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
    total *= 1.15  # Conservative buffer — better to overestimate
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
    except Exception:
        # Non-TTY or other error — treat as approved
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
