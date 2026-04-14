"""Signal-driven wait mode for ``coarse-review --attach <log>``.

Extracted from ``coarse.cli_review`` in the refactor that followed the
initial ``--attach`` landing. The launcher half (``--detach``, the
pipeline invocation, handoff fetching) stays in ``cli_review``; the
watcher half (pidfile r/w, PID liveness, log tail loop with
heartbeats, completion markers, exit-code resolution) lives here.

The split is cleanly one-way: this module has zero imports from any
other ``coarse.*`` submodule. It's pure stdlib (os, subprocess, sys,
time, pathlib, atexit). That makes it safe for ``cli_review`` to
import from at module load time without introducing a circular
dependency, and it means the watcher is trivially unit-testable
without touching the pipeline.

**Public API** (imported by ``cli_review``):

- ``pidfile_for_log(log_path)`` — canonical ``<log>.pid`` path scheme
- ``write_pidfile(pidfile, pid)`` — atomic 0600 write used by the launcher
- ``remove_pidfile(pidfile)`` — best-effort cleanup
- ``read_pidfile(pidfile)`` — parse ``<pid>\\n``, return ``None`` on bad/missing
- ``is_pid_alive(pid)`` — portable liveness check with zombie guard
- ``register_pidfile_cleanup(log_file)`` — atexit hook for detached child
- ``run_attach(log_file, *, timeout_seconds)`` — main watcher loop
- ``handle_watcher_interrupt(log_file)`` — prints re-attach hint, returns 130
- ``ATTACH_DEFAULT_TIMEOUT_SECONDS`` — argparse default for --attach-timeout

Timing knobs (``_ATTACH_HEARTBEAT_SECONDS``, ``_ATTACH_PID_POLL_SECONDS``,
``_ATTACH_PIDFILE_GRACE_SECONDS``, ``_ATTACH_READ_CHUNK``,
``_ATTACH_SUCCESS_MARKERS``, ``_ATTACH_FAILURE_MARKERS``) stay
module-private — tests monkeypatch them via
``cli_attach._ATTACH_FOO``, which works fine on underscore-prefixed
module attributes.
"""

from __future__ import annotations

import atexit
import os
import subprocess
import sys
import time
from pathlib import Path

# Module-level knobs. Tests monkeypatch these to run the watch loop
# in milliseconds instead of seconds — see tests/test_cli_attach.py.
_ATTACH_HEARTBEAT_SECONDS = 30.0
"""Emit a ``[attach] pid=<N> elapsed=<mm:ss> — waiting…`` heartbeat on
stdout after this many seconds of log-file inactivity. Keeps Claude
Code's Bash tool from flagging the wait command as idle (the tool
typically watches for stdout activity in a rolling window)."""

_ATTACH_PID_POLL_SECONDS = 5.0
"""How often to check that the review PID is still alive via
``os.kill(pid, 0)``. Short enough that completion is noticed fast,
long enough that the watcher isn't hot-looping for 25 minutes."""

_ATTACH_PIDFILE_GRACE_SECONDS = 5.0
"""Maximum time to wait for the pidfile + log file to appear when
``--attach`` starts before the launcher has finished writing them. The
watcher may race the launcher if an agent chains ``--detach`` +
``--attach`` as two back-to-back Bash calls in the same shell."""

_ATTACH_READ_CHUNK = 8192
"""Bytes to read per log-tail iteration."""

ATTACH_DEFAULT_TIMEOUT_SECONDS = 1800
"""Default ``--attach-timeout`` upper bound. Matches the upper end of a
realistic coarse review runtime (10-25 min) with a small safety
margin. Longer than this almost certainly means the review crashed
silently and the watcher should bail so the agent can report the
timeout instead of hanging its own tool-call. Public because
``cli_review``'s argparse uses it as the flag default."""

# Sentinels the watcher scans the log for to decide its exit code.
_ATTACH_SUCCESS_MARKERS = ("REVIEW COMPLETE", "PUBLISHED TO COARSE WEB")
_ATTACH_FAILURE_MARKERS = ("ERROR: pipeline failed", "WEB CALLBACK FAILED")


# ---------------------------------------------------------------------------
# Pidfile primitives — used by both the launcher (cli_review) and the
# watcher (this module). Atomic-via-rename so a racing --attach never
# sees a half-written pidfile.
# ---------------------------------------------------------------------------


