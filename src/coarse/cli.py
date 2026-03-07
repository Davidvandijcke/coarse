"""CLI for coarse — AI academic paper reviewer."""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

import typer
from rich.console import Console
from rich.status import Status

from coarse.config import (
    PROVIDER_ENV_VARS,
    CoarseConfig,
    load_config,
    resolve_api_key,
    save_config,
)
from coarse.models import CHEAP_MODELS, QUALITY_MODEL
from coarse.pipeline import review_paper

app = typer.Typer(
    name="coarse",
    help="Free, open-source AI academic paper reviewer.",
    add_completion=False,
)

console = Console()


def _pick_cheap_model() -> str | None:
    """Find the cheapest available model based on which API keys are set."""
    import os
    for env_var, model in CHEAP_MODELS.items():
        if os.environ.get(env_var):
            return model
    return None


def _run_setup(config: CoarseConfig) -> CoarseConfig:
    """Interactive setup: prompt for default model and API keys, return updated config."""
    console.print("\n[bold]coarse setup[/bold] — configure your API keys\n")

    default_model = typer.prompt(
        "Default model (e.g. openai/gpt-4o)",
        default=config.default_model,
    )
    config = config.model_copy(update={"default_model": default_model})

    import os

    for provider, env_var in PROVIDER_ENV_VARS.items():
        if os.environ.get(env_var):
            console.print(f"  [dim]{env_var} already set in environment — skipping[/dim]")
            continue

        key = typer.prompt(
            f"  {env_var} (leave blank to skip)",
            default="",
            hide_input=True,
            show_default=False,
        )
        if key:
            config.api_keys[provider] = key

    save_config(config)
    console.print("\n[green]Configuration saved to ~/.coarse/config.toml[/green]\n")
    return config


@app.command()
def setup() -> None:
    """Interactive setup: configure default model and API keys."""
    config = load_config()
    _run_setup(config)


@app.command()
def review(
    pdf: Path = typer.Argument(..., exists=True, help="Path to PDF file"),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output file path (default: <pdf_stem>_review.md)"
    ),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="LiteLLM model string (e.g. openai/gpt-4o)"
    ),
    cheap: bool = typer.Option(
        False, "--cheap", help="Use cheapest available model"
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip cost confirmation prompt"),
    no_qa: bool = typer.Option(False, "--no-qa", help="Skip post-extraction quality check"),
    agentic: bool = typer.Option(
        False, "--agentic", help="(default now — kept for backwards compat)"
    ),
    no_agentic: bool = typer.Option(
        False, "--no-agentic", help="Disable coding agents (faster, less thorough)"
    ),
    eval_ref: Optional[Path] = typer.Option(
        None, "--eval", help="Path to reference review markdown for quality scoring"
    ),
    eval_panel: bool = typer.Option(
        False, "--eval-panel", help="Use 3-judge panel evaluation (default: single judge)"
    ),
    eval_model: Optional[str] = typer.Option(
        None, "--eval-model", help=f"Model for quality evaluation (default: {QUALITY_MODEL})"
    ),
) -> None:
    """Review a PDF paper and write a markdown report."""

    config = load_config()
    if no_qa:
        config = config.model_copy(update={"extraction_qa": False})
    if no_agentic:
        config = config.model_copy(update={"use_coding_agents": False})
        console.print("[dim]Coding agents disabled[/dim]")
    elif agentic or config.use_coding_agents:
        console.print(
            "[dim]Agentic mode: proof/methodology/results sections use coding agents "
            "(~3-10 min vs ~30s)[/dim]"
        )

    # Resolve model: --cheap > --model > config default
    if cheap:
        resolved_model = _pick_cheap_model()
        if resolved_model is None:
            console.print("[red]--cheap: no API key found for any provider.[/red]")
            raise typer.Exit(code=1)
        console.print(f"[dim]Using cheap model: {resolved_model}[/dim]")
    else:
        resolved_model = model or config.default_model

    # Propagate -m to coding agents so they use the same model
    if model:
        config = config.model_copy(update={"agent_model": resolved_model})

    # Check API key; run setup inline if missing
    if resolve_api_key(resolved_model, config) is None:
        provider = resolved_model.split("/")[0] if "/" in resolved_model else resolved_model
        console.print(f"[yellow]No API key found for provider '{provider}'.[/yellow]")
        if not sys.stdin.isatty():
            console.print(
                "[red]stdin is not a TTY. "
                "Set the appropriate API key environment variable or run 'coarse setup'.[/red]"
            )
            raise typer.Exit(code=1)
        config = _run_setup(config)

    # Determine output path
    out_path = output or Path(f"{pdf.stem}_review.md")

    console.print(f"[bold]Reviewing[/bold] {pdf.name} with {resolved_model}")

    with Status("Running review pipeline...", console=console):
        review_obj, markdown, paper_text = review_paper(
            pdf_path=pdf,
            model=resolved_model,
            skip_cost_gate=yes,
            config=config,
        )

    out_path.write_text(markdown, encoding="utf-8")
    n_comments = len(review_obj.detailed_comments)
    n_issues = len(review_obj.overall_feedback.issues)
    console.print(
        f"[green]Review written to {out_path}[/green] "
        f"({n_issues} issues, {n_comments} detailed comments)"
    )

    if eval_ref is not None:
        from coarse.llm import LLMClient
        from coarse.quality import evaluate_review, evaluate_review_panel, save_quality_report

        reference_text = eval_ref.read_text(encoding="utf-8")
        quality_model = eval_model or QUALITY_MODEL
        quality_client = LLMClient(model=quality_model)
        mode = "panel" if eval_panel else "single"

        with Status(f"Running quality evaluation ({mode})...", console=console):
            if eval_panel:
                report, _ = evaluate_review_panel(
                    markdown, reference_text, client=quality_client,
                    paper_text=paper_text.full_markdown,
                )
            else:
                report = evaluate_review(
                    markdown, reference_text, client=quality_client,
                    paper_text=paper_text.full_markdown,
                )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        quality_path = out_path.parent / f"{pdf.stem}_quality_{timestamp}.md"
        save_quality_report(report, quality_path, str(eval_ref), model=quality_model, mode=mode)
        console.print(
            f"[green]Quality report written to {quality_path}[/green] "
            f"(overall: {report.overall_score:.2f}/5.0)"
        )
