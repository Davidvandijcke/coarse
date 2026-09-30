"""Tests for cli_parallel.py — the ``coarse review-parallel`` runner.

Subprocess tests run the real parent command and real worker processes; the
paid boundary (extraction, QA, LLM client, review pipeline, API keys) is
replaced by ``tests/fake_parallel`` via a ``sitecustomize`` hook on
``PYTHONPATH``. No provider calls happen.
"""

from __future__ import annotations

import json
import os
import pty
import re
import select
import signal
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

import coarse
from coarse import cli_parallel
from coarse.config import CoarseConfig

REPO_ROOT = Path(__file__).resolve().parents[1]
FAKE_SITE = REPO_ROOT / "tests" / "fake_parallel"
_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")


def _plain(text: str) -> str:
    """Strip ANSI sequences: Typer forces colour under GITHUB_ACTIONS/FORCE_COLOR."""
    return _ANSI_RE.sub("", text)


# ---------------------------------------------------------------------------
# Subprocess harness
# ---------------------------------------------------------------------------


class Harness:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.paper = root / "paper with spaces.pdf"
        self.paper.write_text("fake PDF handled only by the test fakes", encoding="utf-8")
        self.trace = root / "trace.txt"
        self.outputs = root / "outputs"
        self.summary_path: Path | None = None
        # Drop inherited fake knobs and forced-color settings so assertions on
        # plain redirected output hold regardless of the developer shell.
        env = {
            k: v
            for k, v in os.environ.items()
            if not k.startswith("COARSE_FAKE_") and k not in ("FORCE_COLOR", "CLICOLOR_FORCE")
        }
        existing = env.get("PYTHONPATH")
        env["PYTHONPATH"] = str(FAKE_SITE) + (os.pathsep + existing if existing else "")
        env["COARSE_FAKE_TRACE"] = str(self.trace)
        env["TERM"] = "xterm-256color"
        self.env = env

    def command(self, models=("fake/one", "fake/two"), extra=()) -> list[str]:
        return [
            sys.executable,
            "-m",
            "coarse",
            "review-parallel",
            str(self.paper),
            "--output-dir",
            str(self.outputs),
            "--yes",
            *[arg for model in models for arg in ("--model", model)],
            *extra,
        ]

    def run(self, models=("fake/one", "fake/two"), extra=(), env=None):
        result = subprocess.run(
            self.command(models, extra),
            env={**self.env, **(env or {})},
            capture_output=True,
            text=True,
            timeout=30,
        )
        summaries = sorted(self.outputs.glob("*/summary.json"))
        assert summaries, result.stdout + result.stderr
        self.summary_path = summaries[-1]
        return result, json.loads(self.summary_path.read_text(encoding="utf-8"))

    def events(self, prefix: str) -> list[str]:
        if not self.trace.exists():
            return []
        lines = self.trace.read_text(encoding="utf-8").splitlines()
        return [line[len(prefix) :] for line in lines if line.startswith(prefix)]


@pytest.fixture()
def harness(tmp_path: Path) -> Harness:
    return Harness(tmp_path)


# ---------------------------------------------------------------------------
# End-to-end behaviour (parent + workers as real processes)
# ---------------------------------------------------------------------------


def test_shared_extraction_qa_parallelism_and_outputs(harness: Harness) -> None:
    result, summary = harness.run(env={"COARSE_FAKE_BARRIER": "2"})
    assert result.returncode == 0, result.stdout + result.stderr
    # Extraction and QA happen exactly once; both reviews see the corrected text.
    assert len(harness.events("extract:")) == 1
    assert len(harness.events("qa:")) == 1
    assert len(harness.events("cache:")) == 1
    reviews = [json.loads(line) for line in harness.events("review:")]
    assert len(reviews) == 2
    assert reviews[0]["text"] == reviews[1]["text"]
    assert "Corrected text" in reviews[0]["text"]
    assert summary["coarse_version"] == coarse.__version__
    assert summary["extraction"]["reported_cost_usd"] == 0.25
    assert summary["extraction"]["details"]["qa_status"] == "completed"
    assert summary["exit_code"] == 0
    assert "setup" not in summary and "source" not in summary
    # Redirected stdout stays plain; worker chatter goes to logs only.
    assert "\x1b" not in result.stdout
    assert "log-only" not in result.stdout
    for review in summary["reviews"]:
        assert review["status"] == "succeeded"
        assert review["reported_cost_usd"] == 1.25
        assert "Corrected text" in Path(review["output"]).read_text(encoding="utf-8")
        assert "log-only" in Path(review["log"]).read_text(encoding="utf-8")


