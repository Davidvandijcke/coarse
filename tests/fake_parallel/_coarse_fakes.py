"""Fake paid-boundary implementations for ``coarse review-parallel`` tests.

Installed by the sibling ``sitecustomize.py`` into every Python process
(parent CLI and ``-m coarse.cli_parallel`` workers) that starts with this
directory on ``PYTHONPATH`` and ``COARSE_FAKE_TRACE`` set. Nothing here is
imported by production code.

Every observable action appends one line to the trace file so tests can
assert *how many times* extraction, QA, and reviews ran, and with what:

    extract:<path>      extract_file called
    cache:<path>        _save_cache called (QA corrected the text)
    qa:<path>           run_extraction_qa called
    review:<json>       review_paper called (model, text, language, key)
    child:<pid>         fake/hang spawned a grandchild that ignores SIGTERM
    done:<model>        review_paper returned

Behaviour knobs (all environment variables):

    COARSE_FAKE_QA              "0" turns config.extraction_qa off (default on)
    COARSE_FAKE_GARBLE          garble_ratio reported by extract_file (default 0)
    COARSE_FAKE_EXTRACTION_FAIL any value makes extract_file raise
    COARSE_FAKE_MISSING_KEY     model whose resolve_api_key returns None
    COARSE_FAKE_KEY             value resolve_api_key returns (default fake-key)
    COARSE_FAKE_BARRIER         N: every review waits until N reviews started

Special model IDs: ``fake/fail`` raises after reporting progress,
``fake/hang`` spawns a stubborn grandchild and sleeps, ``fake/malformed``
writes garbage straight to the worker's event pipe.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import types
from pathlib import Path
from typing import Any


def trace(message: str) -> None:
    with Path(os.environ["COARSE_FAKE_TRACE"]).open("a", encoding="utf-8") as handle:
        handle.write(message + "\n")


# --- coarse.config -----------------------------------------------------------


def load_config() -> Any:
    from coarse.config import CoarseConfig

    return CoarseConfig(
        vision_model="fake/vision",
        extraction_qa=os.getenv("COARSE_FAKE_QA", "1") == "1",
    )


def resolve_api_key(model: str, config: Any = None) -> str | None:
    if os.getenv("COARSE_FAKE_MISSING_KEY") == model:
        return None
    return os.getenv("COARSE_FAKE_KEY", "fake-key")


# --- coarse.extraction / coarse.extraction_cache -----------------------------


def extract_file(path: Path, use_cache: bool = True) -> Any:
    from coarse.types import PaperText

    trace("extract:" + str(path))
    if os.getenv("COARSE_FAKE_EXTRACTION_FAIL"):
        raise RuntimeError("extraction failed deliberately")
    return PaperText(
        full_markdown="# Shared paper\nOriginal text.\n",
        token_estimate=10,
        garble_ratio=float(os.getenv("COARSE_FAKE_GARBLE", "0")),
    )


def _save_cache(path: Path, paper: Any) -> None:
    trace("cache:" + str(path))


# --- coarse.extraction_qa ------------------------------------------------------


def run_extraction_qa(path: Path, paper: Any, client: Any) -> Any:
    from coarse.types import PaperText

    trace("qa:" + str(path))
    client.cost_usd = 0.25
    return PaperText(
        full_markdown=paper.full_markdown.replace("Original", "Corrected"),
        token_estimate=10,
        garble_ratio=0.0,
    )


# --- coarse.llm ------------------------------------------------------------------


class LLMClient:
    def __init__(self, model: str, config: Any = None, **kwargs: Any) -> None:
        self.model = model
        self.cost_usd = 0.0


# --- coarse.pipeline -------------------------------------------------------------


def review_paper(
    pdf_path: Path,
    model: str,
    skip_cost_gate: bool,
    config: Any,
    language: str | None,
    progress_callback: Any,
) -> tuple[None, str, None]:
    assert skip_cost_gate, "parallel reviews must skip the interactive cost gate"
    assert Path(pdf_path).suffix == ".md", "reviews must read the shared extraction"
    text = Path(pdf_path).read_text(encoding="utf-8")
    trace(
        "review:"
        + json.dumps(
            {
                "model": model,
                "text": text,
                "time": time.monotonic(),
                "language": language,
                "key": os.getenv("COARSE_FAKE_KEY"),
            }
        )
    )
    print("log-only output for " + model, flush=True)
    if model == "fake/hang":
        child = subprocess.Popen(
            [
                sys.executable,
                "-c",
                "import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); "
                "time.sleep(120)",
            ]
        )
        trace("child:" + str(child.pid))
        time.sleep(120)
    if model == "fake/malformed":
        fd = int(sys.argv[-1])
        os.write(fd, b"not-json\n" + b"x" * 100000 + b"\n")
    update = types.SimpleNamespace(
        event="started",
        stage_key="structure",
        stage_label="Analyzing structure",
        completed_stages=0,
        total_stages=3,
        actual_cost_usd=0.0,
    )
    progress_callback(update)
    time.sleep(0.15)
    if model == "fake/fail":
        raise RuntimeError("review failed deliberately")
    if os.getenv("COARSE_FAKE_BARRIER"):
        # Every review must have started before any can finish.
        deadline = time.monotonic() + 4
        while True:
            events = Path(os.environ["COARSE_FAKE_TRACE"]).read_text(encoding="utf-8")
            started = sum(line.startswith("review:") for line in events.splitlines())
            if started >= int(os.environ["COARSE_FAKE_BARRIER"]):
                break
            if time.monotonic() > deadline:
                raise RuntimeError("parallel review barrier timed out")
            time.sleep(0.03)
    update.event = "completed"
    update.stage_label = "Review complete"
    update.completed_stages = 3
    update.actual_cost_usd = 1.25
    progress_callback(update)
    trace("done:" + model)
    return None, "# Review by " + model + "\n\n" + text, None


def extract_and_structure(*args: Any, **kwargs: Any) -> Any:
    raise NotImplementedError("fake coarse.pipeline: extract_and_structure is not used here")


def _fake_module(name: str, **attrs: Any) -> types.ModuleType:
    module = types.ModuleType(name, f"Fake {name} installed by tests/fake_parallel.")

    def __getattr__(attr: str) -> Any:
        raise AttributeError(
            f"fake module {name!r} (tests/fake_parallel) has no attribute {attr!r}"
        )

    module.__getattr__ = __getattr__  # type: ignore[attr-defined]
    for key, value in attrs.items():
        setattr(module, key, value)
    return module


def install() -> None:
    """Seed fake heavy modules, then attribute-patch the light real ones."""
    fakes = {
        "coarse.pipeline": _fake_module(
            "coarse.pipeline",
            review_paper=review_paper,
            extract_and_structure=extract_and_structure,
        ),
        "coarse.llm": _fake_module("coarse.llm", LLMClient=LLMClient),
        "coarse.extraction_qa": _fake_module(
            "coarse.extraction_qa", run_extraction_qa=run_extraction_qa
        ),
    }
    sys.modules.update(fakes)

    import coarse  # runs coarse/__init__.py against the fake pipeline
    import coarse.config
    import coarse.extraction
    import coarse.extraction_cache

    for name, module in fakes.items():
        setattr(coarse, name.rsplit(".", 1)[1], module)
    coarse.config.load_config = load_config
    coarse.config.resolve_api_key = resolve_api_key
    coarse.extraction.extract_file = extract_file
    coarse.extraction._save_cache = _save_cache
    coarse.extraction_cache._save_cache = _save_cache
