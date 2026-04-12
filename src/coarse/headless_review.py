"""Entry point for running the full coarse review pipeline with a headless CLI.

Usage:
    python -m coarse.headless_review --host <claude|codex|gemini> \\
        <paper_path> [<pre_extracted_md>] [<output_dir>]

- ``--host``: which CLI to route every LLM call through.
- ``<paper_path>``: PDF, MD, TeX, DOCX, HTML, or EPUB.
- ``<pre_extracted_md>``: optional pre-extracted markdown — skips OCR,
  saves ~$0.05-0.15 and ~30 seconds.
- ``<output_dir>``: where to write ``<stem>_review.md``. Default:
  ``./coarse-output/``.

Environment:
    OPENROUTER_API_KEY   Required unless <pre_extracted_md> is given.
                         Read from env, ~/.coarse/config.toml, or a .env
                         file in the CWD (walked up 3 parents).

    COARSE_HEADLESS_MODEL
    COARSE_HEADLESS_EFFORT
    COARSE_HEADLESS_HOST   Override the --host flag.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path


def _find_openrouter_key() -> str | None:
    """Try env var, ~/.coarse/config.toml, and ./.env (up to 3 parents up)."""
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        return key

    try:
        import tomllib
    except ImportError:
        tomllib = None  # type: ignore[assignment]

    config_path = Path.home() / ".coarse" / "config.toml"
    if config_path.exists() and tomllib is not None:
        try:
            with open(config_path, "rb") as f:
                data = tomllib.load(f)
            stored = data.get("openrouter_api_key") or data.get("openrouter", {}).get("api_key")
            if stored:
                return stored.strip()
        except Exception:
            pass

    for base in [Path.cwd(), *Path.cwd().parents[:3]]:
        env_path = base / ".env"
        if not env_path.exists():
            continue
        try:
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == "OPENROUTER_API_KEY":
                    return v.strip().strip("\"'")
        except Exception:
            continue

    return None


def _require_openrouter_key() -> str:
    key = _find_openrouter_key()
    if key:
        os.environ["OPENROUTER_API_KEY"] = key
        return key

    print(
        "ERROR: OPENROUTER_API_KEY not found.\n\n"
        "Mistral OCR extraction requires an OpenRouter API key. Any of these work:\n"
        "  1. export OPENROUTER_API_KEY=sk-or-v1-...\n"
        "  2. Add OPENROUTER_API_KEY=sk-or-v1-... to a .env file in the\n"
        "     current directory (or any parent directory, up to 3 levels).\n"
        "  3. Run `coarse setup` to save it to ~/.coarse/config.toml\n\n"
        "Alternatively, if you have a pre-extracted markdown file, pass it\n"
        "as the second argument to skip OCR:\n"
        "  python -m coarse.headless_review --host claude <paper.pdf> <paper.md>\n\n"
        "Get a free OpenRouter key at https://openrouter.ai/settings/keys — "
        "review extraction costs ~$0.05-0.15 per paper.",
        file=sys.stderr,
    )
    sys.exit(3)


_DEFAULT_MODELS = {
    "claude": "claude-opus-4-6",
    "codex": "gpt-5.4",
    "gemini": "gemini-3-pro",
}


def _make_client_factory(host: str, model: str | None, effort: str):
    from coarse import headless_clients as hc

    host = host.lower()
    resolved_model = model or _DEFAULT_MODELS[host]

    if host == "claude":

        def _factory(stage: str = ""):
            return hc.ClaudeCodeClient(
                claude_model=resolved_model,
                effort=effort,
            )

        return _factory
    if host == "codex":

        def _factory(stage: str = ""):
            return hc.CodexClient(
                codex_model=resolved_model,
                effort=effort,
            )

        return _factory
    if host == "gemini":

        def _factory(stage: str = ""):
            return hc.GeminiClient(
                gemini_model=resolved_model,
                effort=effort,
            )

        return _factory
    raise ValueError(f"unknown host {host!r} (expected claude, codex, or gemini)")


def _patch_llmclient(host: str, model: str | None, effort: str):
    """Monkey-patch ``coarse.llm.LLMClient`` and ``StageRouter.client_for``."""
    from coarse import llm as _llm_mod
    from coarse import routing as _routing_mod

    # Save original LLMClient before patching — needed for Perplexity lit
    # search which must go through litellm/OpenRouter, not the headless CLI.
    _OriginalLLMClient = _llm_mod.LLMClient

    factory = _make_client_factory(host, model, effort)

    # Replace the LLMClient class itself so any direct LLMClient(...) call
    # in the pipeline returns a headless client instead.
    _llm_mod.LLMClient = factory  # type: ignore[misc]
    _routing_mod.LLMClient = factory  # type: ignore[misc]

    # Stash original for later use by _patch_literature.
    _patch_llmclient._original = _OriginalLLMClient  # type: ignore[attr-defined]

    def _patched_client_for(self, stage: str):
        if stage not in self._clients:
            self._clients[stage] = factory(stage)
        return self._clients[stage]

    _routing_mod.StageRouter.client_for = _patched_client_for  # type: ignore[assignment]


def _patch_extraction(pre_extracted: Path) -> None:
    """Monkey-patch extract_file to return the pre-extracted markdown."""
    from coarse.types import PaperText

    md_text = pre_extracted.read_text()
    paper_text = PaperText(
        full_markdown=md_text,
        token_estimate=len(md_text) // 4,
        garble_ratio=0.0,
    )

    import coarse.extraction as _ext
    import coarse.pipeline as _pipe

    _ext.extract_file = lambda path, use_cache=True: paper_text  # type: ignore[assignment]
    _pipe.extract_file = lambda path, use_cache=True: paper_text  # type: ignore[assignment]


def run_headless_review(
    paper_path: Path,
    *,
    host: str,
    model: str | None,
    effort: str,
    pre_extracted: Path | None = None,
):
    """Run the full coarse pipeline with a headless CLI backend.

    Returns ``(review, markdown, paper_text)`` — the same shape as
    ``coarse.pipeline.review_paper()``. Caller is responsible for
    writing outputs to disk.

    This is the shared entry point used by both ``main()`` (the CLI
    wrapper) and ``coarse.cli_review.main()`` (the web handoff wrapper).
    Keeping the core logic here means the sidecar-file dance between
    cli_review and headless_review is no longer needed — the caller
    gets the full PaperText object directly.
    """
    _patch_llmclient(host, model, effort)

    if pre_extracted is not None:
        _patch_extraction(pre_extracted)

    # Import AFTER patching so the pipeline's lazy imports pick up
    # the patched LLMClient. Patch the literature module with the
    # real LLMClient (Perplexity needs litellm, not the headless CLI).
    from coarse.agents import literature as _lit_mod
    from coarse.pipeline import review_paper

    _lit_mod.LLMClient = _patch_llmclient._original  # type: ignore[attr-defined]

    return review_paper(
        str(paper_path),
        model=f"headless-{host}",
        skip_cost_gate=True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="coarse.headless_review")
    parser.add_argument(
        "--host",
        choices=["claude", "codex", "gemini"],
        default=os.environ.get("COARSE_HEADLESS_HOST", "claude"),
        help="Which CLI to route LLM calls through",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("COARSE_HEADLESS_MODEL"),
        help="Model ID (host-specific). Defaults to the host's "
        "canonical model: claude-opus-4-6 / gpt-5.4 / gemini-3-pro",
    )
    parser.add_argument(
        "--effort",
        default=os.environ.get("COARSE_HEADLESS_EFFORT", "high"),
        choices=["low", "medium", "high", "max"],
        help="Reasoning effort (low/medium/high/max)",
    )
    parser.add_argument("paper_path", type=Path)
    parser.add_argument("pre_extracted_md", type=Path, nargs="?", default=None)
    parser.add_argument("output_dir", type=Path, nargs="?", default=Path("coarse-output"))
    args = parser.parse_args(argv)

    paper_path = args.paper_path.expanduser()
    if not paper_path.exists():
        print(f"ERROR: paper not found: {paper_path}", file=sys.stderr)
        return 2

    pre_extracted = None
    pre_path_str = str(args.pre_extracted_md) if args.pre_extracted_md else ""
    if pre_path_str and pre_path_str != ".":
        pre_extracted = args.pre_extracted_md.expanduser()
        if not pre_extracted.exists():
            print(
                f"ERROR: pre-extracted markdown not found: {pre_extracted}",
                file=sys.stderr,
            )
            return 2

    out_dir = args.output_dir.expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    if pre_extracted is None:
        _require_openrouter_key()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger = logging.getLogger("coarse.headless_review")

    logger.info(
        "Starting coarse review of %s (host=%s, model=%s, effort=%s)",
        paper_path,
        args.host,
        args.model or _DEFAULT_MODELS[args.host],
        args.effort,
    )

    try:
        review, markdown, _paper = run_headless_review(
            paper_path,
            host=args.host,
            model=args.model,
            effort=args.effort,
            pre_extracted=pre_extracted,
        )
    except ImportError as exc:
        print(
            f"ERROR: coarse-ink not installed ({exc}).\n"
            f"Install with: pip install 'coarse-ink[mcp]'",
            file=sys.stderr,
        )
        return 4

    out_path = out_dir / f"{paper_path.stem}_review.md"
    out_path.write_text(markdown)
    logger.info("Wrote %d-char review to %s", len(markdown), out_path)

    print()
    print("REVIEW COMPLETE")
    print(f"  paper:    {paper_path}")
    print(f"  host:     {args.host}")
    print(f"  comments: {len(review.detailed_comments)}")
    print(f"  output:   {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
