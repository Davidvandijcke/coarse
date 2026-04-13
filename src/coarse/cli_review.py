"""Standalone ``coarse-review`` CLI entry point.

Usage:
    coarse-review <paper_path> [--host ...] [--model ...] [--effort ...]
    coarse-review --handoff <url>   [--host ...] [--model ...] [--effort ...]

Two modes:

1. **Local mode** — ``coarse-review paper.pdf`` runs the full coarse
   pipeline on a local file. Extraction uses the user's OpenRouter
   key (from env, ~/.coarse/config.toml, or a .env file), review
   reasoning uses the chosen headless CLI, output is a local markdown
   file in ``./coarse-output/``.

2. **Handoff mode** — ``coarse-review --handoff <url>`` pulls a handoff
   bundle minted by the coarse.vercel.app web form (paper download URL
   + finalize token + callback URL). Extraction still happens locally
   (faster than waiting on the server); the final review gets POSTed
   back to ``/api/mcp-finalize`` so the user can see it at
   ``coarse.vercel.app/review/<paper_id>`` in the normal web UI.
"""

from __future__ import annotations

import argparse
import logging
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

from coarse.extraction import SUPPORTED_EXTENSIONS

_DEFAULT_MODELS = {
    "claude": "claude-opus-4-6",
    "codex": "gpt-5.4",
    "gemini": "gemini-3.1-pro-preview",
}


def _detect_host() -> str:
    """Return the first headless CLI found on PATH (claude → codex → gemini)."""
    import shutil

    for name, bin_ in (("claude", "claude"), ("codex", "codex"), ("gemini", "gemini")):
        if shutil.which(bin_):
            return name
    raise RuntimeError(
        "No headless CLI found on PATH. Install one of: claude (Claude Code), "
        "codex (OpenAI Codex CLI), or gemini (Google Gemini CLI)."
    )


_CONTENT_TYPE_EXTENSIONS = {
    "application/pdf": ".pdf",
    "application/epub+zip": ".epub",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/msword": ".docx",
    "text/markdown": ".md",
    "text/plain": ".txt",
    "text/html": ".html",
    "application/xhtml+xml": ".html",
    "text/x-tex": ".tex",
    "application/x-tex": ".tex",
}


def _supported_suffix(name: str) -> str | None:
    """Return a supported lowercase suffix extracted from ``name``, if any."""
    suffix = Path(unquote(name)).suffix.lower()
    return suffix if suffix in SUPPORTED_EXTENSIONS else None


def _infer_handoff_extension(
    *,
    paper_title: str = "",
    signed_url: str = "",
    content_type: str = "",
) -> str:
    """Infer the source file extension for a handoff download.

    Handoff mode should support the same formats as ``coarse review``:
    PDF, Markdown, plain text, TeX, HTML, DOCX, and EPUB. Prefer the
    extension from the stored ``paper_title`` (authoritative metadata),
    then the signed download URL path, then the HTTP content type. Fall
    back to ``.pdf`` for backward compatibility with older bundles.
    """
    for candidate in (paper_title, urlsplit(signed_url).path):
        suffix = _supported_suffix(candidate)
        if suffix is not None:
            return suffix

    normalized_type = content_type.split(";", 1)[0].strip().lower()
    return _CONTENT_TYPE_EXTENSIONS.get(normalized_type, ".pdf")


def _fetch_handoff(url: str) -> dict:
    """Fetch the handoff bundle JSON from ``url``.

    Accepts either the short form ``coarse.vercel.app/h/<token>`` or
    ``https://coarse.vercel.app/h/<token>``. The endpoint returns the
    bundle as JSON.
    """
    import requests

    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    # Ask for JSON explicitly — the /h/<token> route serves a landing
    # page to browsers and JSON to API clients that request it.
    resp = requests.get(
        url,
        timeout=30,
        headers={"Accept": "application/json", "User-Agent": "coarse-review-cli/1.0"},
        allow_redirects=True,
    )
    if not resp.ok:
        raise RuntimeError(
            f"Failed to fetch handoff bundle ({url}): HTTP {resp.status_code}. "
            f"The token may have expired (15-min TTL) — re-trigger the handoff "
            f"from the coarse web form."
        )
    try:
        bundle = resp.json()
    except ValueError as exc:
        raise RuntimeError(f"Handoff URL did not return JSON: {resp.text[:200]}") from exc

    signed_download_url = bundle.get("signed_download_url") or bundle.get("signed_pdf_url")
    if signed_download_url:
        bundle["signed_download_url"] = signed_download_url
        # Backward compatibility for any callers still reading the legacy key.
        bundle.setdefault("signed_pdf_url", signed_download_url)

    required = ("paper_id", "finalize_token", "callback_url", "signed_download_url")
    missing = [k for k in required if not bundle.get(k)]
    if missing:
        raise RuntimeError(
            f"Handoff bundle missing required fields: {missing}. Got: {list(bundle.keys())}"
        )
    return bundle


