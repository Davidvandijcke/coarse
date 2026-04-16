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
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

from coarse.cli_attach import (
    ATTACH_DEFAULT_TIMEOUT_SECONDS,
    handle_watcher_interrupt,
    pidfile_for_log,
    register_pidfile_cleanup,
    run_attach,
    write_pidfile,
)
from coarse.extraction import SUPPORTED_EXTENSIONS
from coarse.models import HEADLESS_DEFAULT_MODELS, model_filename_slug

_DETACHED_ENV = "COARSE_REVIEW_DETACHED"
# Informational only: must match FINALIZE_TOKEN_TTL_MINUTES in
# web/src/app/api/cli-handoff/route.ts. Only surfaced in CLI error
# messages — the server is authoritative and a mismatch is cosmetic.
FINALIZE_TOKEN_TTL_MINUTES = 180


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


def _scrub_url(url: str) -> str:
    """Strip the query string from a URL before interpolating it into an
    error message or log line.

    On preview deploys, `/api/cli-handoff` and `/h/[token]` append
    `?x-vercel-protection-bypass=<VERCEL_AUTOMATION_BYPASS_SECRET>`
    to the handoff and callback URLs via `appendPreviewBypassQuery`.
    That secret must never land in a CLI stderr line or the detached
    log file (which coding agents routinely capture and grep).
    Stripping the query string also removes any Supabase signed-URL
    token, so the same helper is reused on `signed_download_url`.

    Path + scheme + host are preserved so the error is still useful
    for the human reading it.
    """
    try:
        from urllib.parse import urlsplit, urlunsplit

        parts = urlsplit(url)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    except Exception:
        # Last-resort: chop at the first `?` by string slicing, which
        # is correct for any valid URL and safe even on garbled input.
        return url.split("?", 1)[0]


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
        # 401/403 are almost never a coarse-side failure: the /h/<token>
        # route returns 400/404/410/503/500, so a 401/403 means the
        # request was stopped by Vercel Deployment Protection before it
        # even reached the Next.js route. This happens when the handoff
        # URL points at a preview deployment without a configured
        # VERCEL_AUTOMATION_BYPASS_SECRET.
        if resp.status_code in (401, 403):
            hint = (
                "HTTP 401/403 — the handoff URL is behind Vercel Preview "
                "Protection. The operator needs to set "
                "VERCEL_AUTOMATION_BYPASS_SECRET on the preview "
                "environment (see deploy/PREVIEW_ENVIRONMENTS.md)."
            )
        elif resp.status_code == 410:
            hint = (
                f"HTTP 410 — the handoff token has expired or already "
                f"been consumed. Tokens live for {FINALIZE_TOKEN_TTL_MINUTES} "
                "minutes; re-trigger the handoff from the coarse web form."
            )
        elif resp.status_code == 404:
            hint = (
                "HTTP 404 — token not found or the paper row was deleted. "
                "Re-trigger the handoff from the coarse web form."
            )
        else:
            hint = f"HTTP {resp.status_code} — re-trigger the handoff from the coarse web form."
        raise RuntimeError(f"Failed to fetch handoff bundle ({_scrub_url(url)}): {hint}")
    try:
        bundle = resp.json()
    except ValueError as exc:
        # Don't interpolate `resp.text` — an error body from Vercel can
        # contain the bypass secret query string (echoed from the URL)
        # or upstream auth hints. Log the first 120 chars with any
        # URL-shaped substrings scrubbed instead.
        body_preview = _scrub_url(resp.text[:200]) if resp.text else ""
        raise RuntimeError(f"Handoff URL did not return JSON: {body_preview[:120]}") from exc

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


