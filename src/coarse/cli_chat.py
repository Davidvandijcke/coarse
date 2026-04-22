"""Interactive chat with the reviewer persona over a paper + prior review."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from coarse.chat import ChatSession

console = Console()

_QUIT_COMMANDS = {"/quit", "/exit", "/q"}


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
    session = ChatSession(paper_path=paper, review_path=review, model=model)
    console.print(
        f"[bold]coarse chat[/bold]  paper={paper.name}  review={review.name}\n"
        f"[dim]Type {' or '.join(sorted(_QUIT_COMMANDS))} to exit.[/dim]\n"
    )

    while True:
        try:
            question = typer.prompt("you", prompt_suffix=" > ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print()
            return

        if not question:
            continue
        if question.lower() in _QUIT_COMMANDS:
            return

        reply = session.ask(question)
        console.print(f"\n[bold]reviewer[/bold]:\n{reply}\n")
