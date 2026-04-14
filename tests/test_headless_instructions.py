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
        # Pin to the version that will be published with the release PR
        # that lands this branch on main. See CHANGELOG.md ## Unreleased
        # "RELEASE BLOCKER" note — DEFAULT_MCP_UVX_FROM and these SKILL.md
        # files must all flip from the temporary git-ref pin to
        # ``coarse-ink[mcp]==1.3.0`` as part of the release cut.
        assert "uvx --python 3.12 --from 'coarse-ink[mcp]==1.3.0'" in text
        assert "coarse install-skills --all --force" in text
        # Per-review unique log file: every skill uses a LOG env var
        # derived from a per-paper suffix so parallel runs in the same
        # shell don't clobber each other's logs.
        assert "LOG=/tmp/coarse-review-" in text
        assert '--detach --log-file "$LOG"' in text
        # Signal-driven wait mode: each SKILL.md must show the
        # `coarse-review --attach "$LOG"` follow-up command so agents
        # replace the old per-poll tail loop with one blocking call.
        assert 'coarse-review --attach "$LOG"' in text
        assert "rg '^  view:|^  local:' \"$LOG\"" in text
        assert "uv pip install --reinstall" not in text
        assert "@feat/mcp-server" not in text
        # Old stale URL must not reappear — canonical host is coarse.ink.
        assert "coarse.vercel.app" not in text
        # The old per-60s polling guidance must not creep back in —
        # the point of --attach is to replace exactly this loop.
        assert "every 60-90 seconds" not in text


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
    # Per-review unique log file threaded via paperId → logFile (see
    # buildCliCommands in mcpHandoff.ts). The log path must be built
    # from paperId so parallel reviews don't clobber each other.
    assert "const logFile = `/tmp/coarse-review-${paperId}.log`;" in handoff_lib
    assert (
        "uvx --python 3.12 --from ${quotedUvFrom} coarse-review --detach "
        "--log-file ${logFile} --handoff ${handoffUrl}" in handoff_lib
    )
    # Signal-driven wait: buildCliCommands must emit the matching
    # `--attach ${logFile}` command so the prompt can reference it.
    # This replaces the legacy per-60s tail polling loop.
    assert (
        "uvx --python 3.12 --from ${quotedUvFrom} coarse-review --attach ${logFile}" in handoff_lib
    )
    assert "attachCmd: string;" in handoff_lib
    assert "rg '^  view:|^  local:' ${logFile}" in handoff_lib

    # page.tsx must pass logFile + attachCmd through to buildAgentPrompt
    # on every call site (handleLaunch + the collapsible manual-commands UI).
    assert (
        "const fullPrompt = buildAgentPrompt({ setupCmd, runCmd, attachCmd, logFile });"
        in handoff_page
    )
    assert "coarse.ink does not receive or store your" in handoff_page

    # The /h/<token> landing-page HTML renderer has its OWN runCmd
    # builder (it can't share buildCliCommands because it emits HTML,
    # not a React prop). It must also thread paperId → logFile + attachCmd through.
    assert 'import { MCP_UVX_FROM } from "@/lib/mcpHandoff";' in handoff_route
    assert "const pinnedFrom = MCP_UVX_FROM;" in handoff_route
    assert "const quotedFrom = `'${pinnedFrom}'`;" in handoff_route
    assert "const logFile = `/tmp/coarse-review-${paperId}.log`;" in handoff_route
    assert (
        "uvx --python 3.12 --from ${quotedFrom} coarse install-skills --all --force"
        in handoff_route
    )
    assert (
        "uvx --python 3.12 --from ${quotedFrom} coarse-review --detach "
        "--log-file ${logFile} --handoff ${handoffUrl}" in handoff_route
    )
    assert (
        "uvx --python 3.12 --from ${quotedFrom} coarse-review --attach ${logFile}" in handoff_route
    )
    assert (
        "Runs locally on your machine using your own Claude Code, Codex, or Gemini CLI account."
        in handoff_route
    )
    # Temporary git-ref pin — MUST flip back to a semver in the release PR.
    # See the RELEASE BLOCKER note at the top of CHANGELOG.md ## Unreleased.
    assert "coarse-ink[mcp] @ git+https://github.com/Davidvandijcke/coarse@" in handoff_lib
    assert "@feat/mcp-server" not in handoff_lib
    assert "@feat/mcp-server" not in handoff_route
