"""CLI for coarse — AI academic paper reviewer."""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

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
from coarse.extraction import SUPPORTED_EXTENSIONS
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
    pdf: Path = typer.Argument(
        ..., exists=True,
        help="Path to paper file (PDF, TXT, MD, TeX, DOCX, HTML, EPUB)",
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output file path (default: <pdf_stem>_review.md)"
    ),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="LiteLLM model string (e.g. openai/gpt-4o)"
    ),
    api_key: Optional[str] = typer.Option(
        None, "--api-key",
        help="OpenRouter API key (WARNING: visible in shell history and process "
             "listing; prefer --env-file or OPENROUTER_API_KEY env var)",
    ),
    env_file: Optional[Path] = typer.Option(
        None, "--env-file", help="Path to a .env file to load (e.g. ~/keys.env)"
    ),
    cheap: bool = typer.Option(
        False, "--cheap", help="Use cheapest available model"
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip cost confirmation prompt"),
    no_qa: bool = typer.Option(False, "--no-qa", help="Skip post-extraction quality check"),
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
    """Review a paper and write a markdown report."""

    # Load env file / API key before anything else so config picks them up
    if env_file is not None:
        from dotenv import load_dotenv
        load_dotenv(env_file, override=True)
    if api_key is not None:
        os.environ["OPENROUTER_API_KEY"] = api_key

    if pdf.suffix.lower() not in SUPPORTED_EXTENSIONS:
        console.print(
            f"[red]Unsupported format: {pdf.suffix}. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}[/red]"
        )
        raise typer.Exit(code=1)

    config = load_config()
    if no_qa:
        config = config.model_copy(update={"extraction_qa": False})
    # Resolve model: --cheap > --model > config default
    if cheap:
        resolved_model = _pick_cheap_model()
        if resolved_model is None:
            console.print("[red]--cheap: no API key found for any provider.[/red]")
            raise typer.Exit(code=1)
        console.print(f"[dim]Using cheap model: {resolved_model}[/dim]")
    else:
        resolved_model = model or config.default_model

    # Check API key; run setup inline if missing
    if resolve_api_key(resolved_model, config) is None:
        provider = resolved_model.split("/")[0] if "/" in resolved_model else resolved_model
        console.print(f"[yellow]No API key found for provider '{provider}'.[/yellow]")
        console.print(
            "\n[dim]Quickest fix:[/dim]\n"
            f"  coarse review {pdf} [bold]--api-key YOUR_OPENROUTER_KEY[/bold]\n\n"
            "[dim]Or load from a .env file:[/dim]\n"
            f"  coarse review {pdf} [bold]--env-file path/to/.env[/bold]\n\n"
            "[dim]Or configure once:[/dim]\n"
            "  coarse setup\n\n"
            "[dim]Get a free OpenRouter key at:[/dim] https://openrouter.ai/keys\n"
        )
        if not sys.stdin.isatty():
            raise typer.Exit(code=1)
        config = _run_setup(config)

    # Warn if vision QA is enabled but no vision model key is available
    if config.extraction_qa and resolve_api_key(config.vision_model, config) is None:
        console.print(
            f"[dim]No API key for vision model ({config.vision_model}) — "
            "extraction QA will be skipped. Set GEMINI_API_KEY to enable it.[/dim]"
        )

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

        # Prefer sending the actual PDF for quote verification (no extraction mismatch)
        pdf_path = pdf if pdf.suffix.lower() == ".pdf" else None

        with Status(f"Running quality evaluation ({mode})...", console=console):
            if eval_panel:
                report, _ = evaluate_review_panel(
                    markdown, reference_text, client=quality_client,
                    paper_text=paper_text.full_markdown,
                    paper_pdf=pdf_path,
                )
            else:
                report = evaluate_review(
                    markdown, reference_text, client=quality_client,
                    paper_text=paper_text.full_markdown,
                    paper_pdf=pdf_path,
                )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_slug = resolved_model.replace("/", "_").replace(":", "_")
        quality_path = out_path.parent / f"{pdf.stem}_quality_{model_slug}_{timestamp}.md"
        save_quality_report(report, quality_path, str(eval_ref), model=quality_model, mode=mode)
        console.print(
            f"[green]Quality report written to {quality_path}[/green] "
            f"(overall: {report.overall_score:.2f}/5.0)"
        )
