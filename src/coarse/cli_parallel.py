"""Parallel review runner behind ``coarse review-parallel``.

Extract a paper once (with one optional PDF extraction-QA pass), then review
the resulting Markdown with several models at the same time. Every unit of
work runs in its own worker subprocess (``python -m coarse.cli_parallel
--_worker <spec.json> <fd>``) that streams JSON-lines progress events back
over a pipe. The parent renders one live table, rewrites ``summary.json``
while the run is active, and stops every worker process group on Ctrl-C or
SIGTERM while keeping whatever outputs already exist.

Run layout (``<output-dir>/<paper>-<UTC stamp>-<suffix>/``)::

    extracted.md        shared extraction (QA-corrected when QA ran)
    extraction.log      extraction worker stdout/stderr
    01-<model>.md       one review per --model, numbered in argument order
    01-<model>.log      that review worker's stdout/stderr
    *.job.json          worker specs (paths and options only; no credentials)
    summary.json        statuses, stages, elapsed time, reported costs
    run.log             parent traceback, only when the run itself failed

Reviews always run with ``skip_cost_gate=True``: the interactive cost gate
prompts on stdin, which N concurrent workers cannot share. Costs shown are
the amounts coarse reports per worker; OCR charges from a cold extraction
cache are not itemised.

This module holds no Typer code and must never import ``coarse.cli`` (the
``review-parallel`` command in ``cli.py`` imports this module). POSIX only:
worker cleanup relies on process groups (``os.killpg``).
"""

from __future__ import annotations

import json
import logging
import math
import os
import re
import selectors
import signal
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from coarse import __version__
from coarse.config import CoarseConfig, load_config, resolve_api_key
from coarse.extraction import SUPPORTED_EXTENSIONS

# Longest single JSON event a worker may send before the parent treats the
# stream as corrupt and discards the partial line.
MAX_EVENT_BYTES = 65536

# Garble ratio above which the pipeline auto-triggers extraction QA even when
# ``config.extraction_qa`` is off. Mirrors ``pipeline.review_paper``.
_GARBLE_QA_THRESHOLD = 0.001

COST_NOTE = "Reported amounts only; OCR and other unreported charges may be missing."


# ---------------------------------------------------------------------------
# Small helpers shared by parent and workers
# ---------------------------------------------------------------------------


def atomic_text(path: Path, text: str) -> None:
    """Write ``text`` to ``path`` via a sibling temp file and an atomic rename."""
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def slug(value: str) -> str:
    """Filesystem-safe fragment for run-directory and per-model file names."""
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip(".-_")[:90] or "review"


def clean_text(value: object) -> str:
    """Collapse ``value`` to printable, single-line text safe for the terminal."""
    return " ".join("".join(c for c in str(value) if c.isprintable() or c.isspace()).split())


def preflight(file: Path, models: list[str], config: CoarseConfig) -> None:
    """Validate the input format and API-key availability before any paid work.

    Raises ``ValueError`` with a user-facing message. Runs in the parent, before
    the run directory is created, so a bad invocation leaves nothing behind.
    """
    if file.suffix.lower() not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"Unsupported input format. Supported: {supported}")
    missing = [model for model in models if resolve_api_key(model, config) is None]
    if missing:
        raise ValueError(
            "No API key configured for: "
            + ", ".join(missing)
            + ". Use your environment, --env-file, or coarse setup."
        )


# ---------------------------------------------------------------------------
# Worker side (runs in ``python -m coarse.cli_parallel --_worker``)
# ---------------------------------------------------------------------------

Emit = Callable[[dict[str, Any]], None]


