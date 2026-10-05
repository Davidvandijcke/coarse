"""Checkpointed, app-native execution of the existing review pipeline."""

from __future__ import annotations

import datetime
import json
import re
import shlex
import shutil
import sys
import tempfile
from importlib.metadata import distribution
from pathlib import Path

from coarse import __version__
from coarse.cli_review import (
    _download_handoff_source,
    _ensure_openrouter_key_loaded,
    _fetch_handoff,
    _post_finalize,
)
from coarse.config import CoarseConfig
from coarse.extraction import extract_file
from coarse.headless_review import openrouter_key_preflight_error
from coarse.native_runtime import NativeInvalid, NativePending, NativeRuntime
from coarse.native_store import (
    FORMAT_VERSION,
    atomic_json,
    atomic_text,
    engine_digest,
    file_digest,
    load_run,
    read_json,
    workspace_lock,
)
from coarse.pipeline import review_paper
from coarse.types import Review


def prepare(
    workspace: Path,
    *,
    paper: Path | None = None,
    handoff: str | None = None,
    host: str,
    model: str = "inherit",
    effort: str = "inherit",
    pre_extracted: Path | None = None,
    language: str | None = None,
) -> dict:
    if bool(paper) == bool(handoff):
        raise ValueError("Supply exactly one paper file or handoff URL")
    if host not in ("codex", "claude"):
        raise ValueError("The native pilot supports Codex and Claude Code")
    if workspace.exists():
        raise ValueError("Workspace already exists; use next to resume or choose a new directory")
    workspace.parent.mkdir(parents=True, exist_ok=True)
    workspace.mkdir(mode=0o700)
    try:
        for name in ["tasks", "results"]:
            (workspace / name).mkdir(mode=0o700)
        atomic_text(workspace / ".gitignore", "*\n")
        with tempfile.TemporaryDirectory(prefix="coarse-native-") as tmp:
            bundle = _fetch_handoff(handoff) if handoff else None
            source = _download_handoff_source(bundle, Path(tmp)) if bundle else paper
            assert source is not None
            _ensure_openrouter_key_loaded(pre_extracted)
            error = openrouter_key_preflight_error(source, pre_extracted)
            if error:
                raise ValueError(error)
            source_copy = workspace / ("source" + source.suffix.lower())
            shutil.copyfile(source, source_copy)
            source_copy.chmod(0o600)
            extracted = extract_file(pre_extracted or source_copy, use_cache=False)
            if not extracted.full_markdown.strip():
                raise ValueError("The prepared paper is empty")
            atomic_text(workspace / "paper.md", extracted.full_markdown)
            if bundle:
                atomic_json(workspace / "handoff.json", bundle)
            run = {
                "runner_prefix": _runner_prefix(),
                "format_version": FORMAT_VERSION,
                "coarse_version": __version__,
                "engine_digest": engine_digest(),
                "paper_digest": file_digest(workspace / "paper.md"),
                "source_digest": file_digest(source_copy),
                "source_file": source_copy.name,
                "host": host,
                "model": model,
                "effort": effort,
                "language": language,
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "status": "prepared",
                "pending": [],
                "completed": [],
                "publication": "not_requested",
                "has_handoff": bool(bundle),
                "subscription_usage": None,
                "pdf_visual_qa": "requires_host_check"
                if source.suffix.lower() == ".pdf"
                else "n/a",
            }
            atomic_json(workspace / "run.json", run)
        return advance(workspace)
    except BaseException:
        # Never leave a failed preparation masquerading as a resumable run.
        if not (workspace / "run.json").exists():
            shutil.rmtree(workspace)
        raise


def _replay(workspace: Path, run: dict) -> NativeRuntime:
    runtime = NativeRuntime(workspace, run)
    try:
        review, markdown, _paper = review_paper(
            workspace / "paper.md",
            model="native-" + run["host"],
            skip_cost_gate=True,
            config=CoarseConfig(extraction_qa=False, api_keys={}),
            language=run["language"],
            runtime=runtime,
        )
    except NativePending:
        run["status"] = "waiting"
    except NativeInvalid as exc:
        raise ValueError(str(exc)) from exc
    else:
        if runtime.pending:
            raise ValueError("Review cannot complete with unanswered tasks")
        atomic_json(workspace / "review.json", review.model_dump(mode="json"))
        atomic_text(workspace / "review.md", markdown)
        run["status"] = "ready"
        run["review_digest"] = file_digest(workspace / "review.json")
        run["markdown_digest"] = file_digest(workspace / "review.md")
    run["pending"] = sorted(runtime.pending)
    run["completed"] = sorted(runtime.seen - runtime.pending)
    atomic_json(workspace / "run.json", run)
    return runtime


def summary(workspace: Path, run: dict) -> dict:
    return {
        "workspace": str(workspace),
        "runner_prefix": run["runner_prefix"],
        "status": run["status"],
        "host": run["host"],
        "model": run["model"],
        "effort": run["effort"],
        "tasks": [
            {"task_id": task, "file": str(workspace / "tasks" / f"{task}.json")}
            for task in run["pending"]
        ],
        "completed_tasks": len(run["completed"]),
        "publication": run["publication"],
        "pdf_visual_qa": run["pdf_visual_qa"],
        "review_file": str(workspace / "review.md") if run["status"] == "ready" else None,
        "review_url": run.get("review_url"),
        "subscription_usage": None,
    }


