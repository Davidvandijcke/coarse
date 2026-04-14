"""Tests for the standalone coarse-review handoff wrapper."""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path
from unittest.mock import patch

import pytest

from coarse import cli_review
from coarse.cli_review import (
    _infer_handoff_extension,
    _pidfile_for_log,
    _read_pidfile,
    _run_attach,
    _write_pidfile,
    main,
)
from coarse.types import OverviewFeedback, OverviewIssue, PaperText, Review


def _make_review() -> Review:
    return Review(
        title="Targeting Interventions in Networks",
        domain="social_sciences/economics",
        taxonomy="academic/research_paper",
        date="04/12/2026",
        overall_feedback=OverviewFeedback(
            issues=[OverviewIssue(title=f"Issue {i}", body=f"Body {i}.") for i in range(1, 5)]
        ),
        detailed_comments=[],
    )


def test_infer_handoff_extension_prefers_supported_title_suffix() -> None:
    assert (
        _infer_handoff_extension(
            paper_title="paper.md",
            signed_url="https://example.test/storage/papers/123.pdf?token=abc",
            content_type="application/pdf",
        )
        == ".md"
    )


def test_infer_handoff_extension_uses_content_type_fallback() -> None:
    assert (
        _infer_handoff_extension(
            paper_title="paper",
            signed_url="https://example.test/download/no-extension",
            content_type="text/markdown; charset=utf-8",
        )
        == ".md"
    )


def test_main_handoff_supports_markdown_source(tmp_path) -> None:
    """Handoff mode should preserve non-PDF extensions for direct extraction."""
    source = tmp_path / "paper.md"
    source.write_text("# Paper\n", encoding="utf-8")
    out_dir = tmp_path / "out"

    handoff_bundle = {
        "paper_id": "12345678-1234-1234-1234-123456789abc",
        "signed_download_url": "https://example.test/papers/123.md?token=abc",
        "finalize_token": "tok-123",
        "callback_url": "https://example.test/api/mcp-finalize",
        "paper_title": "paper.md",
        "domain": "",
        "taxonomy": "",
    }
    captured: dict[str, object] = {}

    def fake_run_headless_review(paper_path, **kwargs):
        captured["paper_path"] = paper_path
        captured["kwargs"] = kwargs
        return _make_review(), "# Review\n", PaperText(full_markdown="# Paper\n", token_estimate=2)

    with (
        patch("coarse.cli_review._fetch_handoff", return_value=handoff_bundle),
        patch("coarse.cli_review._download_handoff_source", return_value=source),
        patch("coarse.headless_review.run_headless_review", side_effect=fake_run_headless_review),
        patch(
            "coarse.cli_review._post_finalize",
            return_value={"review_url": "https://example.test/review/123"},
        ),
    ):
        rc = main(
            [
                "--handoff",
                "https://example.test/h/token",
                "--host",
                "codex",
                "--model",
                "gpt-5.4",
                "--effort",
                "high",
                "--output-dir",
                str(out_dir),
            ]
        )

    assert rc == 0
    assert captured["paper_path"] == source
    assert captured["kwargs"] == {
        "host": "codex",
        "model": "gpt-5.4",
        "effort": "high",
        "pre_extracted": None,
    }
    assert (out_dir / "paper_review.md").read_text(encoding="utf-8") == "# Review\n"


def test_main_handoff_success_prints_absolute_local_and_view_lines(tmp_path, capsys) -> None:
    source = tmp_path / "paper.md"
    source.write_text("# Paper\n", encoding="utf-8")
    out_dir = tmp_path / "out"
    handoff_bundle = {
        "paper_id": "12345678-1234-1234-1234-123456789abc",
        "signed_download_url": "https://example.test/papers/123.md?token=abc",
        "finalize_token": "tok-123",
        "callback_url": "https://example.test/api/mcp-finalize",
        "paper_title": "paper.md",
        "domain": "",
        "taxonomy": "",
    }

    with (
        patch("coarse.cli_review._fetch_handoff", return_value=handoff_bundle),
        patch("coarse.cli_review._download_handoff_source", return_value=source),
        patch(
            "coarse.headless_review.run_headless_review",
            return_value=(
                _make_review(),
                "# Review\n",
                PaperText(full_markdown="# Paper\n", token_estimate=2),
            ),
        ),
        patch(
            "coarse.cli_review._post_finalize",
            return_value={"review_url": "https://example.test/review/123"},
        ),
    ):
        rc = main(
            [
                "--handoff",
                "https://example.test/h/token",
                "--host",
                "codex",
                "--output-dir",
                str(out_dir),
            ]
        )

    assert rc == 0
    stdout = capsys.readouterr().out
    assert "PUBLISHED TO COARSE WEB" in stdout
    assert "  view:     https://example.test/review/123" in stdout
    assert f"  local:    {(out_dir / 'paper_review.md').resolve()}" in stdout
    assert "REVIEW COMPLETE" in stdout