def pidfile_for_log(log_path: Path) -> Path:
    """Return the canonical pidfile path for a detached review log.

    Co-located with the log as ``<log>.pid`` so ``run_attach`` can
    discover it knowing only the log path. See ``write_pidfile`` for
    the write semantics.
    """
    return log_path.with_suffix(log_path.suffix + ".pid")


def write_pidfile(pidfile: Path, pid: int) -> None:
    """Write ``<pid>\\n`` to ``pidfile`` atomically with 0600 perms.

    Atomic-via-rename so a racing ``run_attach`` never sees a
    half-written pidfile. Owner-only perms because the pidfile is
    local metadata that shouldn't leak to other users of the same
    machine.
    """
    pidfile.parent.mkdir(parents=True, exist_ok=True)
    tmp = pidfile.with_suffix(pidfile.suffix + ".tmp")
    if os.name == "nt":
        tmp.write_text(f"{pid}\n", encoding="utf-8")
    else:
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            os.fchmod(fd, 0o600)
        except OSError:
            pass
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(f"{pid}\n")
    os.replace(tmp, pidfile)


def remove_pidfile(pidfile: Path) -> None:
    """Best-effort pidfile cleanup. Safe to call from multiple sites."""
    try:
        pidfile.unlink()
    except FileNotFoundError:
        pass
    except OSError:
        # Permission error, busy file, disk yanked mid-run — don't crash
        # the watcher or the detached child because of cleanup failure.
        pass


def read_pidfile(pidfile: Path) -> int | None:
    """Read a PID from ``pidfile`` or return ``None`` if unreadable/malformed."""
    try:
        raw = pidfile.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    except OSError:
        return None
    if not raw:
        return None
    try:
        return int(raw.splitlines()[0])
    except ValueError:
        return None


def register_pidfile_cleanup(log_file: Path) -> None:
    """Register an atexit hook so the detached child removes its own pidfile.

    Called from ``cli_review.main`` at the top of the detached-child
    branch. The hook is best-effort: if the child crashes before
    atexit runs, ``run_attach`` will see a dead PID, read the final
    log tail, and exit cleanly anyway.
    """
    pidfile = pidfile_for_log(log_file.expanduser().resolve())
    atexit.register(remove_pidfile, pidfile)


# ---------------------------------------------------------------------------
# PID liveness — zombie-aware so pytest can run the watcher against
# fake subprocess children without hitting the 10s timeout.
# ---------------------------------------------------------------------------