_POST_FINALIZE_MAX_ATTEMPTS = 3
_POST_FINALIZE_RETRY_BACKOFF_SECONDS = (2.0, 4.0, 8.0)


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
    """POST the rendered review back to coarse.vercel.app/api/mcp-finalize.

    Retries up to ``_POST_FINALIZE_MAX_ATTEMPTS`` times on transient
    failure classes (connection error, timeout, 429, 5xx) with
    exponential backoff. Permanent 4xx failures (except 429) fail
    fast — retrying an invalid-token 401 or a malformed-payload 400
    will not help, and keeps the user's terminal blocked for no
    benefit. The user has already waited 10-25 minutes for the
    review; losing it to a single transient blip would be a poor
    trade-off.

    Token consumption is server-side atomic (`UPDATE ... WHERE
    consumed_at IS NULL` in `/api/mcp-finalize`), so retrying a
    transient failure is safe — either the first attempt already
    persisted the review (and the retry gets a 410) or it didn't
    (and the retry gets a fresh 200).
    """
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

    last_exc: Exception | None = None
    last_status: int | None = None
    last_body: str = ""
    for attempt in range(_POST_FINALIZE_MAX_ATTEMPTS):
        if attempt > 0:
            import time

            sleep_seconds = _POST_FINALIZE_RETRY_BACKOFF_SECONDS[
                min(attempt - 1, len(_POST_FINALIZE_RETRY_BACKOFF_SECONDS) - 1)
            ]
            print(
                f"[post_finalize] retry {attempt + 1}/{_POST_FINALIZE_MAX_ATTEMPTS} "
                f"after {sleep_seconds:.0f}s backoff",
                file=sys.stderr,
            )
            time.sleep(sleep_seconds)
        try:
            resp = requests.post(
                callback_url,
                json=payload,
                timeout=60,
                headers={"Content-Type": "application/json"},
            )
        except (requests.ConnectionError, requests.Timeout) as exc:
            last_exc = exc
            continue

        if resp.ok:
            try:
                return resp.json()
            except ValueError:
                return {}

        last_status = resp.status_code
        last_body = resp.text[:300] if resp.text else ""
        # Transient failure classes: 429 and any 5xx. Everything else
        # is a permanent failure (400 invalid payload, 401 bad token,
        # 403 token mismatch, 404 paper row deleted, 410 token already
        # consumed) — retrying won't help and just wastes the user's
        # time. Fail fast.
        if resp.status_code != 429 and resp.status_code < 500:
            break

    # All attempts exhausted or permanent failure.
    body_preview = _scrub_url(last_body) if last_body else ""
    if last_exc is not None:
        raise RuntimeError(
            f"Callback to {_scrub_url(callback_url)} failed after "
            f"{_POST_FINALIZE_MAX_ATTEMPTS} attempts: "
            f"{type(last_exc).__name__}: {last_exc}"
        )
    raise RuntimeError(
        f"Callback to {_scrub_url(callback_url)} failed: HTTP {last_status} — {body_preview[:200]}"
    )


def _format_hyperlink(url: str) -> str:
    """Render ``url`` as an OSC 8 hyperlink when stdout is a real TTY.

    Modern terminals (iTerm2, Kitty, GNOME Terminal, Wezterm, etc.)
    render the OSC 8 escape sequence as clickable text. Terminals that
    do not support it (dumb pipes, most CI log captures, older xterm)
    either strip the escape silently or render the raw text. We only
    emit the escape when stdout is a TTY so that log captures, Claude
    Code's Bash tool output, and pytest fixtures see a plain URL they
    can parse.

    Returned text displays as the URL itself — not as a custom label —
    so the `view:` line remains grep-friendly for agents that parse
    the log on the backend (buildAgentPrompt instructs them to do so).
    """
    if not url:
        return url
    try:
        if not sys.stdout.isatty():
            return url
    except (AttributeError, ValueError):
        return url
    # OSC 8 ; params ; URI ST  <text>  OSC 8 ; ; ST
    return f"\x1b]8;;{url}\x1b\\{url}\x1b]8;;\x1b\\"


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
        print(f"  view:     {_format_hyperlink(review_url)}")
    print(f"  local:    {local_path.resolve()}")
    print("REVIEW COMPLETE")


