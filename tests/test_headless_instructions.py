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
        assert "uv python install 3.12" in text
        assert "uv tool run --python 3.12 --from ..." in text
        assert "coarse setup" in text
        assert "~/.coarse/config.toml" in text
        assert "uvx --python 3.12 --from 'coarse-ink[mcp]==1.2.2'" in text
        assert "coarse install-skills --all --force" in text
        assert "--detach --log-file /tmp/coarse-review.log" in text
        assert "rg '^  view:|^  local:' /tmp/coarse-review.log" in text
        assert "uv pip install --reinstall" not in text
        assert "@feat/mcp-server" not in text


def test_web_handoff_assets_use_shared_uvx_prompt_flow() -> None:
    handoff_lib = _read("web/src/lib/mcpHandoff.ts")
    handoff_page = _read("web/src/app/page.tsx")
    handoff_route = _read("web/src/app/h/[token]/route.ts")

    assert "command -v uvx || command -v uv" in handoff_lib
    assert "curl -LsSf https://astral.sh/uv/install.sh | sh" in handoff_lib
    assert "uv python install 3.12" in handoff_lib
    assert "uv tool run --python 3.12 --from ..." in handoff_lib
    assert "coarse setup" in handoff_lib
    assert "~/.coarse/config.toml" in handoff_lib
    assert "const MCP_UVX_FROM =" in handoff_lib
    assert "const quotedUvFrom = shellQuote(MCP_UVX_FROM);" in handoff_lib
    assert (
        "uvx --python 3.12 --from ${quotedUvFrom} coarse install-skills --all --force"
        in handoff_lib
    )
    assert (
        "uvx --python 3.12 --from ${quotedUvFrom} coarse-review --detach "
        "--log-file /tmp/coarse-review.log --handoff ${handoffUrl}" in handoff_lib
    )
    assert "rg '^  view:|^  local:' /tmp/coarse-review.log" in handoff_lib

    assert "const fullPrompt = buildAgentPrompt({ setupCmd, runCmd });" in handoff_page
    assert "coarse.ink does not receive or store your" in handoff_page

    assert 'import { MCP_UVX_FROM } from "@/lib/mcpHandoff";' in handoff_route
    assert "const pinnedFrom = MCP_UVX_FROM;" in handoff_route
    assert "const quotedFrom = `'${pinnedFrom}'`;" in handoff_route
    assert (
        "uvx --python 3.12 --from ${quotedFrom} coarse install-skills --all --force"
        in handoff_route
    )
    assert (
        "uvx --python 3.12 --from ${quotedFrom} coarse-review --detach "
        "--log-file /tmp/coarse-review.log --handoff ${handoffUrl}" in handoff_route
    )
    assert (
        "Runs locally on your machine using your own Claude Code, Codex, or Gemini CLI account."
        in handoff_route
    )
    assert "coarse-ink[mcp]==1.2.2" in handoff_lib
    assert "@feat/mcp-server" not in handoff_lib
    assert "@feat/mcp-server" not in handoff_route
