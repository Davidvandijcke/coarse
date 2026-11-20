"""Bounded Python execution for agent-run algebra and numeric checks (#264).

Nine of the sixteen reference findings in ``evals/references/psi.json`` require
differentiating an expression, substituting concrete values, or evaluating a
bound. A text-only model has to do that in its head, which is the regime where
the pipeline has previously produced confident wrong arithmetic. This module
lets an agent run the check instead.

Bounds, all enforced on the child process:

* no network (``socket`` is disabled in the preamble, and nothing in the
  allowed import set opens one);
* wall-clock timeout and address-space cap via ``resource``;
* output truncated;
* ``-I`` isolated mode, so the current directory and user site-packages are
  not on ``sys.path`` and a stray ``json.py`` beside the workspace cannot be
  imported;
* a scratch cwd, never the workspace or the repository.

Not bounded: the child is an ordinary process and can still *read* files the
user can read. Confining the filesystem needs OS-level isolation (a seatbelt
profile on macOS, namespaces or seccomp on Linux) and is not implemented here.
Treat this as a resource and network bound, not a filesystem jail; on the
hosted path the surrounding container supplies the rest.

This runs code the *model* wrote to check its own reasoning. It must never be
used to run code taken out of the paper under review.
"""

from __future__ import annotations

import os
import resource
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
_PREAMBLE = """\
import socket as _socket

def _no_network(*_a, **_k):
    raise OSError("network access is disabled in this sandbox")

_socket.socket = _no_network
_socket.create_connection = _no_network
_socket.getaddrinfo = _no_network
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
                [sys.executable, "-I", "-S", "-c", _loader(script)],
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
