"""Bounded Python execution for agent-run algebra and numeric checks (#264).

Nine of the sixteen reference findings in ``evals/references/psi.json`` require
differentiating an expression, substituting concrete values, or evaluating a
bound. A text-only model has to do that in its head, which is the regime where
the pipeline has previously produced confident wrong arithmetic. This module
lets an agent run the check instead.

Bounds enforced on the child process:

* wall-clock timeout and address-space cap via ``resource``;
* output truncated;
* ``-I`` isolated mode, so the current directory and user site-packages are
  not on ``sys.path`` and a stray ``json.py`` beside the workspace cannot be
  imported;
* a scratch cwd, never the workspace or the repository.

Network denial is enforced by the OS where a mechanism is available, and
otherwise is **not** enforced:

* macOS: ``sandbox-exec`` with a deny-network profile. This holds against a
  child process too, so ``subprocess`` cannot shell out to ``curl``.
* Linux: ``unshare --net`` when permitted (it needs either root or
  unprivileged user namespaces).
* Anywhere else, or when the mechanism is unavailable: no network bound at
  all. ``available_isolation()`` reports which case applies, and the tool
  description shown to the model is written from it.

The in-process ``socket`` patch in the preamble is a speed bump, not a bound.
It is kept because it turns the common accidental case into a clear error
message, but it is defeated by ``import _socket`` or by ``subprocess``, and
both are covered by tests that assert the bypass so the limitation stays
visible.

Also not bounded in any mode: the child can read files the user can read.
Confining the filesystem needs the same OS-level isolation plus a path policy
and is not implemented. On the hosted path the surrounding container supplies
the rest.

This runs code the *model* wrote to check its own reasoning. It must never be
used to run code taken out of the paper under review.
"""

from __future__ import annotations

import functools
import os
import platform
import resource
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass

DEFAULT_TIMEOUT_S = 30
DEFAULT_MEMORY_BYTES = 1_024 * 1_024 * 1_024
MAX_OUTPUT_CHARS = 8_000
MAX_CODE_CHARS = 20_000

# Disable network at the Python level as a second line of defence behind "the
# allowed import set has no network client". Keeps an agent that imports
# urllib from quietly exfiltrating the manuscript.
#
# A speed bump, not a bound. It makes the ordinary `urllib`/`requests` path
# fail with a legible message instead of hanging, which saves the agent turns;
# it does NOT stop `import _socket` or `subprocess`. Real denial comes from
# ``_isolation_prefix`` below. Patch the connecting methods rather than
# replacing ``socket.socket``: replacing the class breaks ``ssl`` at import
# time (it subclasses ``socket.socket``), which surfaces as an unrelated
# TypeError.
_PREAMBLE = """\
import socket as _socket

_MSG = "network access is disabled in this sandbox"


def _no_network(*_a, **_k):
    raise OSError(_MSG)


_socket.socket.connect = _no_network
_socket.socket.connect_ex = _no_network
_socket.socket.sendto = _no_network
_socket.create_connection = _no_network
_socket.getaddrinfo = _no_network
_socket.gethostbyname = _no_network
del _no_network
"""


@dataclass(frozen=True)
class SandboxResult:
    """Outcome of one sandboxed run."""

    ok: bool
    stdout: str
    stderr: str
    timed_out: bool = False
    timeout_s: int = DEFAULT_TIMEOUT_S

    def render(self) -> str:
        """Format for feeding back to the model as a tool result."""
        if self.timed_out:
            return f"TIMEOUT after {self.timeout_s}s. No output captured."
        parts = []
        if self.stdout.strip():
            parts.append(f"stdout:\n{self.stdout.rstrip()}")
        if self.stderr.strip():
            parts.append(f"stderr:\n{self.stderr.rstrip()}")
        if not parts:
            parts.append("(no output — remember to print() what you want to see)")
        return "\n\n".join(parts)


# macOS seatbelt profile: inherit the ordinary filesystem view, deny all
# networking. Verified to hold for child processes as well, so a sandboxed
# script cannot reach the network by exec'ing curl.
_MACOS_DENY_NETWORK_PROFILE = "(version 1)\n(allow default)\n(deny network*)\n"


