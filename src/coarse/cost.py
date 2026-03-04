"""Cost estimation and user approval gate for coarse.

No LLM calls here — purely heuristic token budgets + pricing lookup.
"""
from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from coarse.config import CoarseConfig
from coarse.llm import estimate_call_cost
from coarse.types import CostEstimate, CostStage, PaperText

_DEFAULT_SECTION_COUNT = 8


def build_cost_estimate(
    paper_text: PaperText,
    config: CoarseConfig,
    section_count: int = _DEFAULT_SECTION_COUNT,
) -> CostEstimate:
    """Return a CostEstimate with per-stage breakdowns using heuristic token budgets."""
    model = config.default_model
    total_tokens = paper_text.token_estimate
    section_tokens = max(1, total_tokens // section_count)

    stage_defs: list[tuple[str, int, int]] = [
        ("metadata", 500, 100),
        ("overview", total_tokens, 1200),
        *[(f"section_{i + 1}", section_tokens, 600) for i in range(section_count)],
        ("crossref", total_tokens, 1000),
        ("critique", total_tokens, 800),
    ]

    stages: list[CostStage] = []
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
    section_count: int = _DEFAULT_SECTION_COUNT,
) -> CostEstimate:
    """Build estimate, display it, prompt for confirmation. Returns CostEstimate."""
    estimate = build_cost_estimate(paper_text, config, section_count=section_count)
    display_cost_estimate(estimate)
    confirm_or_abort(estimate, config.max_cost_usd)
    return estimate
