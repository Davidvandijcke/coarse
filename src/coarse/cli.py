"""CLI for coarse — AI academic paper reviewer."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner

from coarse.config import (
    PROVIDER_ENV_VARS,
    CoarseConfig,
    load_config,
    resolve_api_key,
    save_config,
)

app = typer.Typer(
    name="coarse",
    help="Free, open-source AI academic paper reviewer.",
    add_completion=False,
)

console = Console()


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
    vision: bool = typer.Option(False, "--vision", help="Use vision mode for scanned PDFs"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip cost confirmation prompt"),
) -> None:
    """Review a PDF paper and write a markdown report."""
    from coarse.pipeline import review_paper

    config = load_config()
    resolved_model = model or config.default_model

    # Check API key; run setup inline if missing
    if resolve_api_key(resolved_model, config) is None:
        console.print(
            f"[yellow]No API key found for provider '{resolved_model.split('/')[0]}'.[/yellow]"
        )
        if not sys.stdin.isatty():
            console.print(
                "[red]stdin is not a TTY. "
                "Set the appropriate API key environment variable or run 'coarse setup'.[/red]"
            )
            raise typer.Exit(code=1)
        config = _run_setup(config)

    # Determine output path
    out_path = output or Path(f"{pdf.stem}_review.md")

    # Run pipeline with spinner
    with Live(Spinner("dots", text="Reviewing paper…"), console=console, refresh_per_second=10):
        review_obj, markdown = review_paper(
            pdf_path=pdf,
            model=model,
            vision=vision,
            skip_cost_gate=yes,
            config=config,
        )

    out_path.write_text(markdown, encoding="utf-8")
    console.print(f"[green]Review written to {out_path}[/green]")