def test_repeated_models_and_slug_collisions(harness: Harness) -> None:
    result, summary = harness.run(
        ("fake/one", "fake/one", "fake-one"), env={"COARSE_FAKE_BARRIER": "3"}
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert len({review["output"] for review in summary["reviews"]}) == 3


def test_failure_does_not_stop_other_reviews(harness: Harness) -> None:
    result, summary = harness.run(("fake/fail", "fake/two"))
    assert result.returncode == 1
    assert [review["status"] for review in summary["reviews"]] == ["failed", "succeeded"]
    assert "review failed deliberately" in _plain(result.stdout)


def test_extraction_failure_prevents_reviews(harness: Harness) -> None:
    result, summary = harness.run(env={"COARSE_FAKE_EXTRACTION_FAIL": "1"})
    assert result.returncode == 1
    assert harness.events("review:") == []
    assert summary["extraction"]["status"] == "failed"
    assert all(review["status"] == "skipped" for review in summary["reviews"])


def test_missing_key_fails_before_extraction_and_creates_nothing(harness: Harness) -> None:
    result = subprocess.run(
        harness.command(),
        env={**harness.env, "COARSE_FAKE_MISSING_KEY": "fake/two"},
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "No API key configured for: fake/two" in _plain(result.stdout + result.stderr)
    assert not harness.trace.exists()
    # Preflight runs before the run directory exists.
    assert not harness.outputs.exists()


def test_no_qa_disables_garble_override(harness: Harness) -> None:
    result, summary = harness.run(extra=("--no-qa",), env={"COARSE_FAKE_GARBLE": "0.2"})
    assert result.returncode == 0, result.stdout + result.stderr
    assert harness.events("qa:") == []
    assert summary["extraction"]["details"]["qa_status"] == "disabled"


def test_garble_enables_qa_with_config_off(harness: Harness) -> None:
    result, _ = harness.run(env={"COARSE_FAKE_QA": "0", "COARSE_FAKE_GARBLE": "0.2"})
    assert result.returncode == 0, result.stdout + result.stderr
    assert len(harness.events("qa:")) == 1


def test_missing_vision_key_warns_and_continues(harness: Harness) -> None:
    result, summary = harness.run(env={"COARSE_FAKE_MISSING_KEY": "fake/vision"})
    assert result.returncode == 0, result.stdout + result.stderr
    assert harness.events("qa:") == []
    assert "skipped: no vision-model API key" in _plain(result.stdout)
    assert summary["extraction"]["warnings"] == ["skipped: no vision-model API key"]


def test_non_pdf_skips_qa(harness: Harness) -> None:
    harness.paper = harness.root / "paper.md"
    harness.paper.write_text("# A paper", encoding="utf-8")
    result, summary = harness.run()
    assert result.returncode == 0, result.stdout + result.stderr
    assert harness.events("qa:") == []
    assert summary["extraction"]["details"]["qa_status"] == "not applicable"


def test_env_file_and_language_are_forwarded(harness: Harness) -> None:
    env_file = harness.root / "keys.env"
    env_file.write_text("COARSE_FAKE_KEY=from-dotenv\n", encoding="utf-8")
    result, _ = harness.run(
        extra=("--env-file", str(env_file), "--language", "French"),
        env={"COARSE_FAKE_KEY": "from-environment"},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    reviews = [json.loads(line) for line in harness.events("review:")]
    assert reviews, "no reviews ran"
    for event in reviews:
        assert event["key"] == "from-dotenv"  # --env-file overrides the environment
        assert event["language"] == "French"
    # Credentials never land in the run directory: not the value, not the path.
    assert harness.summary_path is not None
    assert "from-dotenv" not in harness.summary_path.read_text(encoding="utf-8")
    for job_file in harness.summary_path.parent.glob("*.job.json"):
        text = job_file.read_text(encoding="utf-8")
        assert "from-dotenv" not in text
        assert "env_file" not in json.loads(text)


def test_malformed_events_do_not_fail_review(harness: Harness) -> None:
    result, summary = harness.run(("fake/malformed",))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Ignored malformed" in _plain(result.stdout)
    assert summary["reviews"][0]["warnings"]


def test_redirected_output_stays_plain_with_force_color(harness: Harness) -> None:
    result, _ = harness.run(("fake/one",), env={"FORCE_COLOR": "1"})
    assert result.returncode == 0, result.stdout + result.stderr
    assert "\x1b" not in result.stdout
    assert "coarse parallel reviews" not in result.stdout


def test_help_and_noninteractive_confirmation(harness: Harness) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "coarse", "review-parallel", "--help"],
        env=harness.env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    help_text = _plain(result.stdout)
    assert "--model" in help_text
    assert "--from" not in help_text
    command = [arg for arg in harness.command() if arg != "--yes"]
    result = subprocess.run(
        command, input="", capture_output=True, text=True, env=harness.env, timeout=30
    )
    assert result.returncode == 2, result.stdout + result.stderr
    assert "require --yes" in _plain(result.stdout + result.stderr)
    assert not harness.outputs.exists()


def test_live_terminal_output(harness: Harness) -> None:
    master, slave = pty.openpty()
    process = subprocess.Popen(
        harness.command(("fake/one",)), env=harness.env, stdout=slave, stderr=slave
    )
    os.close(slave)
    output = b""
    deadline = time.monotonic() + 20
    try:
        while time.monotonic() < deadline:
            ready, _, _ = select.select([master], [], [], 0.2)
            if ready:
                try:
                    chunk = os.read(master, 65536)
                except OSError:
                    break
                if not chunk:
                    break
                output += chunk
            elif process.poll() is not None:
                break
        assert process.wait(timeout=5) == 0, output.decode(errors="replace")
    finally:
        os.close(master)
        if process.poll() is None:
            process.kill()
            process.wait()
    assert b"coarse parallel reviews" in output
    assert b"\x1b[" in output
    assert b"log-only" not in output


def test_interrupt_kills_worker_descendants(harness: Harness) -> None:
    process = subprocess.Popen(
        harness.command(("fake/hang", "fake/one")),
        env=harness.env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    child_pid = None
    try:
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            if harness.events("child:"):
                child_pid = int(harness.events("child:")[0])
                summaries = list(harness.outputs.glob("*/summary.json"))
                if summaries:
                    summary = json.loads(summaries[0].read_text(encoding="utf-8"))
                    if summary["reviews"][1]["status"] == "succeeded":
                        break
            time.sleep(0.05)
        assert child_pid is not None, "review subprocess never started"
        process.send_signal(signal.SIGINT)
        stdout, stderr = process.communicate(timeout=10)
        run_logs = "".join(
            path.read_text(encoding="utf-8") for path in harness.outputs.glob("*/run.log")
        )
        assert process.returncode == 130, stdout + stderr + run_logs
        summary = json.loads(
            next(harness.outputs.glob("*/summary.json")).read_text(encoding="utf-8")
        )
        assert summary["exit_code"] == 130
        assert [review["status"] for review in summary["reviews"]] == ["cancelled", "succeeded"]
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            try:
                os.kill(child_pid, 0)
            except ProcessLookupError:
                break
            time.sleep(0.05)
        else:
            pytest.fail("worker descendant survived cancellation")
    finally:
        if process.poll() is None:
            process.send_signal(signal.SIGTERM)
            process.communicate(timeout=10)
        if child_pid:
            try:
                os.kill(child_pid, signal.SIGKILL)
            except ProcessLookupError:
                pass


# ---------------------------------------------------------------------------
# In-process unit tests
# ---------------------------------------------------------------------------


def test_slug_and_clean_text() -> None:
    assert cli_parallel.slug("openai/gpt-5") == "openai-gpt-5"
    assert cli_parallel.slug("...") == "review"
    assert len(cli_parallel.slug("x" * 200)) == 90
    # Non-printables are dropped and whitespace collapses; what remains of an
    # escape sequence is inert literal text.
    assert cli_parallel.clean_text("a\x1b b\n\tc\x00") == "a b c"
    assert cli_parallel.clean_text("\x1b[31mred\x1b[0m") == "[31mred[0m"


class _StubDisplay:
    def __init__(self) -> None:
        self.transitions: list[tuple[str, str]] = []

    def transition(self, job: cli_parallel.Job, message: str) -> None:
        self.transitions.append((job.label, message))


def _job(tmp_path: Path) -> cli_parallel.Job:
    return cli_parallel.Job(
        "01 fake/one", {"kind": "review", "model": "fake/one"}, tmp_path / "j.log"
    )


def test_receive_event_applies_valid_progress(tmp_path: Path) -> None:
    job, display = _job(tmp_path), _StubDisplay()
    event = {
        "type": "progress",
        "event": "updated",
        "stage_key": "s",
        "stage": "Reviewing",
        "completed": 2,
        "total": 5,
        "reported_cost_usd": 0.5,
    }
    cli_parallel.receive_event(job, json.dumps(event).encode(), display)
    assert (job.completed, job.total, job.cost, job.stage) == (2, 5, 0.5, "Reviewing")
    assert display.transitions == [("01 fake/one", "Reviewing")]
    cli_parallel.receive_event(job, json.dumps({"type": "result", "details": {}}).encode(), display)
    assert job.received_result is True


@pytest.mark.parametrize(
    "payload",
    [
        b"not json",
        b'{"type": "progress", "stage": 3}',
        b'{"type": "progress", "stage": "x", "completed": -1, "total": 2, "reported_cost_usd": 0}',
        b'{"type": "progress", "stage": "x", "completed": 1, "total": 2, "reported_cost_usd": "1"}',
        b'{"type": "result", "details": []}',
        b'{"type": "mystery"}',
    ],
)
def test_receive_event_rejects_malformed_payloads_once(tmp_path: Path, payload: bytes) -> None:
    job, display = _job(tmp_path), _StubDisplay()
    cli_parallel.receive_event(job, payload, display)
    cli_parallel.receive_event(job, payload, display)
    assert job.warnings == ["Ignored malformed worker progress event; see log."]
    assert len(display.transitions) == 1
    assert "Ignored worker event" in job.log.read_text(encoding="utf-8")
    assert job.completed is None and not job.received_result


def test_preflight_rejects_unsupported_format(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unsupported input format"):
        cli_parallel.preflight(tmp_path / "paper.xyz", ["fake/one"], CoarseConfig())


def test_preflight_reports_every_model_without_a_key(tmp_path: Path) -> None:
    def fake_resolve(model: str, config: CoarseConfig) -> str | None:
        return None if model.endswith("nokey") else "sk-test"

    with patch("coarse.cli_parallel.resolve_api_key", fake_resolve):
        cli_parallel.preflight(tmp_path / "paper.pdf", ["fake/one"], CoarseConfig())
        with pytest.raises(ValueError, match="No API key configured for: a/nokey, b/nokey"):
            cli_parallel.preflight(
                tmp_path / "paper.pdf", ["a/nokey", "fake/one", "b/nokey"], CoarseConfig()
            )


def test_worker_main_rejects_direct_invocation(capsys) -> None:
    assert cli_parallel.worker_main([]) == 2
    assert cli_parallel.worker_main(["--_worker", "spec"]) == 2
    assert "internal worker entry point" in capsys.readouterr().err


def test_worker_command_targets_this_module() -> None:
    command = cli_parallel._worker_command(Path("/run/x.job.json"), 7)
    assert command[:4] == [sys.executable, "-u", "-m", "coarse.cli_parallel"]
    assert command[4:] == ["--_worker", "/run/x.job.json", "7"]