def _download_handoff_source(bundle: dict, dest_dir: Path) -> Path:
    """Download the handoff source file into ``dest_dir``.

    Despite the historical ``signed_pdf_url`` field name, CLI handoffs can
    reference any reviewable source format. Preserve the original extension
    so ``extract_file()`` takes the correct path and only uses OCR for PDFs.
    """
    import requests

    signed_url = bundle["signed_download_url"]
    with requests.get(signed_url, stream=True, timeout=120) as resp:
        resp.raise_for_status()
        ext = _infer_handoff_extension(
            paper_title=str(bundle.get("paper_title", "")),
            signed_url=resp.url or signed_url,
            content_type=resp.headers.get("content-type", ""),
        )
        dest = dest_dir / f"{bundle['paper_id']}{ext}"
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
    return dest


def _post_finalize(
    *,
    callback_url: str,
    finalize_token: str,
    paper_id: str,
    paper_title: str,
    domain: str,
    taxonomy: str,
    markdown: str,
    paper_markdown: str,
    host_label: str,
) -> dict:
    """POST the rendered review back to coarse.vercel.app/api/mcp-finalize."""
    import requests

    payload = {
        "token": finalize_token,
        "paper_id": paper_id,
        "paper_title": paper_title,
        "domain": domain,
        "taxonomy": taxonomy,
        "markdown": markdown,
        "paper_markdown": paper_markdown,
        "model": f"coarse-review-cli:{host_label}",
    }
    resp = requests.post(
        callback_url,
        json=payload,
        timeout=60,
        headers={"Content-Type": "application/json"},
    )
    if not resp.ok:
        raise RuntimeError(
            f"Callback to {callback_url} failed: HTTP {resp.status_code} — {resp.text[:300]}"
        )
    try:
        return resp.json()
    except ValueError:
        return {}