def test_main_handoff_callback_failure_still_prints_local_footer(tmp_path, capsys) -> None:
    source = tmp_path / "paper.md"
    source.write_text("# Paper\n", encoding="utf-8")
    out_dir = tmp_path / "out"
    handoff_bundle = {
        "paper_id": "12345678-1234-1234-1234-123456789abc",
        "signed_download_url": "https://example.test/papers/123.md?token=abc",
        "finalize_token": "tok-123",
        "callback_url": "https://example.test/api/mcp-finalize",
        "paper_title": "paper.md",
        "domain": "",
        "taxonomy": "",
    }

    with (
        patch("coarse.cli_review._fetch_handoff", return_value=handoff_bundle),
        patch("coarse.cli_review._download_handoff_source", return_value=source),
        patch(
            "coarse.headless_review.run_headless_review",
            return_value=(
                _make_review(),
                "# Review\n",
                PaperText(full_markdown="# Paper\n", token_estimate=2),
            ),
        ),
        patch(
            "coarse.cli_review._post_finalize",
            side_effect=RuntimeError("Callback to https://example.test/api failed: HTTP 500"),
        ),
    ):
        rc = main(
            [
                "--handoff",
                "https://example.test/h/token",
                "--host",
                "codex",
                "--output-dir",
                str(out_dir),
            ]
        )

    assert rc == 7
    stdout = capsys.readouterr().out
    assert "WEB CALLBACK FAILED" in stdout
    assert "  view:     unavailable" in stdout
    assert f"  local:    {(out_dir / 'paper_review.md').resolve()}" in stdout
    assert "REVIEW COMPLETE" in stdout


def test_main_local_mode_prints_absolute_local_footer(tmp_path, capsys) -> None:
    paper = tmp_path / "paper.md"
    paper.write_text("# Paper\n", encoding="utf-8")
    out_dir = tmp_path / "out"

    with patch(
        "coarse.headless_review.run_headless_review",
        return_value=(
            _make_review(),
            "# Review\n",
            PaperText(full_markdown="# Paper\n", token_estimate=2),
        ),
    ):
        rc = main(
            [
                str(paper),
                "--host",
                "codex",
                "--output-dir",
                str(out_dir),
            ]
        )

    assert rc == 0
    stdout = capsys.readouterr().out
    assert "REVIEW COMPLETE" in stdout
    assert f"  local:    {(out_dir / 'paper_review.md').resolve()}" in stdout


def test_main_loads_openrouter_key_from_headless_helper(tmp_path, monkeypatch) -> None:
    paper = tmp_path / "paper.md"
    paper.write_text("# Paper\n", encoding="utf-8")
    out_dir = tmp_path / "out"
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    captured: dict[str, str | None] = {}

    def fake_run_headless_review(*args, **kwargs):
        captured["key"] = os.environ.get("OPENROUTER_API_KEY")
        return _make_review(), "# Review\n", PaperText(full_markdown="# Paper\n", token_estimate=2)

    with (
        patch("coarse.headless_review._find_openrouter_key", return_value="sk-or-v1-dotenv"),
        patch("coarse.headless_review.run_headless_review", side_effect=fake_run_headless_review),
    ):
        rc = main(
            [
                str(paper),
                "--host",
                "codex",
                "--output-dir",
                str(out_dir),
            ]
        )

    assert rc == 0
    assert captured["key"] == "sk-or-v1-dotenv"


def test_main_skips_openrouter_lookup_when_pre_extracted(tmp_path, monkeypatch) -> None:
    paper = tmp_path / "paper.pdf"
    paper.write_text("%PDF", encoding="utf-8")
    pre_extracted = tmp_path / "paper.md"
    pre_extracted.write_text("# Paper\n", encoding="utf-8")
    out_dir = tmp_path / "out"

    with (
        patch(
            "coarse.headless_review._find_openrouter_key",
            side_effect=AssertionError("unexpected"),
        ),
        patch(
            "coarse.headless_review.run_headless_review",
            return_value=(
                _make_review(),
                "# Review\n",
                PaperText(full_markdown="# Paper\n", token_estimate=2),
            ),
        ),
    ):
        rc = main(
            [
                str(paper),
                "--host",
                "codex",
                "--pre-extracted",
                str(pre_extracted),
                "--output-dir",
                str(out_dir),
            ]
        )

    assert rc == 0