def extract_shared(spec: dict[str, Any], config: CoarseConfig, emit: Emit) -> dict[str, Any]:
    """Extract the paper once and, for PDFs, run extraction QA once.

    Mirrors the extraction + QA block of ``pipeline.review_paper``: QA runs when
    the config enables it or the text looks garbled, unless ``--no-qa`` was
    given, and the corrected text is saved back to the extraction cache beside
    the source document so later runs reuse it.
    """
    from coarse.extraction import extract_file

    path = Path(spec["file"])
    emit({"type": "stage", "stage": "Extracting paper text"})
    paper = extract_file(path)
    is_pdf = path.suffix.lower() == ".pdf"
    qa_status = "disabled" if is_pdf else "not applicable"
    qa_cost: float | None = None
    if is_pdf and not spec["no_qa"]:
        if config.extraction_qa or paper.garble_ratio > _GARBLE_QA_THRESHOLD:
            if resolve_api_key(config.vision_model, config) is None:
                qa_status = "skipped: no vision-model API key"
                emit({"type": "warning", "message": qa_status})
            else:
                from coarse.extraction_cache import _save_cache
                from coarse.extraction_qa import run_extraction_qa
                from coarse.llm import LLMClient

                emit({"type": "stage", "stage": "Checking PDF extraction"})
                client = LLMClient(model=config.vision_model, config=config)
                corrected = run_extraction_qa(path, paper, client)
                if corrected is not paper:
                    _save_cache(path, corrected)
                paper = corrected
                qa_cost = client.cost_usd
                qa_status = "completed"
    if not paper.full_markdown.strip():
        raise ValueError("Extraction produced no text")
    atomic_text(Path(spec["output"]), paper.full_markdown)
    return {
        "qa_status": qa_status,
        "reported_cost_usd": qa_cost,
        "token_estimate": paper.token_estimate,
    }


def review_shared(spec: dict[str, Any], config: CoarseConfig, emit: Emit) -> dict[str, Any]:
    """Run one full review of the shared Markdown with ``spec["model"]``."""
    from coarse.pipeline import review_paper

    def progress(update: Any) -> None:
        emit(
            {
                "type": "progress",
                "event": update.event,
                "stage_key": update.stage_key,
                "stage": update.stage_label,
                "completed": update.completed_stages,
                "total": update.total_stages,
                "reported_cost_usd": update.actual_cost_usd,
            }
        )

    _, markdown, _ = review_paper(
        pdf_path=Path(spec["input"]),
        model=spec["model"],
        skip_cost_gate=True,
        config=config,
        language=spec.get("language"),
        progress_callback=progress,
    )
    if not markdown.strip():
        raise ValueError("Review produced no Markdown")
    atomic_text(Path(spec["output"]), markdown)
    return {}


def worker(spec_path: str, event_fd: int) -> int:
    """Worker entry: run the job described by ``spec_path``, stream events to ``event_fd``."""
    # Coarse's internal threads can report concurrently. Keep JSON records intact.
    os.set_inheritable(event_fd, False)
    lock = threading.Lock()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    with os.fdopen(event_fd, "w", encoding="utf-8", buffering=1) as stream:

        def emit(event: dict[str, Any]) -> None:
            with lock:
                stream.write(json.dumps(event, ensure_ascii=True) + "\n")

        try:
            spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
            config = load_config()
            if spec["kind"] == "extract":
                result = extract_shared(spec, config, emit)
            elif spec["kind"] == "review":
                result = review_shared(spec, config, emit)
            else:
                raise ValueError(f"Unknown job kind: {spec['kind']!r}")
            emit({"type": "result", "details": result})
            return 0
        except Exception as exc:
            traceback.print_exc()
            emit({"type": "error", "message": f"{type(exc).__name__}: {exc}"})
            return 1


def worker_main(argv: list[str]) -> int:
    """``python -m coarse.cli_parallel`` entry. Only the hidden worker form is valid."""
    if len(argv) == 3 and argv[0] == "--_worker":
        return worker(argv[1], int(argv[2]))
    print(
        "usage: coarse review-parallel PAPER --model MODEL [--model MODEL ...]\n"
        "(python -m coarse.cli_parallel is the internal worker entry point)",
        file=sys.stderr,
    )
    return 2


# ---------------------------------------------------------------------------
# Parent side: jobs, display, event loop
# ---------------------------------------------------------------------------


@dataclass
class Job:
    label: str
    spec: dict[str, Any]
    log: Path
    status: str = "waiting"
    stage: str = "Waiting"
    completed: int | None = None
    total: int | None = None
    cost: float | None = None
    started: float | None = None
    ended: float | None = None
    returncode: int | None = None
    details: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    process: subprocess.Popen | None = field(default=None, repr=False)
    fd: int | None = field(default=None, repr=False)
    buffer: bytes = field(default=b"", repr=False)
    discard_line: bool = field(default=False, repr=False)
    received_result: bool = False

    def elapsed(self) -> float:
        return 0 if self.started is None else (self.ended or time.monotonic()) - self.started

    def record(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "model": self.spec.get("model"),
            "status": self.status,
            "stage": self.stage,
            "elapsed_seconds": round(self.elapsed(), 2),
            "completed_stages": self.completed,
            "total_stages": self.total,
            "reported_cost_usd": self.cost,
            "exit_code": self.returncode,
            "output": self.spec.get("output"),
            "log": str(self.log),
            "warnings": self.warnings,
            "details": self.details,
        }