def is_pid_alive(pid: int) -> bool:
    """Portable 'is this PID still running' check.

    ``os.kill(pid, 0)`` sends signal 0 — no-op permission check that
    returns normally if the PID exists, ``ProcessLookupError`` if
    it's gone, and ``PermissionError`` if the PID exists but belongs
    to another user (treated as 'alive' — someone is running there).

    **Zombie guard**: on POSIX, ``kill -0`` returns success for a
    zombie (reaped-state) process because the entry still exists in
    the process table until the parent calls ``wait()``. In
    production the detached worker is orphaned to init at launch
    time so init reaps immediately — no zombies — but in pytest the
    test process IS the parent of the fake worker and sees a zombie
    for the whole test. Probe ``ps -o state=`` for a Z state so the
    watcher correctly reports dead in both environments. The ``ps``
    hop adds ~2ms per poll in the hot path, which is negligible at
    the 5s production poll cadence.
    """
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True

    if os.name == "nt":
        return True

    try:
        result = subprocess.run(
            ["ps", "-o", "state=", "-p", str(pid)],
            capture_output=True,
            text=True,
            timeout=1,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        # ps missing or unresponsive — fall back to the kill(0) result.
        return True

    if result.returncode != 0:
        # ps says no such pid — definitely gone, even though kill(0)
        # raced us and saw it.
        return False
    state = result.stdout.strip()
    if state.startswith("Z"):
        return False
    return True


# ---------------------------------------------------------------------------
# Watcher loop helpers.
# ---------------------------------------------------------------------------


def _format_elapsed(seconds: float) -> str:
    """mm:ss for the heartbeat line."""
    total = int(seconds)
    return f"{total // 60:02d}:{total % 60:02d}"


def _scan_markers(text: str) -> tuple[bool, bool]:
    """Scan a blob of log text for completion/failure sentinels.

    Returns ``(saw_success, saw_failure)``. Both flags can be True
    simultaneously — the log can contain an intermediate error followed
    by a successful recovery path. Exit-code resolution picks failure
    over success when both are present (fail-loud), but the success
    flag is still reported so the watcher knows a REVIEW COMPLETE line
    was emitted at some point.
    """
    saw_success = any(marker in text for marker in _ATTACH_SUCCESS_MARKERS)
    saw_failure = any(marker in text for marker in _ATTACH_FAILURE_MARKERS)
    return saw_success, saw_failure


# ---------------------------------------------------------------------------
# Main watcher entry points.
# ---------------------------------------------------------------------------


def run_attach(log_file: Path, *, timeout_seconds: int) -> int:
    """Watch a detached coarse-review run and block until it exits.

    Replaces the per-poll ``tail -20`` loop coding agents run during a
    handoff wait. The design goal is: **one agent-visible Bash call
    for the whole wait**, with incremental stdout so the Bash tool
    sees activity and doesn't flag the command as hung.

    Mechanics:

    1. Resolve the pidfile at ``<log>.pid``. Wait up to
       ``_ATTACH_PIDFILE_GRACE_SECONDS`` for it to appear (covers the
       launcher/watcher race when the agent chains ``--detach`` and
       ``--attach`` as back-to-back Bash calls).
    2. Read + parse the PID.
    3. Open the log file from offset 0 and stream new bytes to stdout
       as they appear. Every ``_ATTACH_HEARTBEAT_SECONDS`` of
       log-file idleness, emit a ``[attach] pid=<N> elapsed=<mm:ss>
       — waiting…`` heartbeat line so the Bash tool's
       activity-detection doesn't kill us.
    4. Every ``_ATTACH_PID_POLL_SECONDS``, check that the review
       process is still alive via ``os.kill(pid, 0)``. Once it exits,
       drain any remaining log bytes and return.
    5. Exit codes:

       - ``0`` — log contains at least one of the success markers
         (``REVIEW COMPLETE`` / ``PUBLISHED TO COARSE WEB``) and no
         failure marker.
       - ``1`` — log contains a failure marker
         (``ERROR: pipeline failed`` / ``WEB CALLBACK FAILED``).
         Failure wins over success if both are present.
       - ``2`` — PID is gone but no marker was seen. Ambiguous
         outcome — the worker probably crashed silently.
       - ``3`` — pidfile missing or malformed after the grace window,
         or the log file never appeared. Caller error (``--attach``
         was pointed at the wrong log).
       - ``124`` — exceeded ``timeout_seconds``. Matches the
         ``timeout(1)`` convention so shells can special-case it.

    The watcher is **passive**: it never signals the detached process.
    If the user kills ``--attach`` (Ctrl+C, Bash tool timeout), the
    detached worker keeps running and can be re-attached from a
    fresh invocation. This is the whole point of decoupling the
    launcher from the watcher.
    """
    log_path = log_file.expanduser().resolve()
    pidfile = pidfile_for_log(log_path)

    # Line-buffer stdout so each log line / heartbeat is flushed immediately
    # to the watching agent's Bash tool. Guarded against stdout replacements
    # that don't expose reconfigure() — pytest's capsys uses a buffer that
    # works, but io.StringIO doesn't, and some CI harnesses wrap stdout in
    # a pipe-based writer that raises AttributeError. Line buffering is a
    # nice-to-have, not load-bearing; failing the whole attach over it would
    # be wrong.
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except (AttributeError, OSError):
        pass

    # Grace window for the launcher to finish writing both the pidfile
    # and the log file. Bounded — we don't want to hang forever if the
    # caller pointed us at the wrong log path.
    start_monotonic = time.monotonic()
    grace_deadline = start_monotonic + _ATTACH_PIDFILE_GRACE_SECONDS
    while not pidfile.exists():
        if time.monotonic() >= grace_deadline:
            print(
                f"[attach] error: pidfile {pidfile} did not appear within "
                f"{_ATTACH_PIDFILE_GRACE_SECONDS:.0f}s. The detached review "
                f"may not have started, or you pointed --attach at the wrong "
                f"log path.",
                file=sys.stderr,
            )
            return 3
        time.sleep(min(0.05, _ATTACH_PIDFILE_GRACE_SECONDS / 10))

    pid = read_pidfile(pidfile)
    if pid is None:
        print(
            f"[attach] error: pidfile {pidfile} is empty or malformed.",
            file=sys.stderr,
        )
        return 3

    print(f"[attach] watching pid={pid} log={log_path}")

    # Wait for the log file to exist too — again bounded by the grace
    # window. The launcher creates both in the same _detach_review_process
    # call, so if the pidfile is there the log almost always is too.
    while not log_path.exists():
        if time.monotonic() >= grace_deadline:
            print(
                f"[attach] error: log file {log_path} did not appear within "
                f"{_ATTACH_PIDFILE_GRACE_SECONDS:.0f}s.",
                file=sys.stderr,
            )
            return 3
        time.sleep(0.05)

    # Tail loop: open the log, read in chunks, emit to stdout, poll PID
    # every _ATTACH_PID_POLL_SECONDS, emit heartbeat every
    # _ATTACH_HEARTBEAT_SECONDS of log-file idleness.
    last_activity = time.monotonic()
    last_pid_poll = 0.0
    buffered_text = ""  # accumulated log content for marker scanning
    timeout_deadline = start_monotonic + max(1, int(timeout_seconds))

    with open(log_path, "r", encoding="utf-8", errors="replace") as fh:
        while True:
            now = time.monotonic()

            if now >= timeout_deadline:
                print(
                    f"[attach] timeout: review did not finish within "
                    f"{timeout_seconds}s (pid={pid} still "
                    f"{'alive' if is_pid_alive(pid) else 'dead'}).",
                    file=sys.stderr,
                )
                return 124

            chunk = fh.read(_ATTACH_READ_CHUNK)
            if chunk:
                sys.stdout.write(chunk)
                buffered_text += chunk
                last_activity = now
                # Don't sleep — there may be more buffered content to
                # flush immediately. Continue the loop.
                continue

            # No new bytes. Decide whether to heartbeat, pid-poll, or sleep.
            if now - last_pid_poll >= _ATTACH_PID_POLL_SECONDS:
                last_pid_poll = now
                if not is_pid_alive(pid):
                    # Process is gone. Drain any final bytes that
                    # landed between our last read and its exit.
                    tail = fh.read()
                    if tail:
                        sys.stdout.write(tail)
                        buffered_text += tail
                    break

            if now - last_activity >= _ATTACH_HEARTBEAT_SECONDS:
                elapsed = now - start_monotonic
                print(f"[attach] pid={pid} elapsed={_format_elapsed(elapsed)} — waiting…")
                last_activity = now

            time.sleep(min(0.2, _ATTACH_PID_POLL_SECONDS / 4))

    # Worker exited. Clean up the pidfile (best-effort — the child's
    # atexit may have beaten us to it).
    remove_pidfile(pidfile)

    saw_success, saw_failure = _scan_markers(buffered_text)
    if saw_failure:
        print("[attach] review ended with a failure marker.")
        return 1
    if saw_success:
        print("[attach] review complete.")
        return 0
    print(
        "[attach] review process exited without a completion marker. "
        "The worker may have crashed silently — inspect the log above.",
        file=sys.stderr,
    )
    return 2


def handle_watcher_interrupt(log_file: Path) -> int:
    """Print a re-attach hint and return exit code 130.

    Called by ``cli_review.main`` from the ``except KeyboardInterrupt``
    branch wrapping ``run_attach``. Factored out of ``main`` so the
    detach-hint logic can be unit-tested without spinning up argparse.

    Ctrl+C on the watcher MUST NOT kill the detached worker — the
    watcher is passive by design. This function just prints the
    state of the world and the exact command needed to re-attach.
    """
    log_path = log_file.expanduser().resolve()
    pid = read_pidfile(pidfile_for_log(log_path))
    print()
    print("[attach] watcher detached (Ctrl+C). The review keeps running in the background.")
    if pid is not None and is_pid_alive(pid):
        print(f"[attach] re-attach with: coarse-review --attach {log_path}")
    return 130
