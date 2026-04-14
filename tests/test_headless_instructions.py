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


def test_release_blocker_pin_is_coupled_to_unreleased_version() -> None:
    """Mechanical guard for the ``DEFAULT_MCP_UVX_FROM`` release blocker.

    The git-ref pin in ``web/src/lib/mcpHandoff.ts`` is allowed to exist
    ONLY while ``__version__`` is still at ``1.2.2`` (i.e. no release
    cut has happened yet). The moment ``src/coarse/__init__.py`` or
    ``pyproject.toml`` bumps to any other version, this test must FAIL
    until the pin is reverted to a semver pin
    (``coarse-ink[mcp]==<new-version>``) and every consumer site is
    updated.

    This catches the failure mode the architecture review flagged:
    a release PR that bumps the version and updates ``SKILL.md`` to
    ``1.3.0`` but silently forgets ``mcpHandoff.ts``. Without this
    test, every other drift-detection assertion still passes and the
    broken pin ships to production, where every user's clipboard
    prompt starts cloning from a git ref that no longer matches the
    published PyPI package.

    The release-cut checklist (CHANGELOG.md ## Unreleased warning
    block) must do all four in the same commit:
      1. Bump pyproject.toml + src/coarse/__init__.py
      2. Publish to PyPI
      3. Revert DEFAULT_MCP_UVX_FROM to coarse-ink[mcp]==<new-version>
      4. Update the three SKILL.md files to match
    This test enforces item 3.
    """
    init_text = _read("src/coarse/__init__.py")
    handoff_lib = _read("web/src/lib/mcpHandoff.ts")

    # Pull the current version out of __init__.py.
    import re as _re

    match = _re.search(r'__version__\s*=\s*"([^"]+)"', init_text)
    assert match is not None, "could not find __version__ in src/coarse/__init__.py"
    current_version = match.group(1)

    has_git_ref_pin = (
        "coarse-ink[mcp] @ git+https://github.com/Davidvandijcke/coarse@" in handoff_lib
    )

    if current_version == "1.2.2":
        # Pre-release state — the git-ref pin is allowed (it was
        # introduced specifically to unblock dev testing against the
        # unreleased install-skills + --attach flow). Either a git
        # ref OR a bare ==1.2.2 pin is acceptable here.
        return

    # Post-release state — the version moved but the pin didn't.
    # This is the exact failure mode this test exists to catch.
    assert not has_git_ref_pin, (
        f"RELEASE BLOCKER: src/coarse/__init__.py is at {current_version!r} "
        f"but web/src/lib/mcpHandoff.ts still pins DEFAULT_MCP_UVX_FROM to a "
        f"git ref. Revert it to 'coarse-ink[mcp]=={current_version}' in the "
        f"same release commit that bumps the version. See the RELEASE BLOCKER "
        f"warning block at the top of ## Unreleased in CHANGELOG.md."
    )
    # Also double-check the semver pin actually matches __version__ so
    # a release that flipped to ==1.3.1 by mistake is also caught.
    expected_semver_pin = f'"coarse-ink[mcp]=={current_version}"'
    assert expected_semver_pin in handoff_lib, (
        f"web/src/lib/mcpHandoff.ts does not contain {expected_semver_pin}; "
        f"the DEFAULT_MCP_UVX_FROM pin must match __version__={current_version!r}."
    )