def _print_completion_footer(
    *,
    local_path: Path,
    review_url: str | None = None,
    callback_failed: bool = False,
    callback_error: str | None = None,
) -> None:
    """Print a machine-parsable completion footer for coding agents.

    The handoff prompts tell agents to parse `view:` / `local:` from the
    log after the background job completes. Make those lines available in
    every terminal outcome, including web-callback failures.
    """
    print()
    if callback_failed:
        print("WEB CALLBACK FAILED")
        if callback_error:
            print(f"  error:    {callback_error}")
        print("  view:     unavailable")
    elif review_url:
        print("PUBLISHED TO COARSE WEB")
        print(f"  view:     {review_url}")
    print(f"  local:    {local_path.resolve()}")
    print("REVIEW COMPLETE")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="coarse-review",
        description="Run the full coarse review pipeline using a headless CLI.",
    )
    parser.add_argument(
        "paper_path",
        type=Path,
        nargs="?",
        help="Local paper file (PDF, MD, TeX, DOCX, HTML, EPUB). Omit when using --handoff.",
    )
    parser.add_argument(
        "--handoff",
        metavar="URL",
        help="Handoff URL from the coarse web form (coarse.vercel.app/h/<token>).",
    )
    parser.add_argument(
        "--host",
        choices=["claude", "codex", "gemini"],
        default=None,
        help="Which headless CLI to use. Defaults to whichever is installed first.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Host-specific model ID (e.g. claude-sonnet-4-6, gpt-5, gemini-3-flash). "
        "Defaults to the host's canonical model.",
    )
    parser.add_argument(
        "--effort",
        choices=["low", "medium", "high", "max"],
        default="high",
        help="Reasoning effort level (default: high)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("coarse-output"),
        help="Where to write the final review markdown (default: ./coarse-output/)",
    )
    parser.add_argument(
        "--pre-extracted",
        type=Path,
        default=None,
        help="Pre-extracted markdown file — skips Mistral OCR (useful when "
        "you already have the paper extracted from a previous run).",
    )
    args = parser.parse_args(argv)

    if not args.handoff and not args.paper_path:
        parser.error("either paper_path or --handoff is required")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger = logging.getLogger("coarse-review")

    try:
        host = args.host or _detect_host()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 5

    model = args.model or _DEFAULT_MODELS[host]
    effort = args.effort

    # Handoff mode: fetch bundle, download the source file to temp, then run like local mode.
    handoff_bundle: dict | None = None
    temp_source: Path | None = None

    if args.handoff:
        logger.info("Fetching handoff bundle from %s", args.handoff)
        handoff_bundle = _fetch_handoff(args.handoff)
        tmpdir = Path(tempfile.mkdtemp(prefix="coarse-review-"))
        temp_source = _download_handoff_source(handoff_bundle, tmpdir)
        logger.info("Downloading paper to %s", temp_source)
        if temp_source.suffix.lower() != ".pdf":
            logger.info(
                "Non-PDF handoff detected (%s); using direct extraction without OCR",
                temp_source.suffix.lower() or "<no extension>",
            )
        paper_path = temp_source
    else:
        paper_path = args.paper_path.expanduser()
        if not paper_path.exists():
            print(f"ERROR: paper not found: {paper_path}", file=sys.stderr)
            return 2

    out_dir = args.output_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Call the pipeline directly so we get the PaperText back in-process
    # (no sidecar file dance). run_headless_review handles all the
    # monkey-patching for the chosen host.
    from coarse.headless_review import run_headless_review

    logger.info(
        "Running coarse pipeline (host=%s, model=%s, effort=%s)",
        host,
        model,
        effort,
    )

    try:
        review, md_text, paper_text = run_headless_review(
            paper_path,
            host=host,
            model=model,
            effort=effort,
            pre_extracted=args.pre_extracted.expanduser() if args.pre_extracted else None,
        )
    except Exception as exc:
        print(f"ERROR: pipeline failed — {exc}", file=sys.stderr)
        return 6

    # Save the review markdown locally regardless of mode.
    review_md_path = out_dir / f"{paper_path.stem}_review.md"
    review_md_path.write_text(md_text)
    logger.info("Wrote %d-char review to %s", len(md_text), review_md_path)

    # Handoff mode: POST the review back to coarse web.
    if handoff_bundle is not None:
        logger.info(
            "POSTing review back to %s",
            handoff_bundle["callback_url"],
        )
        try:
            # Use the paper metadata from the Review object (authoritative).
            title = review.title or handoff_bundle.get("paper_title", "Untitled")
            domain = review.domain or handoff_bundle.get("domain", "unknown")
            taxonomy = review.taxonomy or handoff_bundle.get("taxonomy", "")

            # Use the extracted paper_text directly — no sidecar file.
            paper_markdown = paper_text.full_markdown
            logger.info(
                "Including %d-char paper markdown in finalize POST",
                len(paper_markdown),
            )

            resp = _post_finalize(
                callback_url=handoff_bundle["callback_url"],
                finalize_token=handoff_bundle["finalize_token"],
                paper_id=handoff_bundle["paper_id"],
                paper_title=title,
                domain=domain,
                taxonomy=taxonomy,
                markdown=md_text,
                paper_markdown=paper_markdown,
                host_label=host,
            )
            review_url = resp.get("review_url", "")
            _print_completion_footer(
                local_path=review_md_path,
                review_url=review_url or None,
            )
        except Exception as exc:
            _print_completion_footer(
                local_path=review_md_path,
                callback_failed=True,
                callback_error=str(exc),
            )
            return 7

    if handoff_bundle is None:
        _print_completion_footer(local_path=review_md_path)

    # Clean up temp source file if we downloaded one.
    if temp_source is not None and temp_source.exists():
        try:
            temp_source.unlink()
            temp_source.parent.rmdir()
        except OSError:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