def test_main_detach_respawns_cli_with_log_file(tmp_path, capsys, monkeypatch) -> None:
    paper = tmp_path / "paper.md"
    paper.write_text("# Paper\n", encoding="utf-8")
    log_path = tmp_path / "coarse-review.log"
    popen_calls: dict[str, object] = {}

    class _DummyProc:
        pid = 4242

    def fake_popen(cmd, **kwargs):
        popen_calls["cmd"] = cmd
        popen_calls["kwargs"] = kwargs
        return _DummyProc()

    monkeypatch.delenv("COARSE_REVIEW_DETACHED", raising=False)
    monkeypatch.setattr("coarse.cli_review.subprocess.Popen", fake_popen)

    rc = main(
        [
            str(paper),
            "--host",
            "codex",
            "--detach",
            "--log-file",
            str(log_path),
        ]
    )

    assert rc == 0
    stdout = capsys.readouterr().out
    assert "Review PID: 4242" in stdout
    assert f"Log file:   {log_path.resolve()}" in stdout
    assert popen_calls["cmd"][:3] == [popen_calls["cmd"][0], "-m", "coarse.cli_review"]
    assert "--detach" in popen_calls["cmd"]
    assert popen_calls["kwargs"]["env"]["COARSE_REVIEW_DETACHED"] == "1"
    assert log_path.exists()
    assert log_path.stat().st_mode & 0o777 == 0o600


def test_main_detached_child_runs_pipeline_without_respawning(tmp_path, monkeypatch) -> None:
    paper = tmp_path / "paper.md"
    paper.write_text("# Paper\n", encoding="utf-8")
    out_dir = tmp_path / "out"
    popen_called = False
    captured: dict[str, object] = {}

    def fake_popen(*args, **kwargs):
        nonlocal popen_called
        popen_called = True
        raise AssertionError("unexpected respawn")

    def fake_run_headless_review(*args, **kwargs):
        captured["kwargs"] = kwargs
        return _make_review(), "# Review\n", PaperText(full_markdown="# Paper\n", token_estimate=2)

    monkeypatch.setenv("COARSE_REVIEW_DETACHED", "1")
    monkeypatch.setattr("coarse.cli_review.subprocess.Popen", fake_popen)

    with patch("coarse.headless_review.run_headless_review", side_effect=fake_run_headless_review):
        rc = main(
            [
                str(paper),
                "--host",
                "codex",
                "--detach",
                "--output-dir",
                str(out_dir),
            ]
        )

    assert rc == 0
    assert popen_called is False
    assert captured["kwargs"]["host"] == "codex"


# ---------------------------------------------------------------------------
# --attach signal-driven wait mode.
# ---------------------------------------------------------------------------
#
# These tests pin the one-Bash-call wait flow that replaces the
# per-poll tail loop coding agents were running during a handoff
# wait. The design constraints are spelled out in the _run_attach
# docstring in src/coarse/cli_review.py — the tests here are the
# canary for them.
#
# To keep the whole group under two seconds we monkeypatch the three
# timing knobs (heartbeat interval, PID-poll cadence, pidfile grace
# window) down to milliseconds. The production defaults (30s / 5s /
# 5s) would make these tests wall-clock-bound in a way that gates
# CI on sleep().


@pytest.fixture()
def _fast_attach(monkeypatch):
    """Collapse attach timing knobs so tests run in milliseconds.

    Production values (30s heartbeat, 5s pid poll, 5s grace) produce
    the real-world behavior; these values just shrink the same loop
    to fit in a pytest run without changing any semantics.
    """
    monkeypatch.setattr(cli_review, "_ATTACH_HEARTBEAT_SECONDS", 0.05)
    monkeypatch.setattr(cli_review, "_ATTACH_PID_POLL_SECONDS", 0.02)
    monkeypatch.setattr(cli_review, "_ATTACH_PIDFILE_GRACE_SECONDS", 0.5)
    yield