def _ensure_openrouter_key_loaded(pre_extracted: Path | None) -> None:
    """Load OPENROUTER_API_KEY from env/config/.env before extraction starts."""
    if pre_extracted is not None:
        return

    from coarse.headless_review import _find_openrouter_key

    key = _find_openrouter_key()
    if key:
        os.environ["OPENROUTER_API_KEY"] = key


def _open_detached_log(log_path: Path):
    """Open the detached log with owner-only permissions where supported."""
    if os.name == "nt":
        return open(log_path, "w", encoding="utf-8")

    fd = os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.fchmod(fd, 0o600)
    except OSError:
        pass
    return os.fdopen(fd, "w", encoding="utf-8")


def _detach_review_process(argv: list[str], log_file: Path) -> int:
    """Respawn this CLI in a detached child process and return immediately.

    In addition to printing ``Review PID`` / ``Log file`` to stdout for
    humans and shell captures, writes ``<log>.pid`` via
    ``cli_attach.write_pidfile`` so a subsequent
    ``coarse-review --attach <log>`` invocation can discover the PID
    without having to parse stdout. The detached child itself removes
    the pidfile on its own exit via ``register_pidfile_cleanup``.
    """
    log_path = log_file.expanduser().resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    env[_DETACHED_ENV] = "1"
    # Force UTF-8 everywhere in the detached child, regardless of
    # the parent's locale. On Windows, the default text-mode encoding
    # is `cp1252` (or another legacy codepage), which crashes with
    # `UnicodeEncodeError: 'charmap' codec can't encode character`
    # the moment the pipeline touches non-ASCII paper content
    # (Greek letters, math arrows, em dashes — everything a real
    # academic paper contains). `PYTHONUTF8=1` is Python's
    # documented switch for UTF-8 Mode, which overrides
    # `locale.getpreferredencoding(False)` for every `open()`,
    # `sys.stdout`, `sys.stderr`, and `subprocess` text pipe in the
    # child process. `PYTHONIOENCODING=utf-8` is belt-and-suspenders
    # for older Python paths that don't honour UTF-8 Mode fully.
    # Parent env stays untouched — only the detached worker gets
    # the override. See: https://docs.python.org/3/library/os.html#utf8-mode
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    cmd = [sys.executable, "-m", "coarse.cli_review", *argv]
    popen_kwargs: dict[str, object] = {
        "stdin": subprocess.DEVNULL,
        "stdout": _open_detached_log(log_path),
        "stderr": subprocess.STDOUT,
        "cwd": str(Path.cwd()),
        "env": env,
        "close_fds": True,
    }
    if os.name == "nt":
        popen_kwargs["creationflags"] = (
            subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        )
    else:
        popen_kwargs["start_new_session"] = True

    proc = subprocess.Popen(cmd, **popen_kwargs)
    pidfile = pidfile_for_log(log_path)
    try:
        write_pidfile(pidfile, proc.pid)
    except OSError as exc:
        # Pidfile is a nice-to-have — the legacy polling path still
        # works without it. Warn on stderr so the caller knows
        # ``--attach`` won't be available for this run.
        print(
            f"warning: could not write pidfile {pidfile}: {exc}",
            file=sys.stderr,
        )
    print(f"Review PID: {proc.pid}")
    print(f"Log file:   {log_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
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
    parser.add_argument(
        "--detach",
        action="store_true",
        help="Start the review in a detached background process and return immediately.",
    )
    parser.add_argument(
        "--attach",
        metavar="LOG",
        type=Path,
        default=None,
        help="Watch a previously-detached review by log path. Blocks until "
        "the review finishes, streaming log content to stdout and emitting "
        "a heartbeat every 30s. Mutually exclusive with --detach and with "
        "a paper path / --handoff. Uses `<log>.pid` written by --detach to "
        "find the worker PID.",
    )
    parser.add_argument(
        "--attach-timeout",
        type=int,
        default=ATTACH_DEFAULT_TIMEOUT_SECONDS,
        help=(
            f"Max seconds --attach will wait before giving up "
            f"(default: {ATTACH_DEFAULT_TIMEOUT_SECONDS}, exit 124 on "
            "timeout). The watcher gives up but does NOT kill the "
            "detached worker."
        ),
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=Path("/tmp/coarse-review.log"),
        help="Log path used with --detach (default: /tmp/coarse-review.log).",
    )
    args = parser.parse_args(argv)

    # --attach is a watch-only mode that does NOT run the pipeline.
    # It must be mutually exclusive with anything that starts a review.
    if args.attach is not None:
        exclusive_conflicts = []
        if args.detach:
            exclusive_conflicts.append("--detach")
        if args.handoff:
            exclusive_conflicts.append("--handoff")
        if args.paper_path:
            exclusive_conflicts.append("<paper_path>")
        if args.pre_extracted:
            exclusive_conflicts.append("--pre-extracted")
        if exclusive_conflicts:
            parser.error(
                "--attach is mutually exclusive with "
                + ", ".join(exclusive_conflicts)
                + " (it only watches an existing detached run; "
                "it does not launch a new one)"
            )
        try:
            return run_attach(args.attach, timeout_seconds=args.attach_timeout)
        except KeyboardInterrupt:
            # Ctrl+C on the watcher MUST NOT kill the detached worker.
            # handle_watcher_interrupt prints the detach notice + re-attach
            # hint and returns the standard SIGINT exit code (130).
            return handle_watcher_interrupt(args.attach)

    if not args.handoff and not args.paper_path:
        parser.error("either paper_path or --handoff is required")

    if args.detach and os.environ.get(_DETACHED_ENV) != "1":
        return _detach_review_process(argv, args.log_file)

    # Inside the detached child: register the pidfile cleanup so an
    # orderly exit from the detached worker unlinks its own pidfile.
    # The watcher is also idempotent about cleanup, so a crash-exit
    # that skips atexit just leaves cleanup to --attach.
    if os.environ.get(_DETACHED_ENV) == "1":
        register_pidfile_cleanup(args.log_file)

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

    model = args.model or HEADLESS_DEFAULT_MODELS[host]
    effort = args.effort

    # Handoff mode: fetch bundle, download the source file to temp, then
    # run like local mode. Everything from here to the end of main() is
    # wrapped in a single outer try/finally so the handoff tempdir gets
    # cleaned up regardless of which stage fails — fetch, download,
    # pipeline, or finalize POST. Earlier revisions had three separate
    # cleanup blocks and a pipeline-failure path that leaked
    # `/tmp/coarse-review-*` dirs across invocations.
    handoff_bundle: dict | None = None
    # Track the tempfile.mkdtemp result separately from temp_source so the
    # cleanup in the ``finally`` below unlinks the right directory even when
    # test mocks replace _download_handoff_source with a fixture file whose
    # ``.parent`` is NOT the handoff tempdir (e.g. the pytest tmp_path).
    handoff_tmpdir: Path | None = None
    callback_failed_rc: int | None = None

    try:
        if args.handoff:
            # Scrub the URL before logging — on preview deploys the URL
            # carries the Vercel bypass secret as a query param and we
            # don't want it in the detached log file.
            logger.info("Fetching handoff bundle from %s", _scrub_url(args.handoff))
            try:
                handoff_bundle = _fetch_handoff(args.handoff)
            except Exception as exc:
                # `_fetch_handoff` already raises RuntimeError with a
                # scrubbed URL. Anything else (requests.ConnectionError,
                # requests.Timeout) gets a generic message so a surprise
                # exception type doesn't leak URL query strings through
                # its default __str__.
                print(
                    f"ERROR: fetching handoff bundle: {type(exc).__name__}: {_scrub_url(str(exc))}",
                    file=sys.stderr,
                )
                return 8
            handoff_tmpdir = Path(tempfile.mkdtemp(prefix="coarse-review-"))
            logger.info("Downloading paper from handoff signed URL to %s", handoff_tmpdir)
            try:
                temp_source = _download_handoff_source(handoff_bundle, handoff_tmpdir)
            except Exception as exc:
                print(
                    f"ERROR: downloading paper: {type(exc).__name__}: {_scrub_url(str(exc))}",
                    file=sys.stderr,
                )
                return 8
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

        _ensure_openrouter_key_loaded(
            args.pre_extracted.expanduser() if args.pre_extracted else None,
        )

        # Call the pipeline directly so we get the PaperText back in-process
        # (no sidecar file dance). run_headless_review handles all the
        # monkey-patching for the chosen host.
        from coarse.extraction_openrouter import signed_url_ctx
        from coarse.headless_review import run_headless_review

        logger.info(
            "Running coarse pipeline (host=%s, model=%s, effort=%s)",
            host,
            model,
            effort,
        )

        # Hand OpenRouter the signed Supabase URL directly when one is
        # available instead of base64-encoding the full PDF into the
        # request body. OpenRouter's inline base64 path has an
        # effective ~8-16 MB limit on the request body — a 20 MB paper
        # base64-encodes to ~27 MB of JSON and gets rejected with a
        # generic HTTP 400 well before Mistral OCR ever sees it. The
        # URL path bypasses that entirely (OpenRouter fetches the PDF
        # server-side) and scales to Mistral's real 50 MB / 1000-page
        # ceiling. The local download in ``_download_handoff_source``
        # still happens because ``extraction_qa.py`` needs the PDF on
        # disk for the vision LLM page-render check — we only skip
        # the base64 blob in the OpenRouter request, not the download.
        handoff_signed_url: str | None = None
        if handoff_bundle is not None:
            raw_signed_url = handoff_bundle.get("signed_download_url")
            if isinstance(raw_signed_url, str) and raw_signed_url.startswith("https://"):
                handoff_signed_url = raw_signed_url
        signed_url_token = signed_url_ctx.set(handoff_signed_url)
        try:
            review, md_text, paper_text = run_headless_review(
                paper_path,
                host=host,
                model=model,
                effort=effort,
                pre_extracted=args.pre_extracted.expanduser() if args.pre_extracted else None,
            )
        except Exception as exc:
            # Scrub the exception string before printing — if any upstream
            # helper ever interpolates a URL or token into its error, this
            # is the last line of defense before the detached log file.
            print(f"ERROR: pipeline failed — {_scrub_url(str(exc))}", file=sys.stderr)
            return 6
        finally:
            signed_url_ctx.reset(signed_url_token)

        # Save the review markdown locally regardless of mode. Explicit
        # utf-8 because review markdown contains non-ASCII content (math
        # symbols, em dashes, quoted paper excerpts) and Windows' default
        # `cp1252` encoding crashes on those. `PYTHONUTF8=1` in the
        # detached child also covers this, but the explicit encoding
        # makes the non-detached path safe too.
        review_md_path = out_dir / f"{paper_path.stem}_review_{model_filename_slug(model)}.md"
        review_md_path.write_text(md_text, encoding="utf-8")
        logger.info("Wrote %d-char review to %s", len(md_text), review_md_path)

        # Handoff mode: POST the review back to coarse web.
        if handoff_bundle is not None:
            # Log a scrubbed callback URL — the real one carries the
            # Vercel bypass secret query param on preview deploys.
            logger.info(
                "POSTing review back to %s",
                _scrub_url(handoff_bundle["callback_url"]),
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
                    callback_error=_scrub_url(str(exc)),
                )
                callback_failed_rc = 7
        else:
            _print_completion_footer(local_path=review_md_path)
    finally:
        # Single cleanup point for the handoff tempdir. Runs on every
        # exit path — fetch failure, download failure, pipeline
        # failure, finalize failure, happy path. Targets
        # ``handoff_tmpdir`` directly rather than ``temp_source.parent``
        # so test mocks that return a fixture path whose parent is the
        # test's own ``tmp_path`` (not the handoff tempdir) don't get
        # their fixture wiped out.
        if handoff_tmpdir is not None:
            import shutil

            shutil.rmtree(handoff_tmpdir, ignore_errors=True)

    return callback_failed_rc if callback_failed_rc is not None else 0


if __name__ == "__main__":
    sys.exit(main())
