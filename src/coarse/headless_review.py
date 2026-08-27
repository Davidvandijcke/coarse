"""Entry point for running the full coarse review pipeline with a headless CLI.

Usage:
    python -m coarse.headless_review --host <claude|codex|gemini> \\
        <paper_path> [<pre_extracted_md>] [<output_dir>]

- ``--host``: which CLI to route review-reasoning calls through. PDF
  extraction QA keeps its configured vision-model route.
- ``<paper_path>``: PDF, MD, TeX, DOCX, HTML, or EPUB.
- ``<pre_extracted_md>``: optional pre-extracted markdown — skips OCR,
  saves ~$0.05-0.15 and ~30 seconds.
- ``<output_dir>``: where to write ``<stem>_review_<model>.md``. Default:
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

from coarse.models import HEADLESS_DEFAULT_MODELS, model_filename_slug

# Shared guidance for a missing/invalid OpenRouter key. Used by both
# headless_review (sys.exit) and cli_review (return-code preflight) so the
# two entrypoints stay in lockstep. The first line is also a recognized
# --attach failure marker (cli_attach._ATTACH_FAILURE_MARKERS); keep them in
# sync if this wording changes.
_OPENROUTER_KEY_HELP = (
    "ERROR: No valid OpenRouter API key found (keys look like `sk-or-...`).\n\n"
    "PDF OCR and post-extraction vision QA require an OpenRouter API key. "
    "Any of these work:\n"
    "  1. Run `coarse setup` to save it to ~/.coarse/config.toml\n"
    "  2. export OPENROUTER_API_KEY=sk-or-v1-...\n"
    "  3. Add OPENROUTER_API_KEY=sk-or-v1-... to a .env file in the\n"
    "     current directory (or any parent directory, up to 3 levels) if\n"
    "     you explicitly prefer project-local storage.\n\n"
    "Alternatively, if you have a pre-extracted markdown file, pass it\n"
    "as the second argument to skip OCR:\n"
    "  python -m coarse.headless_review --host claude <paper.pdf> <paper.md>\n\n"
    "Get a free OpenRouter key at https://openrouter.ai/settings/keys — "
    "PDF OCR costs ~$0.05-0.15 per paper; vision QA adds a small charge when it runs."
)

_DEEP_LITERATURE_KEY_HELP = (
    "ERROR: Deep literature search requires a valid OpenRouter API key "
    "(keys look like `sk-or-...`).\n\n"
    "Set OPENROUTER_API_KEY, add it to ./.env, or save it in "
    "~/.coarse/config.toml, then retry.\n"
    "Get a key at https://openrouter.ai/settings/keys."
)


def _looks_like_openrouter_key(value: str | None) -> bool:
    """True only for a plausibly real OpenRouter key (``sk-or-…``).

    OpenRouter inference and provisioning keys are all ``sk-or-`` prefixed.
    Rejecting everything else turns config junk — a literal ``"FROM_ENV"``
    placeholder, a blank/quoted entry, or a top-level string mis-set under
    ``[api_keys]`` — into "absent" so it is never forwarded as
    ``Authorization: Bearer <junk>``, which otherwise surfaces as an opaque
    401 deep inside extraction instead of a clean missing-key error (#197).
    """
    return bool(value) and value.strip().startswith("sk-or-")


def _find_openrouter_key() -> str | None:
    """Find an OpenRouter key from env var, ~/.coarse/config.toml, or ./.env
    (up to 3 parents up), in that priority order.

    Only a value that looks like a real key (``sk-or-…``) is accepted; a
    non-key value from any source is skipped so resolution falls through to
    the next source rather than returning junk that would 401 (#197).
    """
    env_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if _looks_like_openrouter_key(env_key):
        return env_key

    try:
        import tomllib
    except ImportError:
        tomllib = None  # type: ignore[assignment]

    config_path = Path.home() / ".coarse" / "config.toml"
    if config_path.exists() and tomllib is not None:
        try:
            with open(config_path, "rb") as f:
                data = tomllib.load(f)
            stored = (
                data.get("api_keys", {}).get("openrouter")
                or data.get("openrouter_api_key")
                or data.get("openrouter", {}).get("api_key")
            )
            if _looks_like_openrouter_key(stored):
                return stored.strip()
        except Exception:
            pass

    for base in [Path.cwd(), *Path.cwd().parents[:3]]:
        env_path = base / ".env"
        if not env_path.exists():
            continue
        try:
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == "OPENROUTER_API_KEY":
                    candidate = v.strip().strip("\"'")
                    if _looks_like_openrouter_key(candidate):
                        return candidate
        except Exception:
            continue

    return None


def _require_openrouter_key() -> str:
    key = _find_openrouter_key()
    if key:
        os.environ["OPENROUTER_API_KEY"] = key
        return key

    print(_OPENROUTER_KEY_HELP, file=sys.stderr)
    sys.exit(3)


def openrouter_key_preflight_error(
    paper_path: Path,
    pre_extracted: Path | None,
    *,
    deep_literature_search: bool = False,
) -> str | None:
    """Return guidance if a requested stage needs a missing OpenRouter key.

    PDFs need the key for OCR. Opt-in deep literature search needs it for every
    source format; unlike the standard search, silently dropping to arXiv would
    violate the user's explicit depth choice. Reads ``os.environ`` — callers
    must load config/.env first so this check is authoritative.
    """
    if _looks_like_openrouter_key(os.environ.get("OPENROUTER_API_KEY")):
        return None
    if deep_literature_search:
        return _DEEP_LITERATURE_KEY_HELP
    if pre_extracted is not None or paper_path.suffix.lower() != ".pdf":
        return None
    return _OPENROUTER_KEY_HELP


def _make_client_factory(
    host: str,
    model: str | None,
    effort: str,
    *,
    api_client_factory=None,
):
    from coarse import headless_clients as hc

    host = host.lower()
    resolved_model = model or HEADLESS_DEFAULT_MODELS[host]

    # The factory replaces coarse.llm.LLMClient at monkey-patch time, so it
    # gets called with whatever kwargs the pipeline passes to LLMClient:
    # `stage` from ReviewAgent.build_client(), but also `model=...` /
    # `config=...` from pipeline.py's direct `LLMClient(model=..., config=...)`
    # calls. Review calls carry the synthetic `headless-<host>` model marker;
    # an explicit different model is a stage-specific route (currently the
    # extraction-QA vision model) and must stay on the real API client so its
    # multimodal content survives.
    if host == "claude":

        def _headless_factory(stage: str = "", *_args, **_kwargs):
            return hc.ClaudeCodeClient(
                claude_model=resolved_model,
                effort=effort,
            )
    elif host == "codex":

        def _headless_factory(stage: str = "", *_args, **_kwargs):
            return hc.CodexClient(
                codex_model=resolved_model,
                effort=effort,
            )
    elif host == "gemini":

        def _headless_factory(stage: str = "", *_args, **_kwargs):
            return hc.GeminiClient(
                gemini_model=resolved_model,
                effort=effort,
            )
    else:
        raise ValueError(f"unknown host {host!r} (expected claude, codex, or gemini)")

    if api_client_factory is None:
        return _headless_factory

    review_model_marker = f"headless-{host}"

    def _routed_factory(stage: str = "", *_args, **_kwargs):
        requested_model = _kwargs.get("model")
        if requested_model is not None and requested_model != review_model_marker:
            # LLMClient's real constructor does not accept the headless-only
            # `stage` argument. Pipeline stage-specific clients use keyword
            # `model=` / `config=`, so forward that supported call shape.
            return api_client_factory(**_kwargs)
        return _headless_factory(stage, *_args, **_kwargs)

    return _routed_factory


def _patch_llmclient(host: str, model: str | None, effort: str):
    """Monkey-patch ``coarse.llm.LLMClient`` so the pipeline uses the headless host."""
    from coarse import llm as _llm_mod

    # Save the original LLMClient before patching. Reuse the first captured
    # class if a process runs more than one headless review; otherwise the
    # second run would mistake the prior routed factory for the API client.
    _OriginalLLMClient = getattr(_patch_llmclient, "_original", _llm_mod.LLMClient)

    factory = _make_client_factory(
        host,
        model,
        effort,
        api_client_factory=_OriginalLLMClient,
    )

    # Replace the LLMClient class so review-model construction returns a
    # headless client while explicit stage-specific models keep the API route.
    _llm_mod.LLMClient = factory  # type: ignore[misc]

    # Also patch the name imported into pipeline.py (it did `from coarse.llm
    # import LLMClient`, so the monkey-patch on the module isn't seen by
    # already-imported references).
    import coarse.pipeline as _pipe_mod

    _pipe_mod.LLMClient = factory  # type: ignore[misc]

    # Stash original for later use by _patch_literature.
    _patch_llmclient._original = _OriginalLLMClient  # type: ignore[attr-defined]


def _patch_extraction(pre_extracted: Path) -> None:
    """Monkey-patch extract_file to return the pre-extracted markdown."""
    from coarse.textscript import estimate_tokens
    from coarse.types import PaperText

    md_text = pre_extracted.read_text(encoding="utf-8")
    paper_text = PaperText(
        full_markdown=md_text,
        token_estimate=estimate_tokens(md_text),
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
    language: str | None = None,
    deep_literature_search: bool = False,
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

    review_kwargs = {
        "model": f"headless-{host}",
        "skip_cost_gate": True,
        "language": language,
    }
    if deep_literature_search:
        review_kwargs["deep_literature_search"] = True
    return review_paper(str(paper_path), **review_kwargs)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="coarse.headless_review")
    parser.add_argument(
        "--host",
        choices=["claude", "codex", "gemini"],
        default=os.environ.get("COARSE_HEADLESS_HOST", "claude"),
        help="Which CLI to route LLM calls through",
    )
    _canonical_help = " / ".join(
        f"{host}={model}" for host, model in HEADLESS_DEFAULT_MODELS.items()
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("COARSE_HEADLESS_MODEL"),
        help=(
            f"Model ID (host-specific). Defaults to the host's canonical model ({_canonical_help})."
        ),
    )
    parser.add_argument(
        "--effort",
        default=os.environ.get("COARSE_HEADLESS_EFFORT", "high"),
        choices=["low", "medium", "high", "max"],
        help="Reasoning effort (low/medium/high/max)",
    )
    parser.add_argument(
        "--language",
        default=os.environ.get("COARSE_REVIEW_LANGUAGE"),
        help="Language for the review output (e.g. 'Spanish', 'French'); default English.",
    )
    parser.add_argument(
        "--deep-literature-search",
        action="store_true",
        help="Use Perplexity Sonar Deep Research for the literature pass.",
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

    needs_openrouter_key = (
        pre_extracted is None and paper_path.suffix.lower() == ".pdf"
    ) or args.deep_literature_search
    if needs_openrouter_key:
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
        args.model or HEADLESS_DEFAULT_MODELS[args.host],
        args.effort,
    )

    try:
        headless_kwargs = {
            "host": args.host,
            "model": args.model,
            "effort": args.effort,
            "pre_extracted": pre_extracted,
            "language": args.language,
        }
        if args.deep_literature_search:
            headless_kwargs["deep_literature_search"] = True
        review, markdown, _paper = run_headless_review(paper_path, **headless_kwargs)
    except ImportError as exc:
        print(
            f"ERROR: coarse-ink not installed ({exc}).\nInstall with: pip install coarse-ink",
            file=sys.stderr,
        )
        return 4

    if args.model:
        out_path = out_dir / f"{paper_path.stem}_review_{model_filename_slug(args.model)}.md"
    else:
        out_path = out_dir / f"{paper_path.stem}_review.md"
    out_path.write_text(markdown, encoding="utf-8")
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