def _spawn_fake_review(
    log_path: Path,
    *,
    script: str,
) -> subprocess.Popen:
    """Spawn a short-lived Python subprocess that behaves like a
    detached coarse-review worker for the purposes of --attach tests.

    ``script`` is inlined Python source that writes to the log file
    via sys.argv[1]. The subprocess is a real OS process so
    ``os.kill(pid, 0)`` behaves correctly (faking the PID check would
    defeat the whole point of the watcher).
    """
    return subprocess.Popen(
        [sys.executable, "-c", script, str(log_path)],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def test_pidfile_path_is_sibling_of_log(tmp_path: Path) -> None:
    """Regression: ``_pidfile_for_log`` returns ``<log>.pid``.

    The watcher and the launcher both derive the pidfile from the
    log path — they must agree on the exact suffix scheme or a race
    between the two sites leaves stale files behind.
    """
    log = tmp_path / "coarse-review-abc.log"
    assert _pidfile_for_log(log) == tmp_path / "coarse-review-abc.log.pid"


def test_write_pidfile_is_atomic_and_owner_readable(tmp_path: Path) -> None:
    """``_write_pidfile`` writes via rename and tightens perms to 0600.

    Atomic-via-rename is the property that lets a racing ``--attach``
    read the pidfile safely. The mode check is best-effort (Windows
    skips it) so the test only asserts 0600 on POSIX.
    """
    log = tmp_path / "review.log"
    pidfile = _pidfile_for_log(log)
    _write_pidfile(pidfile, 12345)
    assert pidfile.exists()
    assert _read_pidfile(pidfile) == 12345
    if os.name != "nt":
        mode = pidfile.stat().st_mode & 0o777
        assert mode == 0o600, f"expected 0600, got 0o{mode:o}"


def test_attach_missing_pidfile_exits_3(tmp_path, _fast_attach, capsys) -> None:
    """Regression: ``--attach`` bails cleanly when the pidfile never
    appears within the grace window.

    This is the "user pointed --attach at the wrong log path" case.
    Before the grace loop existed, the watcher would hang forever.
    The grace window is monkeypatched to 0.5s so the test finishes
    fast.
    """
    log = tmp_path / "ghost.log"
    rc = _run_attach(log, timeout_seconds=5)
    assert rc == 3
    err = capsys.readouterr().err
    assert "pidfile" in err and "did not appear" in err


def test_attach_empty_pidfile_exits_3(tmp_path, _fast_attach, capsys) -> None:
    """Malformed pidfile (empty string) should exit 3, not crash."""
    log = tmp_path / "broken.log"
    _pidfile_for_log(log).write_text("", encoding="utf-8")
    log.write_text("", encoding="utf-8")
    rc = _run_attach(log, timeout_seconds=5)
    assert rc == 3
    err = capsys.readouterr().err
    assert "empty or malformed" in err


def test_attach_happy_path_streams_and_exits_zero(tmp_path, _fast_attach, capsys) -> None:
    """End-to-end happy path: real subprocess writes log lines, emits
    a completion marker, exits — watcher drains the log, prints it
    all, and returns exit code 0.
    """
    log = tmp_path / "review.log"
    script = textwrap.dedent(
        """
        import sys, time
        log = open(sys.argv[1], 'w')
        log.write('starting extraction...\\n'); log.flush()
        time.sleep(0.05)
        log.write('section 1 done\\n'); log.flush()
        time.sleep(0.05)
        log.write('REVIEW COMPLETE\\n'); log.flush()
        log.close()
        """
    )
    proc = _spawn_fake_review(log, script=script)
    try:
        _write_pidfile(_pidfile_for_log(log), proc.pid)
        rc = _run_attach(log, timeout_seconds=10)
    finally:
        proc.wait(timeout=5)
    out = capsys.readouterr().out
    assert rc == 0, f"expected clean exit, got {rc}; stdout={out!r}"
    assert "starting extraction" in out
    assert "section 1 done" in out
    assert "REVIEW COMPLETE" in out
    # Watcher cleaned up the pidfile on exit.
    assert not _pidfile_for_log(log).exists()


def test_attach_returns_one_on_failure_marker(tmp_path, _fast_attach, capsys) -> None:
    """Failure marker in the log → exit 1.

    Failure wins over success if both markers appear (fail-loud).
    """
    log = tmp_path / "review.log"
    script = textwrap.dedent(
        """
        import sys
        log = open(sys.argv[1], 'w')
        log.write('ERROR: pipeline failed — something broke\\n')
        log.close()
        """
    )
    proc = _spawn_fake_review(log, script=script)
    try:
        _write_pidfile(_pidfile_for_log(log), proc.pid)
        rc = _run_attach(log, timeout_seconds=10)
    finally:
        proc.wait(timeout=5)
    out = capsys.readouterr().out
    assert rc == 1, f"expected failure exit, got {rc}; stdout={out!r}"
    assert "ERROR: pipeline failed" in out


def test_attach_returns_two_when_pid_dies_without_marker(tmp_path, _fast_attach, capsys) -> None:
    """Silent crash → exit 2 (ambiguous, probably failed).

    The log has no success marker and no failure marker. The watcher
    reports uncertainty instead of falsely claiming success.
    """
    log = tmp_path / "review.log"
    script = textwrap.dedent(
        """
        import sys
        log = open(sys.argv[1], 'w')
        log.write('processing...\\n')
        log.close()
        """
    )
    proc = _spawn_fake_review(log, script=script)
    try:
        _write_pidfile(_pidfile_for_log(log), proc.pid)
        rc = _run_attach(log, timeout_seconds=10)
    finally:
        proc.wait(timeout=5)
    err = capsys.readouterr().err
    assert rc == 2
    assert "without a completion marker" in err


def test_attach_emits_heartbeat_when_log_is_idle(tmp_path, _fast_attach, capsys) -> None:
    """Regression: ``--attach`` prints heartbeat lines when the log
    goes quiet, so Claude Code's Bash tool sees activity during the
    10-25 min wait.

    Uses a fake subprocess that sleeps ~0.3s without writing anything
    before finishing. The heartbeat interval is monkeypatched to 0.05s
    so multiple heartbeat lines should fire in that window.
    """
    log = tmp_path / "review.log"
    script = textwrap.dedent(
        """
        import sys, time
        log = open(sys.argv[1], 'w')
        log.write('init\\n'); log.flush()
        time.sleep(0.3)
        log.write('REVIEW COMPLETE\\n'); log.flush()
        log.close()
        """
    )
    proc = _spawn_fake_review(log, script=script)
    try:
        _write_pidfile(_pidfile_for_log(log), proc.pid)
        rc = _run_attach(log, timeout_seconds=10)
    finally:
        proc.wait(timeout=5)
    out = capsys.readouterr().out
    assert rc == 0
    assert "[attach] pid=" in out
    # "waiting…" substring is ASCII-safe on the heartbeat line so we
    # can grep for it in CI stdout without encoding gotchas.
    assert "waiting" in out


def test_attach_mutually_exclusive_with_detach(tmp_path, monkeypatch) -> None:
    """Regression: ``main`` rejects ``--attach`` combined with launch-mode flags.

    --attach is watch-only and must not be combined with anything
    that would start a new review. Argparse-level guard, so SystemExit
    with a specific error message.
    """
    log = tmp_path / "review.log"
    log.write_text("", encoding="utf-8")
    _write_pidfile(_pidfile_for_log(log), os.getpid())

    for extra in (
        ["--detach"],
        ["--handoff", "https://example.test/h/abc"],
        [str(tmp_path / "paper.pdf")],
    ):
        with pytest.raises(SystemExit) as excinfo:
            main(["--attach", str(log), *extra])
        # argparse error() exits with code 2
        assert excinfo.value.code == 2


def test_detach_writes_pidfile_with_correct_pid(tmp_path, monkeypatch) -> None:
    """Regression: ``_detach_review_process`` writes ``<log>.pid``
    next to the log containing the subprocess PID.

    Faked subprocess.Popen so the test doesn't actually spawn a
    second Python interpreter. The point is that the pidfile is
    written with the PID the launcher got back from Popen — that's
    the contract ``--attach`` relies on.
    """
    log = tmp_path / "detached.log"
    paper = tmp_path / "paper.pdf"
    paper.write_bytes(b"not-a-real-pdf")

    class _FakePopen:
        def __init__(self, *args, **kwargs):
            self.pid = 424242

    monkeypatch.setattr(cli_review.subprocess, "Popen", _FakePopen)

    rc = cli_review._detach_review_process(
        [str(paper), "--host", "claude", "--detach", "--log-file", str(log)],
        log,
    )
    assert rc == 0
    pidfile = _pidfile_for_log(log)
    assert pidfile.exists(), f"pidfile not written at {pidfile}"
    assert _read_pidfile(pidfile) == 424242
    if os.name != "nt":
        assert (pidfile.stat().st_mode & 0o777) == 0o600
