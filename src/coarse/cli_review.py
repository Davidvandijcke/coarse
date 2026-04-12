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

_DEFAULT_MODELS = {
    "claude": "claude-opus-4-6",
    "codex": "gpt-5-codex",
    "gemini": "gemini-3-pro",
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

    required = ("paper_id", "signed_pdf_url", "finalize_token", "callback_url")
    missing = [k for k in required if k not in bundle]
    if missing:
        raise RuntimeError(
            f"Handoff bundle missing required fields: {missing}. Got: {list(bundle.keys())}"
        )
    return bundle


def _download_pdf(signed_url: str, dest: Path) -> None:
    """Stream the PDF at ``signed_url`` into ``dest``."""
    import requests

    with requests.get(signed_url, stream=True, timeout=120) as resp:
        resp.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)


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

    # Handoff mode: fetch bundle, download PDF to temp, then run like local mode.
    handoff_bundle: dict | None = None
    temp_pdf: Path | None = None

    if args.handoff:
        logger.info("Fetching handoff bundle from %s", args.handoff)
        handoff_bundle = _fetch_handoff(args.handoff)
        tmpdir = Path(tempfile.mkdtemp(prefix="coarse-review-"))
        temp_pdf = tmpdir / f"{handoff_bundle['paper_id']}.pdf"
        logger.info("Downloading paper to %s", temp_pdf)
        _download_pdf(handoff_bundle["signed_pdf_url"], temp_pdf)
        paper_path = temp_pdf
    else:
        paper_path = args.paper_path.expanduser()
        if not paper_path.exists():
            print(f"ERROR: paper not found: {paper_path}", file=sys.stderr)
            return 2

    out_dir = args.output_dir.expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Delegate to the shared headless_review driver for the actual pipeline.
    # Pass host/model/effort via env vars since the underlying main() reads
    # them. We also pass them as real argparse args when we invoke it.
    from coarse.headless_review import main as run_headless

    forwarded = ["--host", host, "--effort", effort]
    if model:
        forwarded += ["--model", model]
    forwarded += [str(paper_path)]
    if args.pre_extracted:
        forwarded += [str(args.pre_extracted.expanduser())]
    else:
        forwarded += [""]  # positional placeholder
    forwarded += [str(out_dir)]

    logger.info(
        "Running coarse pipeline (host=%s, model=%s, effort=%s)",
        host,
        model,
        effort,
    )

    rc = run_headless(forwarded)
    if rc != 0:
        return rc

    # Locate the output markdown the pipeline just wrote.
    review_md_path = out_dir / f"{paper_path.stem}_review.md"
    if not review_md_path.exists():
        print(
            f"ERROR: pipeline completed but no review markdown found at {review_md_path}",
            file=sys.stderr,
        )
        return 6

    # Handoff mode: POST the review back to coarse web.
    if handoff_bundle is not None:
        logger.info(
            "POSTing review back to %s",
            handoff_bundle["callback_url"],
        )
        try:
            # Recover paper metadata from the rendered markdown header.
            md_text = review_md_path.read_text()
            title = _parse_md_header(md_text, "# ") or handoff_bundle.get("paper_title", "Untitled")
            domain = _parse_md_header(md_text, "**Domain**: ") or handoff_bundle.get(
                "domain", "unknown"
            )
            taxonomy = _parse_md_header(md_text, "**Taxonomy**: ") or handoff_bundle.get(
                "taxonomy", ""
            )

            # We don't have the original paper_markdown here (coarse's
            # extract_file result isn't persisted across main()). Pass empty
            # — the web side can render the review without the side-by-side
            # view. Populating it would require the pipeline to save a
            # paper_markdown dump; that's a future enhancement.
            resp = _post_finalize(
                callback_url=handoff_bundle["callback_url"],
                finalize_token=handoff_bundle["finalize_token"],
                paper_id=handoff_bundle["paper_id"],
                paper_title=title,
                domain=domain,
                taxonomy=taxonomy,
                markdown=md_text,
                paper_markdown="",
                host_label=host,
            )
            review_url = resp.get("review_url", "")
            print()
            print("PUBLISHED TO COARSE WEB")
            if review_url:
                print(f"  view:     {review_url}")
            print(f"  local:    {review_md_path}")
        except Exception as exc:
            print()
            print("WARNING: local review complete but web callback failed:")
            print(f"  {exc}")
            print(f"  Review is still available locally at: {review_md_path}")
            return 7

    # Clean up temp PDF if we downloaded one.
    if temp_pdf is not None and temp_pdf.exists():
        try:
            temp_pdf.unlink()
            temp_pdf.parent.rmdir()
        except OSError:
            pass

    return 0


def _parse_md_header(md: str, prefix: str) -> str:
    """Pull a value from the markdown header (e.g. ``# Title`` or
    ``**Domain**: X``). Returns empty string if not found."""
    for line in md.splitlines()[:30]:
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return ""


if __name__ == "__main__":
    sys.exit(main())
