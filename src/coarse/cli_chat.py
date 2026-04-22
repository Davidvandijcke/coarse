"""Interactive chat with the reviewer persona over a paper + prior review."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

console = Console()


def chat(
    paper: Path = typer.Argument(
        ...,
        exists=True,
        help="Path to the paper file (PDF, MD, TXT, TeX, DOCX, HTML, EPUB).",
    ),
    review: Path = typer.Argument(
        ...,
        exists=True,
        help="Path to the existing review markdown produced by `coarse review`.",
    ),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="LiteLLM model string. Defaults to config default_model."
    ),
) -> None:
    """Chat with the reviewer about a paper and its prior review."""
    console.print(f"[bold]chat stub[/bold]: paper={paper.name} review={review.name} model={model}")