class Display:
    """One live table for every job, or plain prefixed lines when not a terminal.

    Owns its own ``Console`` on purpose: ``cli.py`` keeps a module-level console
    for the single-review progress bar, and rich allows one ``Live`` per console.
    """

    def __init__(self, jobs: list[Job]):
        from rich.console import Console
        from rich.live import Live

        self.console = Console(force_terminal=sys.stdout.isatty(), markup=False, highlight=False)
        self.jobs = jobs
        self.live = (
            Live(self.table(), console=self.console, auto_refresh=False, transient=True)
            if self.console.is_terminal and not self.console.is_dumb_terminal
            else None
        )

    def table(self) -> Any:
        from rich.table import Table
        from rich.text import Text

        table = Table(
            title="coarse parallel reviews",
            caption=(
                "Stage totals are estimates. Costs are reported amounts; "
                "OCR charges may be missing."
            ),
        )
        for name in ("Model / task", "Status / stage", "Stages (est.)", "Elapsed", "Reported USD"):
            table.add_column(name, overflow="fold")
        for job in self.jobs:
            count = f"{job.completed}/{job.total}" if job.total else "—"
            seconds = int(job.elapsed())
            elapsed = f"{seconds // 60}:{seconds % 60:02d}" if job.started else "—"
            table.add_row(
                Text(clean_text(job.label)),
                Text(clean_text(job.stage)),
                count,
                elapsed,
                f"${job.cost:.4f}" if job.cost is not None else "—",
            )
        return table

    def __enter__(self) -> Display:
        if self.live:
            self.live.start()
        return self

    def __exit__(self, *exc: Any) -> None:
        if self.live:
            self.live.stop()

    def refresh(self) -> None:
        if self.live:
            self.live.update(self.table(), refresh=True)

    def transition(self, job: Job, message: str) -> None:
        if not self.live:
            self.console.print(f"[{clean_text(job.label)}] {clean_text(message)}")


def receive_event(job: Job, data: bytes, display: Display) -> None:
    """Apply one JSON event from a worker to its job; never trust its shape."""
    try:
        event = json.loads(data)
        kind = event["type"]
        if kind in ("stage", "progress"):
            stage = event["stage"]
            if not isinstance(stage, str):
                raise ValueError("stage must be text")
            if kind == "progress":
                completed = event["completed"]
                total = event["total"]
                cost = event["reported_cost_usd"]
                if (
                    type(completed) is not int
                    or type(total) is not int
                    or completed < 0
                    or total < 0
                    or not isinstance(cost, (int, float))
                    or not math.isfinite(cost)
                    or cost < 0
                ):
                    raise ValueError("invalid progress values")
                job.completed, job.total, job.cost = completed, total, cost
            if stage != job.stage:
                job.stage = stage
                display.transition(job, stage)
        elif kind == "result":
            if not isinstance(event["details"], dict):
                raise ValueError("result must contain details")
            job.details.update(event["details"])
            job.received_result = True
            if event["details"].get("reported_cost_usd") is not None:
                job.cost = float(event["details"]["reported_cost_usd"])
        elif kind == "error":
            job.details["error"] = clean_text(event["message"])
        elif kind == "warning":
            message = clean_text(event["message"])
            job.warnings.append(message)
            display.transition(job, message)
        else:
            raise ValueError("unknown event type")
    except (ValueError, KeyError, TypeError, OverflowError):
        message = "Ignored malformed worker progress event; see log."
        if message not in job.warnings:
            job.warnings.append(message)
            display.transition(job, message)
        with job.log.open("a", encoding="utf-8") as log:
            log.write("\nIgnored worker event: " + repr(data[:1000]) + "\n")


