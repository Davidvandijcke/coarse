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
    has_provider_key,
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


def _pick_cheap_model(config: CoarseConfig) -> str | None:
    """Find the cheapest available model based on which API keys are set.

    Respects both env-var and config-file keys (via has_provider_key) so
    users who configured keys in ~/.coarse/config.toml aren't forced to
    export them as env vars for --cheap to work.
    """
    env_to_provider = {v: k for k, v in PROVIDER_ENV_VARS.items()}
    for env_var, model in CHEAP_MODELS.items():
        provider = env_to_provider.get(env_var)
        if provider and has_provider_key(provider, config):
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
        ...,
        exists=True,
        help="Path to paper file (PDF, TXT, MD, TeX, DOCX, HTML, EPUB)",
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output file path (default: <pdf_stem>_review.md)"
    ),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="LiteLLM model string (e.g. openai/gpt-4o)"
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        help="OpenRouter API key (WARNING: visible in shell history and process "
        "listing; prefer --env-file or OPENROUTER_API_KEY env var)",
    ),
    env_file: Optional[Path] = typer.Option(
        None, "--env-file", help="Path to a .env file to load (e.g. ~/keys.env)"
    ),
    cheap: bool = typer.Option(False, "--cheap", help="Use cheapest available model"),
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
    stage_override: Optional[list[str]] = typer.Option(
        None,
        "--stage-override",
        help=(
            "Override the model used for a specific pipeline stage. Repeatable. "
            "Format: --stage-override <stage>=<model>. Valid stage names: "
            "metadata, math_detection, contribution_extraction, calibration, "
            "overview, completeness, section, cross_section, verify, editorial. "
            "Defaults from src/coarse/models.py::STAGE_MODELS are applied first; "
            "this flag takes precedence."
        ),
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
        resolved_model = _pick_cheap_model(config)
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

    # Parse --stage-override entries into a dict. Each entry is
    # "<stage>=<model>". Malformed entries exit early with a clear error
    # message. StageRouter will validate the stage names at construction.
    stage_overrides: dict[str, str] = {}
    for entry in stage_override or []:
        if "=" not in entry:
            console.print(f"[red]--stage-override: expected '<stage>=<model>', got '{entry}'[/red]")
            raise typer.Exit(code=1)
        stage, override_model = entry.split("=", 1)
        stage_overrides[stage.strip()] = override_model.strip()

    console.print(f"[bold]Reviewing[/bold] {pdf.name} with {resolved_model}")

    with Status("Running review pipeline...", console=console):
        review_obj, markdown, paper_text = review_paper(
            pdf_path=pdf,
            model=resolved_model,
            skip_cost_gate=yes,
            config=config,
            stage_overrides=stage_overrides or None,
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
                    markdown,
                    reference_text,
                    client=quality_client,
                    paper_text=paper_text.full_markdown,
                    paper_pdf=pdf_path,
                )
            else:
                report = evaluate_review(
                    markdown,
                    reference_text,
                    client=quality_client,
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


@app.command("mcp-ingest")
def mcp_ingest(
    path: Path = typer.Argument(
        ...,
        exists=True,
        dir_okay=False,
        help="Path to a paper file (PDF, TXT, MD, TeX, DOCX, HTML, EPUB)",
    ),
    server: str = typer.Option(
        "http://127.0.0.1:8765/mcp",
        "--server",
        "-s",
        help="URL of a running coarse MCP server (see deploy/mcp_server.py)",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        help="OpenRouter key for extraction (falls back to OPENROUTER_API_KEY)",
    ),
) -> None:
    """Ingest a local paper file into a running coarse MCP server.

    Reads the file, base64-encodes it, and calls the ``upload_paper_bytes``
    tool on the supplied server URL. Prints the paper_id and section map
    the server returns. Use this when you've already started the MCP
    server (``uv run python deploy/mcp_server.py``) and want to hand a
    local file to it without round-tripping through a public URL.

    The OpenRouter key is only used for extraction (Mistral OCR + structure
    parsing, ~$0.05-0.15). It's passed as a tool argument and is never
    persisted on the server side.
    """
    import asyncio
    import base64

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        console.print(
            f"[red]Unsupported format: {path.suffix}. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}[/red]"
        )
        raise typer.Exit(code=1)

    key = (api_key or os.environ.get("OPENROUTER_API_KEY") or "").strip()
    if not key:
        console.print(
            "[red]No OpenRouter key.[/red] Pass --api-key or set "
            "OPENROUTER_API_KEY in your environment."
        )
        raise typer.Exit(code=1)

    try:
        from fastmcp import Client
    except ImportError:
        console.print(
            "[red]fastmcp not installed.[/red] Install the MCP extra: "
            "[bold]uv sync --extra mcp[/bold] or "
            "[bold]pip install coarse-ink\\[mcp][/bold]"
        )
        raise typer.Exit(code=1) from None

    data_bytes = path.read_bytes()
    data_b64 = base64.b64encode(data_bytes).decode()

    async def _run() -> dict:
        async with Client(server) as client:
            result = await client.call_tool(
                "upload_paper_bytes",
                {
                    "filename": path.name,
                    "data_b64": data_b64,
                    "openrouter_key": key,
                },
            )
            data = getattr(result, "data", None)
            if data is not None:
                return data  # type: ignore[return-value]
            # Tool-level error path: fastmcp surfaces it as a text content block
            content = getattr(result, "content", None) or []
            if content and hasattr(content[0], "text"):
                raise RuntimeError(content[0].text)
            raise RuntimeError(f"unexpected MCP result: {result!r}")

    size_mb = len(data_bytes) / 1024 / 1024
    console.print(f"[bold]Ingesting[/bold] {path.name} ({size_mb:.1f} MB) via {server}")
    try:
        with Status("Uploading + extracting...", console=console):
            result = asyncio.run(_run())
    except Exception as exc:
        console.print(f"[red]MCP ingest failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]Ingested[/green] paper_id=[bold]{result['paper_id']}[/bold]")
    console.print(f"  title: {result.get('title') or '(untitled)'}")
    console.print(
        f"  {result.get('section_count', 0)} sections, domain={result.get('domain') or 'unknown'}"
    )
    for sec in result.get("sections") or []:
        math = " [math]" if sec.get("math_content") else ""
        console.print(
            f"  - {sec['id']}. {sec['title']} ({sec['type']}, {sec['chars']} chars){math}"
        )
    console.print(
        "\n[dim]Next: use this paper_id with get_review_prompt / "
        "verify_quotes / finalize_review, or run:[/dim]\n"
        f"  uv run python deploy/mcp_test_client.py --path {path} "
        f"--server {server}"
    )


# ---------------------------------------------------------------------------
# install-skills — copy bundled skill files into ~/.<host>/skills/ for each
# detected headless CLI (claude, codex, gemini). Source files ship inside
# the wheel under src/coarse/_skills/.
# ---------------------------------------------------------------------------

_SKILL_HOSTS: dict[str, tuple[str, str]] = {
    # (package-dir, install-dir-relative-to-$HOME)
    "claude": ("claude_code", ".claude/skills/coarse-review"),
    "codex": ("codex", ".codex/skills/coarse-review"),
    "gemini": ("gemini_cli", ".gemini/skills/coarse-review"),
}


def _bin_available(name: str) -> bool:
    import shutil

    return shutil.which(name) is not None


@app.command("install-skills")
def install_skills(
    all_hosts: bool = typer.Option(
        False,
        "--all",
        help="Install for all three hosts even if the CLI isn't on PATH.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite existing skill files without prompting.",
    ),
) -> None:
    """Install the coarse-review skill for each detected headless CLI.

    Copies the bundled SKILL.md + scripts into ``~/.claude/skills/``,
    ``~/.codex/skills/``, and/or ``~/.gemini/skills/`` depending on
    which of ``claude``, ``codex``, and ``gemini`` are on PATH.
    """
    from importlib.resources import files as resource_files

    try:
        skills_root = resource_files("coarse") / "_skills"
    except (ModuleNotFoundError, FileNotFoundError) as exc:
        console.print(
            f"[red]Could not locate bundled skills ({exc})[/red]. Is coarse-ink installed?"
        )
        raise typer.Exit(1) from exc

    installed: list[str] = []
    skipped: list[str] = []
    for host, (pkg_dir, install_rel) in _SKILL_HOSTS.items():
        bin_name = host  # "claude", "codex", "gemini"
        if not all_hosts and not _bin_available(bin_name):
            skipped.append(f"{host} (CLI not on PATH)")
            continue

        src = skills_root / pkg_dir
        dest = Path.home() / install_rel

        if dest.exists() and not force:
            # Compare existing SKILL.md — if it's identical, silently refresh.
            try:
                existing = (dest / "SKILL.md").read_text()
                bundled = (src / "SKILL.md").read_text()
                if existing == bundled:
                    console.print(f"  [dim]✓ {host}: already up to date at {dest}[/dim]")
                    installed.append(host)
                    continue
            except Exception:
                pass
            if not typer.confirm(f"  Overwrite existing skill at {dest}?", default=True):
                skipped.append(f"{host} (user declined overwrite)")
                continue

        dest.mkdir(parents=True, exist_ok=True)
        (dest / "scripts").mkdir(exist_ok=True)

        # Copy SKILL.md
        (dest / "SKILL.md").write_text((src / "SKILL.md").read_text())

        # Copy scripts/* if any are bundled (for now we rely on the
        # coarse-review CLI entry point, so no scripts are shipped per-skill).
        scripts_src = src / "scripts"
        if scripts_src.is_dir():
            for child in scripts_src.iterdir():
                if child.is_file():
                    (dest / "scripts" / child.name).write_text(child.read_text())

        installed.append(host)
        console.print(f"  [green]✓ {host}[/green] → {dest}")

    console.print()
    if installed:
        console.print(
            "[bold green]Installed coarse-review skill for:[/bold green] " + ", ".join(installed)
        )
    if skipped:
        console.print(f"[dim]Skipped: {', '.join(skipped)}[/dim]")
    if not installed:
        console.print(
            "[yellow]No hosts installed.[/yellow] Pass [bold]--all[/bold] to "
            "install for all three hosts regardless of which CLIs are on PATH."
        )
        raise typer.Exit(2)

    console.print(
        "\n[dim]Usage:[/dim]\n"
        "  coarse-review <paper.pdf> [--host claude|codex|gemini] "
        "[--model <id>] [--effort low|medium|high|max]\n"
    )