@functools.lru_cache(maxsize=1)
def available_isolation() -> str:
    """Return which network-denial mechanism this host offers.

    One of ``"seatbelt"`` (macOS ``sandbox-exec``), ``"netns"`` (Linux
    ``unshare --net``), or ``"none"``. Probed once per process by actually
    running the mechanism, because both can be present and refuse: seatbelt
    profiles can be rejected, and ``unshare`` needs root or unprivileged user
    namespaces.
    """
    if platform.system() == "Darwin" and shutil.which("sandbox-exec"):
        if _probe(["sandbox-exec", "-p", _MACOS_DENY_NETWORK_PROFILE]):
            return "seatbelt"
    if platform.system() == "Linux" and shutil.which("unshare"):
        if _probe(["unshare", "--net", "--map-root-user"]):
            return "netns"
        if _probe(["unshare", "--net"]):
            return "netns"
    return "none"


def _probe(prefix: list[str]) -> bool:
    """True if *prefix* can run a trivial command successfully."""
    try:
        proc = subprocess.run(
            [*prefix, sys.executable, "-I", "-c", "print(1)"],
            capture_output=True,
            text=True,
            timeout=25,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return proc.returncode == 0 and proc.stdout.strip() == "1"


def _isolation_prefix() -> list[str]:
    """Command prefix that denies the child network access, if any."""
    mechanism = available_isolation()
    if mechanism == "seatbelt":
        return ["sandbox-exec", "-p", _MACOS_DENY_NETWORK_PROFILE]
    if mechanism == "netns":
        if _probe(["unshare", "--net", "--map-root-user"]):
            return ["unshare", "--net", "--map-root-user"]
        return ["unshare", "--net"]
    return []


def network_is_denied() -> bool:
    """Whether a run of this sandbox actually has no network access."""
    return available_isolation() != "none"


def _set_limits(memory_bytes: int) -> None:
    """Child-process preexec hook: cap address space and disable core dumps."""
    try:
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
    except (ValueError, OSError):
        pass
    try:
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    except (ValueError, OSError):
        pass


def run_python(
    code: str,
    *,
    timeout_s: int = DEFAULT_TIMEOUT_S,
    memory_bytes: int = DEFAULT_MEMORY_BYTES,
) -> SandboxResult:
    """Execute *code* in a bounded subprocess and return its output."""
    if len(code) > MAX_CODE_CHARS:
        return SandboxResult(
            ok=False,
            stdout="",
            stderr=f"code too long ({len(code)} chars, limit {MAX_CODE_CHARS})",
        )

    env = {
        "PATH": "/usr/bin:/bin",
        "HOME": "/nonexistent",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "MPLBACKEND": "Agg",
    }
    # Preserve the interpreter's own library path so sympy/numpy resolve, but
    # nothing from the user's environment or the current directory.
    if sys.prefix:
        env["VIRTUAL_ENV"] = sys.prefix

    with tempfile.TemporaryDirectory(prefix="coarse-sbx-") as scratch:
        script = os.path.join(scratch, "check.py")
        with open(script, "w", encoding="utf-8") as fh:
            fh.write(_PREAMBLE)
            fh.write("\n")
            fh.write(code)
        try:
            proc = subprocess.run(
                [*_isolation_prefix(), sys.executable, "-I", "-S", "-c", _loader(script)],
                capture_output=True,
                text=True,
                timeout=timeout_s,
                cwd=scratch,
                env=env,
                preexec_fn=lambda: _set_limits(memory_bytes),
                check=False,
            )
        except subprocess.TimeoutExpired:
            return SandboxResult(
                ok=False, stdout="", stderr="", timed_out=True, timeout_s=timeout_s
            )

    return SandboxResult(
        ok=proc.returncode == 0,
        stdout=(proc.stdout or "")[:MAX_OUTPUT_CHARS],
        stderr=(proc.stderr or "")[:MAX_OUTPUT_CHARS],
        timeout_s=timeout_s,
    )


def _loader(script_path: str) -> str:
    """Build the -c program that restores site-packages then runs the script.

    ``-I -S`` strips the current directory, user site-packages and ``site``
    processing. The interpreter's own ``site-packages`` is then re-added
    explicitly so ``sympy`` and ``numpy`` import, without ever putting the
    script's directory or the caller's cwd on the path.
    """
    import site
    import sysconfig

    paths = [sysconfig.get_paths().get("purelib"), sysconfig.get_paths().get("platlib")]
    try:
        paths.extend(site.getsitepackages())
    except Exception:
        pass
    wanted = sorted({p for p in paths if p and os.path.isdir(p)})
    return (
        "import sys, runpy\n"
        f"sys.path.extend({wanted!r})\n"
        f"runpy.run_path({script_path!r}, run_name='__main__')\n"
    )