def drain(job: Job, display: Display) -> bool:
    """Read one available chunk. Return False on EOF; bound corrupt record sizes."""
    try:
        chunk = os.read(job.fd, 16384)
    except BlockingIOError:
        return True
    if not chunk:
        if job.buffer:
            receive_event(job, job.buffer, display)
            job.buffer = b""
        return False
    job.buffer += chunk
    while b"\n" in job.buffer:
        line, job.buffer = job.buffer.split(b"\n", 1)
        if not job.discard_line:
            receive_event(job, line, display)
        job.discard_line = False
    if len(job.buffer) > MAX_EVENT_BYTES:
        job.buffer = b""
        job.discard_line = True
        receive_event(job, b"oversized event", display)
    return True


def stop_processes(jobs: list[Job]) -> None:
    """Terminate, then kill, every job's whole process group."""
    # Workers have their own process groups, including any subprocesses they start.
    processes = [job.process for job in jobs if job.process is not None]

    def signal_group(process: subprocess.Popen, signum: int) -> None:
        try:
            os.killpg(process.pid, signum)
        except ProcessLookupError:
            pass
        except PermissionError:
            # Some macOS environments report EPERM, not ESRCH, for a group
            # which has already disappeared. Never hide a live-worker denial.
            if process.poll() is None:
                raise

    for process in processes:
        signal_group(process, signal.SIGTERM)
    deadline = time.monotonic() + 2
    for process in processes:
        try:
            process.wait(timeout=max(0, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            pass
    # Kill remaining descendants even if their group leader has already exited.
    for process in processes:
        signal_group(process, signal.SIGKILL)
        process.wait()


def _worker_command(spec_path: Path, write_fd: int) -> list[str]:
    return [
        sys.executable,
        "-u",
        "-m",
        "coarse.cli_parallel",
        "--_worker",
        str(spec_path),
        str(write_fd),
    ]


def run_jobs(jobs: list[Job], display: Display, save_summary: Callable[[], None]) -> None:
    """Start every job as a worker subprocess and pump events until all exit."""
    with selectors.DefaultSelector() as selector:
        try:
            for job in jobs:
                spec_path = job.log.with_suffix(".job.json")
                atomic_text(spec_path, json.dumps(job.spec, indent=2) + "\n")
                read_fd, write_fd = os.pipe()
                job.fd = read_fd
                try:
                    with job.log.open("a", encoding="utf-8") as log:
                        job.process = subprocess.Popen(
                            _worker_command(spec_path, write_fd),
                            stdin=subprocess.DEVNULL,
                            stdout=log,
                            stderr=subprocess.STDOUT,
                            pass_fds=(write_fd,),
                            start_new_session=True,
                            env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
                        )
                finally:
                    os.close(write_fd)
                os.set_blocking(read_fd, False)
                selector.register(read_fd, selectors.EVENT_READ, job)
                job.started = time.monotonic()
                job.status, job.stage = "running", "Starting"
                display.transition(job, job.stage)
            last_save = 0.0
            while any(job.status == "running" for job in jobs):
                for key, _ in selector.select(timeout=0.2):
                    if not drain(key.data, display):
                        selector.unregister(key.fd)
                for job in jobs:
                    if job.status != "running" or job.process.poll() is None:
                        continue
                    # A worker can exit before its final pipe records are consumed.
                    while job.fd in selector.get_map():
                        if not drain(job, display):
                            selector.unregister(job.fd)
                    job.returncode = job.process.returncode
                    job.ended = time.monotonic()
                    output = job.spec.get("output")
                    success = (
                        job.returncode == 0
                        and job.received_result
                        and "error" not in job.details
                        and (not output or Path(output).is_file())
                    )
                    job.status = "succeeded" if success else "failed"
                    job.stage = "Done" if success else "Failed"
                    if not success:
                        job.details.setdefault(
                            "error",
                            f"Worker exited with code {job.returncode} without a complete result",
                        )
                    # Clean up this group now, not after other models finish:
                    # retaining a reaped PID for a long run risks PID reuse.
                    stop_processes([job])
                    job.process = None
                    display.transition(job, job.stage)
                display.refresh()
                if time.monotonic() - last_save >= 1:
                    save_summary()
                    last_save = time.monotonic()
        finally:
            # Ignore further interrupts only while performing bounded cleanup.
            previous = {
                sig: signal.signal(sig, signal.SIG_IGN) for sig in (signal.SIGINT, signal.SIGTERM)
            }
            try:
                stop_processes(jobs)
                for job in jobs:
                    if job.fd is not None:
                        os.close(job.fd)
                        job.fd = None
                    if job.status == "running":
                        job.status, job.stage = "cancelled", "Cancelled"
                        job.ended = time.monotonic()
                        job.returncode = job.process.returncode
            finally:
                for sig, handler in previous.items():
                    signal.signal(sig, handler)
            save_summary()


# ---------------------------------------------------------------------------
# Parent entry point (called by ``coarse review-parallel``)
# ---------------------------------------------------------------------------


def run_parallel(
    file: Path,
    models: list[str],
    output_dir: Path,
    *,
    language: str | None = None,
    no_qa: bool = False,
) -> int:
    """Extract once, then review with every model in parallel. Returns the exit code.

    ``file`` and ``output_dir`` should already be resolved absolute paths and
    ``preflight()`` should already have passed. Exit codes: 0 when every review
    succeeded, 1 when any job failed or the run itself errored, 130 when
    interrupted (Ctrl-C or SIGTERM). ``KeyboardInterrupt`` never escapes.
    """

    def interrupted(signum: int, frame: Any) -> None:
        raise KeyboardInterrupt

    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    directory = Path(tempfile.mkdtemp(prefix=f"{slug(file.stem)}-{stamp}-", dir=output_dir))
    common = {"file": str(file), "no_qa": no_qa, "language": language}
    extraction = Job(
        "Shared extraction / QA",
        {**common, "kind": "extract", "output": str(directory / "extracted.md")},
        directory / "extraction.log",
    )
    reviews: list[Job] = []
    for index, model in enumerate(models, 1):
        name = f"{index:02d}-{slug(model)}"
        reviews.append(
            Job(
                f"{index:02d} {model}",
                {
                    **common,
                    "kind": "review",
                    "model": model,
                    "input": extraction.spec["output"],
                    "output": str(directory / f"{name}.md"),
                },
                directory / f"{name}.log",
            )
        )
    jobs = [extraction, *reviews]
    summary: dict[str, Any] = {
        "input": str(file),
        "created_at": stamp,
        "coarse_version": __version__,
        "cost_note": COST_NOTE,
    }

    def save_summary() -> None:
        payload = {
            **summary,
            "extraction": extraction.record(),
            "reviews": [job.record() for job in reviews],
        }
        atomic_text(directory / "summary.json", json.dumps(payload, indent=2) + "\n")

    display = Display(jobs)
    display.console.print(f"Run directory: {directory}")
    code = 1
    save_summary()
    # SIGTERM should clean up reviews just like Ctrl-C; workers keep the default.
    previous_sigterm = signal.signal(signal.SIGTERM, interrupted)
    try:
        with display:
            run_jobs([extraction], display, save_summary)
            if extraction.status == "succeeded":
                run_jobs(reviews, display, save_summary)
                code = 0 if all(job.status == "succeeded" for job in reviews) else 1
    except KeyboardInterrupt:
        code = 130
        display.console.print("Interrupted; stopped workers and kept existing outputs.")
    except Exception as exc:
        summary["error"] = f"{type(exc).__name__}: {exc}"
        (directory / "run.log").write_text(traceback.format_exc(), encoding="utf-8")
        display.console.print(f"Run failed: {clean_text(exc)}")
        display.console.print(f"  Log: {directory / 'run.log'}")
    finally:
        signal.signal(signal.SIGTERM, previous_sigterm)
        for job in jobs:
            if job.status == "waiting":
                job.status, job.stage = "skipped", "Skipped"
        summary["exit_code"] = code
        save_summary()
    if display.live:
        display.console.print(display.table())
    for job in jobs:
        if job.status == "failed":
            display.console.print(f"[{clean_text(job.label)}] {job.details.get('error', 'Failed')}")
            display.console.print(f"  Log: {job.log}")
        elif job.spec["kind"] == "review":
            target = job.spec["output"] if job.status == "succeeded" else str(job.log)
            display.console.print(f"[{clean_text(job.label)}] {job.status}: {target}")
        for warning in job.warnings:
            display.console.print(f"[{clean_text(job.label)}] {warning}")
    display.console.print(f"Summary: {directory / 'summary.json'}")
    return code


if __name__ == "__main__":
    sys.exit(worker_main(sys.argv[1:]))
