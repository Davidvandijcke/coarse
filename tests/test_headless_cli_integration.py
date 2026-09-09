"""Opt-in smoke tests for installed host-CLI isolation boundaries.

Run with ``COARSE_RUN_HOST_CLI_INTEGRATION=1``.  Normal CI keeps these tests
skipped because subscription CLIs are not repository dependencies.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from copy import deepcopy

import pytest

from coarse.headless_isolation import (
    CODEX_REVIEW_PERMISSION_PROFILE,
    GEMINI_REVIEW_SETTINGS,
    clean_subprocess_env,
    prepare_gemini_workspace_env,
)

pytestmark = pytest.mark.skipif(
    os.environ.get("COARSE_RUN_HOST_CLI_INTEGRATION") != "1",
    reason="set COARSE_RUN_HOST_CLI_INTEGRATION=1 to test installed subscription CLIs",
)


def _require_cli(name: str) -> str:
    binary = shutil.which(name)
    if binary is None:
        pytest.skip(f"{name} is not installed")
    return binary


@pytest.mark.skipif(os.name == "nt", reason="uses POSIX /bin/cat for a sandbox smoke test")
def test_codex_profile_denies_sibling_but_reads_workspace(tmp_path) -> None:
    codex = _require_cli("codex")
    codex_home = tmp_path / "codex-home"
    workspace = tmp_path / "workspace"
    sibling = tmp_path / "sibling-secret.txt"
    workspace_file = workspace / "visible.txt"
    codex_home.mkdir()
    workspace.mkdir()
    sibling.write_text("must-not-leak", encoding="utf-8")
    workspace_file.write_text("workspace-visible", encoding="utf-8")

    base_cmd = [
        codex,
        "sandbox",
        "-c",
        CODEX_REVIEW_PERMISSION_PROFILE,
        "-P",
        "coarse-review",
        "-C",
        str(workspace),
        "/bin/cat",
    ]
    env = clean_subprocess_env()
    env["CODEX_HOME"] = str(codex_home)

    denied = subprocess.run(base_cmd + [str(sibling)], capture_output=True, env=env, check=False)
    allowed = subprocess.run(
        base_cmd + [str(workspace_file)], capture_output=True, env=env, check=False
    )

    assert denied.returncode != 0
    assert b"must-not-leak" not in denied.stdout
    assert allowed.returncode == 0
    assert allowed.stdout == b"workspace-visible"


def test_gemini_parser_accepts_tool_free_isolated_profile(tmp_path, monkeypatch) -> None:
    gemini = _require_cli("gemini")
    source_home = tmp_path / "source-home"
    workspace = tmp_path / "workspace"
    source_home.mkdir()
    workspace.mkdir()
    monkeypatch.setattr("coarse.headless_isolation.Path.home", lambda: source_home)
    env = prepare_gemini_workspace_env(str(workspace))

    # ``--list-extensions`` exercises argument and settings parsing without a
    # model request. Use a dummy API-key auth selector only for this parser run.
    settings_path = workspace / "gemini-home" / ".gemini" / "settings.json"
    settings = deepcopy(GEMINI_REVIEW_SETTINGS)
    settings["security"]["auth"]["selectedType"] = "gemini-api-key"
    settings_path.write_text(json.dumps(settings), encoding="utf-8")
    env["GEMINI_API_KEY"] = "parser-smoke-only"

    result = subprocess.run(
        [
            gemini,
            "--approval-mode",
            "plan",
            "--output-format",
            "text",
            "--list-extensions",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Invalid policy rule" not in result.stderr


def test_gemini_isolated_profile_ignores_ambient_system_mcp(tmp_path, monkeypatch) -> None:
    gemini = _require_cli("gemini")
    source_home = tmp_path / "source-home"
    workspace = tmp_path / "workspace"
    source_home.mkdir()
    workspace.mkdir()
    monkeypatch.setattr("coarse.headless_isolation.Path.home", lambda: source_home)

    ambient_settings = tmp_path / "ambient-system-settings.json"
    ambient_settings.write_text(
        json.dumps(
            {
                "admin": {"mcp": {"enabled": True}},
                "mcpServers": {"ambient-proof": {"command": "/usr/bin/false"}},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("GEMINI_CLI_SYSTEM_SETTINGS_PATH", str(ambient_settings))
    env = prepare_gemini_workspace_env(str(workspace))

    result = subprocess.run(
        [gemini, "--debug", "mcp", "list"],
        cwd=workspace,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        check=False,
    )

    combined = (result.stdout or "") + (result.stderr or "")
    assert result.returncode == 0, combined
    assert "ambient-proof" not in combined
