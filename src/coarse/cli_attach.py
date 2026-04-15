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


# Command-line substrings used to verify a PID belongs to a coarse-review
# worker rather than an unrelated process that inherited a recycled PID.
# The detached worker is invoked via ``python -m coarse.cli_review ...``
# (see ``_detach_review_process`` in ``cli_review.py``), so its ``ps``
# command line contains ``coarse.cli_review``. The uvx launcher path
# runs ``coarse-review`` as a console script; its cmdline contains the
# string ``coarse-review`` (or ``coarse/cli_review.py`` on some uvx
# layouts). Both substrings are safe to match.
_COARSE_REVIEW_CMDLINE_MARKERS = (
    "coarse.cli_review",
    "coarse-review",
    "coarse/cli_review",
)


def _pid_cmdline(pid: int) -> str | None:
    """Return the command line for a PID, or ``None`` if ``ps`` can't answer.

    On macOS/Linux, ``ps -o command= -p <pid>`` prints the full invocation
    string. Returns ``None`` on any subprocess error so callers can fall
    through to ``kill(0)``-based liveness.
    """
    if os.name == "nt":
        return None
    try:
        result = subprocess.run(
            ["ps", "-o", "command=", "-p", str(pid)],
            capture_output=True,
            text=True,
            timeout=1,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None
    if result.returncode != 0:
        return ""  # ps says no such pid — distinguishable from 'unknown'
    return result.stdout.strip()


def _pid_looks_like_coarse_review(pid: int) -> bool:
    """True if the PID's command line looks like a coarse-review worker.

    Guards against **PID recycling across runs**: if review A crashes
    hard (SIGKILL, OOM, segfault) without firing its atexit pidfile
    cleanup, a stale ``<log>.pid`` is left on disk. Time passes, the OS
    reuses review A's PID for some unrelated process, user points
    ``--attach`` at the same log path. Without this guard,
    ``is_pid_alive`` sees ``os.kill(pid, 0)`` succeed and treats the
    unrelated process as an alive worker — the watcher then hangs for
    the full ``--attach-timeout``.

    With this guard, ``ps -o command=`` is inspected for any of the
    expected coarse-review substrings. A recycled PID whose cmdline
    doesn't match returns False, and ``is_pid_alive`` reports dead.

    Falls back to True when ``ps`` is missing or unreadable — we'd
    rather falsely wait out the timeout than falsely claim a live
    worker is dead, because the false-dead path causes the watcher
    to drain the log and exit while the real worker is still
    running, which loses review output.
    """
    cmdline = _pid_cmdline(pid)
    if cmdline is None:
        return True  # ps missing → fall through to kill(0) result
    if cmdline == "":
        return False  # ps explicitly says no such pid
    return any(marker in cmdline for marker in _COARSE_REVIEW_CMDLINE_MARKERS)


def _windows_pid_alive(pid: int) -> bool:
    """Windows-native process-liveness check via `OpenProcess` +
    `GetExitCodeProcess`. Pure stdlib (no psutil), no subprocess spawn.

    Windows' `os.kill(pid, 0)` is **not supported** — the Windows
    implementation only accepts `SIGTERM`, `CTRL_C_EVENT`, and
    `CTRL_BREAK_EVENT` as signal arguments, and calling it with
    signal 0 raises `OSError: [WinError 87] The parameter is
    incorrect`. The earlier `if os.name == "nt": return True`
    short-circuit sat AFTER the `os.kill` call, so the exception
    fired before the early-return could save us, and the watcher
    crashed on every poll.

    This helper replaces that path entirely. `OpenProcess` with
    `PROCESS_QUERY_LIMITED_INFORMATION` (0x1000) succeeds as long as
    the calling user has any access to the process object (cheaper
    than `PROCESS_QUERY_INFORMATION` and works across session
    boundaries in most cases). `GetExitCodeProcess` then returns
    `STILL_ACTIVE` (259) iff the process is still running.

    The `STILL_ACTIVE == 259` collision (a process that legitimately
    exited with code 259 is indistinguishable from a running one
    via `GetExitCodeProcess` alone) is disambiguated by a follow-up
    `WaitForSingleObject(handle, 0)` call: `WAIT_OBJECT_0` means the
    process object is signaled (i.e., actually exited), `WAIT_TIMEOUT`
    means it is still running. The two-call sequence is the pattern
    Microsoft's own docs recommend for unambiguous liveness checks.

    Returns False on any failure path (PID doesn't exist, permission
    denied, process genuinely exited).
    """
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.windll.kernel32
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    SYNCHRONIZE = 0x00100000
    STILL_ACTIVE = 259
    # WAIT_OBJECT_0 (0x0) signals the process actually exited; we
    # only care about the distinction from WAIT_TIMEOUT below.
    WAIT_TIMEOUT = 0x00000102

    # Open with both QUERY_LIMITED_INFORMATION (for GetExitCodeProcess)
    # and SYNCHRONIZE (for WaitForSingleObject). Both are cheap and
    # granted to the process owner by default.
    handle = kernel32.OpenProcess(
        PROCESS_QUERY_LIMITED_INFORMATION | SYNCHRONIZE,
        False,
        pid,
    )
    if not handle:
        return False
    try:
        exit_code = wintypes.DWORD()
        if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
            return False
        if exit_code.value != STILL_ACTIVE:
            # Process exited with a non-STILL_ACTIVE code — unambiguous dead.
            return False
        # Exit code is 259 — could be STILL_ACTIVE (alive) or a real
        # exit code of 259 (dead). Disambiguate via WaitForSingleObject
        # with a zero timeout. WAIT_OBJECT_0 means the process handle
        # is signaled (actually exited); WAIT_TIMEOUT means still
        # running. Anything else (WAIT_FAILED, WAIT_ABANDONED) we
        # treat as "dead" to err on the side of not hanging the
        # watcher.
        wait_result = kernel32.WaitForSingleObject(handle, 0)
        return wait_result == WAIT_TIMEOUT
    finally:
        kernel32.CloseHandle(handle)


def is_pid_alive(pid: int) -> bool:
    """Portable 'is this PID still running as a coarse-review worker' check.

    On Windows, delegates to ``_windows_pid_alive`` (OpenProcess +
    GetExitCodeProcess) because ``os.kill(pid, 0)`` is not supported
    by the Windows Python runtime — see that helper's docstring.
    The PID-recycling and zombie guards below are POSIX-only (they
    shell out to ``ps``), so Windows callers accept a slightly
    weaker guarantee: the watcher trusts the OS kernel's view of
    process existence, with no command-line fingerprint check. In
    practice this is fine because the coarse-review detached worker
    is the only thing writing to the log path, and PID recycling
    across runs is rare on the short timescale of a review.

    On POSIX:

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
    watcher correctly reports dead in both environments.

    **PID recycling guard**: after all the above returns 'alive', we
    additionally verify via ``_pid_looks_like_coarse_review`` that
    the command line at that PID looks like a coarse-review worker.
    This closes the stale-pidfile-after-hard-crash failure mode
    spelled out in ``_pid_looks_like_coarse_review``'s docstring.

    The ``ps`` probes add ~2ms per poll in the hot path, which is
    negligible at the 5s production poll cadence.
    """
    if os.name == "nt":
        return _windows_pid_alive(pid)

    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        # Another user's process — definitely not our worker (our
        # detached child is always spawned by the current user).
        return False

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
    # State probe passed — process exists and is not a zombie. Now
    # verify its command line looks like a coarse-review worker so
    # a PID recycled from a hard-crashed prior run doesn't masquerade
    # as alive.
    return _pid_looks_like_coarse_review(pid)


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
