"""Tests for coarse.agent.sandbox.

These run real subprocesses but make no network or provider calls, so they are
zero-spend (#264: deterministic integration coverage for the tool path).
"""

from __future__ import annotations

import pytest

from coarse.agent.sandbox import MAX_CODE_CHARS, run_python


def test_runs_code_and_captures_stdout():
    result = run_python("print(2 + 2)")
    assert result.ok
    assert "4" in result.stdout
    assert "4" in result.render()


def test_reports_an_exception_without_raising():
    result = run_python("raise ValueError('boom')")
    assert not result.ok
    assert "ValueError" in result.stderr
    assert "boom" in result.render()


def test_silent_code_gets_a_hint_to_print():
    assert "print()" in run_python("x = 1").render()


def test_network_access_is_refused():
    result = run_python(
        "import urllib.request\n"
        "print(urllib.request.urlopen('http://example.com', timeout=5).status)"
    )
    assert not result.ok
    assert "disabled" in result.render() or "OSError" in result.render()


def test_socket_connect_is_refused():
    result = run_python("import socket; socket.create_connection(('example.com', 80))")
    assert not result.ok


def test_timeout_is_enforced_and_reported_with_the_actual_limit():
    result = run_python("while True: pass", timeout_s=2)
    assert result.timed_out
    assert not result.ok
    assert "TIMEOUT after 2s" in result.render()


def test_oversized_code_is_refused_before_execution():
    result = run_python("print(1)\n" + "# pad\n" * MAX_CODE_CHARS)
    assert not result.ok
    assert "too long" in result.stderr


def test_the_caller_cwd_is_not_importable():
    """``-I`` keeps a file beside the caller from shadowing a stdlib module."""
    result = run_python("import json, os\nprint(os.path.dirname(json.__file__))")
    assert result.ok
    # Whatever json resolves to, it must not be the sandbox scratch dir.
    assert "coarse-sbx-" not in result.stdout


def test_output_is_truncated():
    from coarse.agent.sandbox import MAX_OUTPUT_CHARS

    result = run_python(f"print('x' * {MAX_OUTPUT_CHARS * 3})")
    assert len(result.stdout) <= MAX_OUTPUT_CHARS


@pytest.mark.parametrize("module", ["sympy", "numpy"])
def test_the_computation_libraries_are_importable(module):
    """The sandbox exists so an agent can check algebra rather than guess it."""
    result = run_python(f"import {module}; print({module}.__name__)")
    assert result.ok, result.render()
    assert module in result.stdout


def test_sympy_reproduces_a_sign_check():
    """The capability the harness was built for: differentiate, don't guess."""
    result = run_python(
        "import sympy as sp\n"
        "n, s, th, y, X = sp.symbols('n s th y X', positive=True)\n"
        "L = (y - X*th)**2 / (n*s)\n"
        "print(sp.simplify(sp.diff(L, th) - 2*X*(X*th - y)/(n*s)) == 0)\n"
    )
    assert result.ok, result.render()
    assert "True" in result.stdout


# ---------------------------------------------------------------------------
# Network denial is an OS-level bound where one is available, and otherwise
# is not a bound at all. These tests pin both halves of that so the claim in
# the docstring and the tool description cannot drift from reality.
# ---------------------------------------------------------------------------


def test_available_isolation_reports_a_known_mechanism():
    from coarse.agent.sandbox import available_isolation, network_is_denied

    mechanism = available_isolation()
    assert mechanism in {"seatbelt", "netns", "none"}
    assert network_is_denied() is (mechanism != "none")


@pytest.mark.skipif(
    not __import__("coarse.agent.sandbox", fromlist=["x"]).network_is_denied(),
    reason="no OS-level network isolation on this host",
)
def test_subprocess_cannot_reach_the_network():
    """The in-process socket patch does not cover this; the OS bound must.

    Shelling out to curl defeated the Python-level patch completely, which is
    why denial moved to sandbox-exec / unshare.
    """
    result = run_python(
        "import subprocess\n"
        "p = subprocess.run(\n"
        "    ['/usr/bin/curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',\n"
        "     '--max-time', '8', 'https://example.com'],\n"
        "    capture_output=True, text=True)\n"
        "print('exit', p.returncode, 'http', (p.stdout or '').strip())\n"
    )
    assert result.ok, result.render()
    # curl exits non-zero and reports no HTTP status when it cannot resolve.
    assert "http 000" in result.stdout or "exit 6" in result.stdout


@pytest.mark.skipif(
    not __import__("coarse.agent.sandbox", fromlist=["x"]).network_is_denied(),
    reason="no OS-level network isolation on this host",
)
def test_the_underlying_socket_extension_cannot_connect():
    """``import _socket`` bypasses the patched ``socket`` module."""
    result = run_python(
        "import _socket\n"
        "s = _socket.socket()\n"
        "s.settimeout(8)\n"
        "s.connect(('example.com', 80))\n"
        "print('CONNECTED')\n"
    )
    assert not result.ok
    assert "CONNECTED" not in result.stdout


def test_the_socket_patch_still_gives_a_legible_message():
    """Kept for the message, not for the bound: an agent that reaches for
    urllib should read a refusal rather than puzzle over a timeout."""
    result = run_python(
        "import urllib.request\n"
        "print(urllib.request.urlopen('http://example.com', timeout=5).status)\n"
    )
    assert not result.ok
    assert "disabled in this sandbox" in result.render()


def test_computation_still_works_under_isolation():
    """The isolation prefix must not break the thing the sandbox is for."""
    result = run_python("import sympy as sp\nx = sp.symbols('x')\nprint(sp.diff(x**3, x))\n")
    assert result.ok, result.render()
    assert "3*x**2" in result.stdout
