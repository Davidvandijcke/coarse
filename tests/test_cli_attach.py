"""Tests for the ``coarse-review --attach`` signal-driven wait mode.

Extracted from ``tests/test_cli_review.py`` in the same refactor that
moved the watcher implementation out of ``coarse.cli_review`` and into
``coarse.cli_attach``. These tests exercise the watcher directly
against a fake subprocess — the launcher-level tests
(``test_attach_mutually_exclusive_with_detach``,
``test_detach_writes_pidfile_with_correct_pid``) stay in
``tests/test_cli_review.py`` because they test ``main`` and
``_detach_review_process``, which still live on the launcher side.

The pinned contract is spelled out in the ``run_attach`` docstring in
``src/coarse/cli_attach.py``; this file is the canary for it.
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from coarse import cli_attach
from coarse.cli_attach import (
    pidfile_for_log,
    read_pidfile,
    run_attach,
    write_pidfile,
)


@pytest.fixture()
def _fast_attach(monkeypatch):
    """Collapse attach timing knobs so tests run in milliseconds.

    Production values (30s heartbeat, 5s pid poll, 5s grace) produce
    the real-world behavior; these values just shrink the same loop
    to fit in a pytest run without changing any semantics. The
    underscore-prefixed attributes are private module state, but
    ``monkeypatch.setattr`` works on any attribute name — the leading
    underscore is just a naming convention.
    """
    monkeypatch.setattr(cli_attach, "_ATTACH_HEARTBEAT_SECONDS", 0.05)
    monkeypatch.setattr(cli_attach, "_ATTACH_PID_POLL_SECONDS", 0.02)
    monkeypatch.setattr(cli_attach, "_ATTACH_PIDFILE_GRACE_SECONDS", 0.5)
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
    """Regression: ``pidfile_for_log`` returns ``<log>.pid``.

    The watcher and the launcher both derive the pidfile from the
    log path — they must agree on the exact suffix scheme or a race
    between the two sites leaves stale files behind.
    """
    log = tmp_path / "coarse-review-abc.log"
    assert pidfile_for_log(log) == tmp_path / "coarse-review-abc.log.pid"


def test_write_pidfile_is_atomic_and_owner_readable(tmp_path: Path) -> None:
    """``write_pidfile`` writes via rename and tightens perms to 0600.

    Atomic-via-rename is the property that lets a racing ``run_attach``
    read the pidfile safely. The mode check is best-effort (Windows
    skips it) so the test only asserts 0600 on POSIX.
    """
    log = tmp_path / "review.log"
    pidfile = pidfile_for_log(log)
    write_pidfile(pidfile, 12345)
    assert pidfile.exists()
    assert read_pidfile(pidfile) == 12345
    if os.name != "nt":
        mode = pidfile.stat().st_mode & 0o777
        assert mode == 0o600, f"expected 0600, got 0o{mode:o}"


def test_attach_missing_pidfile_exits_3(tmp_path, _fast_attach, capsys) -> None:
    """Regression: ``run_attach`` bails cleanly when the pidfile never
    appears within the grace window.

    This is the "user pointed --attach at the wrong log path" case.
    Before the grace loop existed, the watcher would hang forever.
    The grace window is monkeypatched to 0.5s so the test finishes
    fast.
    """
    log = tmp_path / "ghost.log"
    rc = run_attach(log, timeout_seconds=5)
    assert rc == 3
    err = capsys.readouterr().err
    assert "pidfile" in err and "did not appear" in err


def test_attach_empty_pidfile_exits_3(tmp_path, _fast_attach, capsys) -> None:
    """Malformed pidfile (empty string) should exit 3, not crash."""
    log = tmp_path / "broken.log"
    pidfile_for_log(log).write_text("", encoding="utf-8")
    log.write_text("", encoding="utf-8")
    rc = run_attach(log, timeout_seconds=5)
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
        write_pidfile(pidfile_for_log(log), proc.pid)
        rc = run_attach(log, timeout_seconds=10)
    finally:
        proc.wait(timeout=5)
    out = capsys.readouterr().out
    assert rc == 0, f"expected clean exit, got {rc}; stdout={out!r}"
    assert "starting extraction" in out
    assert "section 1 done" in out
    assert "REVIEW COMPLETE" in out
    # Watcher cleaned up the pidfile on exit.
    assert not pidfile_for_log(log).exists()


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
        write_pidfile(pidfile_for_log(log), proc.pid)
        rc = run_attach(log, timeout_seconds=10)
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
        write_pidfile(pidfile_for_log(log), proc.pid)
        rc = run_attach(log, timeout_seconds=10)
    finally:
        proc.wait(timeout=5)
    err = capsys.readouterr().err
    assert rc == 2
    assert "without a completion marker" in err


def test_attach_emits_heartbeat_when_log_is_idle(tmp_path, _fast_attach, capsys) -> None:
    """Regression: ``run_attach`` prints heartbeat lines when the log
    goes quiet, so Claude Code's Bash tool sees activity during the
    10-25 min wait.

    Uses a fake subprocess that sleeps ~0.6s without writing anything
    before finishing. The heartbeat interval is monkeypatched to 0.05s
    so ~10 heartbeats should fire in that window. The sleep is
    deliberately generous (vs. the 0.05s heartbeat and the 0.02s pid
    poll) so the test stays reliable even under significant load —
    we only need ONE heartbeat line to appear on stdout, and the
    ~10x margin keeps that robust.
    """
    log = tmp_path / "review.log"
    script = textwrap.dedent(
        """
        import sys, time
        log = open(sys.argv[1], 'w')
        log.write('init\\n'); log.flush()
        time.sleep(0.6)
        log.write('REVIEW COMPLETE\\n'); log.flush()
        log.close()
        """
    )
    proc = _spawn_fake_review(log, script=script)
    try:
        write_pidfile(pidfile_for_log(log), proc.pid)
        rc = run_attach(log, timeout_seconds=10)
    finally:
        proc.wait(timeout=5)
    out = capsys.readouterr().out
    assert rc == 0
    assert "[attach] pid=" in out
    # "waiting…" substring is ASCII-safe on the heartbeat line so we
    # can grep for it in CI stdout without encoding gotchas.
    assert "waiting" in out
