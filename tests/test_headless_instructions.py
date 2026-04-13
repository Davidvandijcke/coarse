"""Regression tests for shipped headless-review instructions."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_bundled_skill_assets_use_ephemeral_uvx_flow() -> None:
    skill_paths = [
        "src/coarse/_skills/claude_code/SKILL.md",
        "src/coarse/_skills/codex/SKILL.md",
        "src/coarse/_skills/gemini_cli/SKILL.md",
    ]

    for rel_path in skill_paths:
        text = _read(rel_path)
        assert "command -v uvx || command -v uv" in text
        assert "curl -LsSf https://astral.sh/uv/install.sh | sh" in text
        assert "uv tool run --from ..." in text
        assert "uvx --from 'coarse-ink[mcp] @" in text
        assert "coarse install-skills --all --force" in text
        assert "nohup uvx --from 'coarse-ink[mcp] @" in text
        assert "rg '^  view:|^  local:' /tmp/coarse-review.log" in text
        assert "uv pip install --reinstall" not in text


def test_web_handoff_assets_use_shared_uvx_prompt_flow() -> None:
    handoff_lib = _read("web/src/lib/mcpHandoff.ts")
    handoff_page = _read("web/src/app/page.tsx")
    handoff_route = _read("web/src/app/h/[token]/route.ts")

    assert "command -v uvx || command -v uv" in handoff_lib
    assert "curl -LsSf https://astral.sh/uv/install.sh | sh" in handoff_lib
    assert "uv tool run --from ..." in handoff_lib
    assert "const MCP_UVX_FROM =" in handoff_lib
    assert "uvx --from ${MCP_UVX_FROM} coarse install-skills --all --force" in handoff_lib
    assert "uvx --from ${MCP_UVX_FROM} coarse-review --handoff ${handoffUrl}" in handoff_lib
    assert "nohup ${runCmd} > /tmp/coarse-review.log 2>&1 < /dev/null &" in handoff_lib
    assert "rg '^  view:|^  local:' /tmp/coarse-review.log" in handoff_lib

    assert "const fullPrompt = buildAgentPrompt({ setupCmd, runCmd });" in handoff_page

    assert "uvx --from ${pinnedFrom} coarse install-skills --all --force" in handoff_route
    assert "nohup uvx --from ${pinnedFrom} coarse-review --handoff ${handoffUrl}" in handoff_route