def status(workspace: Path) -> dict:
    with workspace_lock(workspace):
        return summary(workspace, load_run(workspace))


def advance(workspace: Path) -> dict:
    with workspace_lock(workspace):
        run = load_run(workspace)
        if run["publication"] != "not_requested":
            return summary(workspace, run)
        _replay(workspace, run)
        return summary(workspace, run)


def submit(
    workspace: Path,
    task_id: str,
    response: dict,
    *,
    agent_id: str,
    reported_model: str | None = None,
    reported_effort: str | None = None,
) -> dict:
    if not re.fullmatch(r"[0-9a-f]{24}", task_id):
        raise ValueError("Invalid task ID")
    if not agent_id.strip():
        raise ValueError("Record the native agent ID for this response")
    with workspace_lock(workspace):
        run = load_run(workspace)
        if run["publication"] != "not_requested":
            raise ValueError("A published or uncertain run cannot accept new responses")
        runtime = _replay(workspace, run)
        if task_id not in runtime.models:
            raise ValueError("Task is not part of the current review checkpoint")
        if run["model"] != "inherit" and reported_model != run["model"]:
            raise ValueError("Reported agent model must match the requested model")
        if run["effort"] != "inherit" and reported_effort != run["effort"]:
            raise ValueError("Reported agent effort must match the requested effort")
        value = runtime.models[task_id].model_validate(response).model_dump(mode="json")
        task = read_json(workspace / "tasks" / f"{task_id}.json")
        path = workspace / "results" / f"{task_id}.json"
        if path.exists():
            if read_json(path)["result"] != value:
                raise ValueError("Accepted responses are immutable; start a new run to revise")
        else:
            atomic_json(
                path,
                {
                    "request_digest": task["request_digest"],
                    "result": value,
                    "receipt": {
                        "agent_id": agent_id,
                        "reported_model": reported_model,
                        "reported_effort": reported_effort,
                        "verification": "host-reported",
                    },
                },
            )
        return {"accepted": task_id, "next": "Run next after submitting this batch"}


def publish(workspace: Path) -> dict:
    with workspace_lock(workspace):
        run = load_run(workspace)
        if run["publication"] == "published":
            return summary(workspace, run)
        if run["publication"] != "not_requested":
            raise ValueError("Publication outcome is uncertain; verify the website before retrying")
        _replay(workspace, run)
        if run["status"] != "ready":
            raise ValueError("Finish every required task before publishing")
        if run["pdf_visual_qa"] == "requires_host_check":
            raise ValueError("Confirm PDF extraction with confirm-extraction before publishing")
        if not run["has_handoff"]:
            raise ValueError("This local review has no website handoff; use the local artifacts")
        review = Review.model_validate(read_json(workspace / "review.json"))
        bundle = read_json(workspace / "handoff.json")
        run["publication"] = "uncertain"
        atomic_json(workspace / "run.json", run)
        # Write uncertain before sending. A lost HTTP response must not trigger
        # a blind second publication or be reported as a confirmed failure.
        result = _post_finalize(
            callback_url=bundle["callback_url"],
            finalize_token=bundle["finalize_token"],
            paper_id=bundle["paper_id"],
            paper_title=review.title,
            domain=review.domain,
            taxonomy=review.taxonomy,
            markdown=(workspace / "review.md").read_text(),
            paper_markdown=(workspace / "paper.md").read_text(),
            host_label="native-pilot:" + run["host"],
            language=review.language.model_dump() if review.language else None,
        )
        if not result.get("review_url"):
            raise ValueError("Server did not confirm a review URL; inspect the website")
        run["publication"] = "published"
        run["review_url"] = result["review_url"]
        atomic_json(workspace / "run.json", run)
        return summary(workspace, run)


def _runner_prefix() -> str:
    metadata = distribution("coarse-ink").read_text("direct_url.json")
    direct = json.loads(metadata) if metadata else {}
    commit = direct.get("vcs_info", {}).get("commit_id", "")
    if direct.get("url") == "https://github.com/Davidvandijcke/coarse" and re.fullmatch(
        r"[0-9a-f]{40}", commit
    ):
        return shlex.join(
            [
                "uvx",
                "--python",
                "3.12",
                "--from",
                "coarse-ink @ git+https://github.com/Davidvandijcke/coarse@" + commit,
                "coarse-native",
            ]
        )
    return shlex.join([sys.executable, "-m", "coarse.native_cli"])


def confirm_extraction(workspace: Path, *, agent_id: str, notes: str) -> dict:
    if not agent_id.strip() or not notes.strip():
        raise ValueError("Record the native agent ID and extraction inspection notes")
    with workspace_lock(workspace):
        run = load_run(workspace)
        if run["pdf_visual_qa"] == "n/a":
            raise ValueError("This source is not a PDF")
        if run["publication"] != "not_requested":
            raise ValueError("Publication has already been attempted")
        run["pdf_visual_qa"] = "host_checked"
        run["extraction_receipt"] = {
            "agent_id": agent_id,
            "notes": notes,
            "verification": "host-reported",
        }
        atomic_json(workspace / "run.json", run)
        return summary(workspace, run)
