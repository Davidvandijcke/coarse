"""Regression guards for web-side security findings.

These tests don't exercise Next.js — the web package has no JS test
runner. Instead they read the TypeScript source verbatim and assert
that the specific unsafe strings Codex security flagged are gone.
Cheaper than adding a vitest dependency for three assertions, and
enough to catch an accidental revert during review.

Covers three findings:

- #1/#5: ``web/src/lib/mcpHandoff.ts`` must not instruct the agent to
  echo/grep the API key value or invite the user to paste the key
  into chat.
- #4: ``web/src/app/api/cli-handoff/route.ts`` must not rebuild
  ``siteUrl`` from the ``x-forwarded-host`` request header.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    path = REPO_ROOT / relative
    assert path.exists(), f"expected {relative} to exist in the repo"
    return path.read_text(encoding="utf-8")


def test_mcp_handoff_prompt_does_not_leak_api_key() -> None:
    src = _read("web/src/lib/mcpHandoff.ts")

    # The value-printing probes (finding #5) must be gone from the
    # actual instruction text. They're still mentioned by name as
    # *forbidden* probes, which is fine — we only need to ensure the
    # prompt does not tell the agent to run them.
    assert "Run `echo $OPENROUTER_API_KEY` and `grep OPENROUTER_API_KEY .env" not in src, (
        "buildAgentPrompt still instructs the agent to echo/grep the "
        "OpenRouter key — that copies the key value into the LLM "
        "transcript. Use presence-only probes instead."
    )

    # The "paste it here" / "paste it to me" option (finding #1) must
    # not appear as an allowed path in the prompt.
    lowered = src.lower()
    assert "paste it here" not in lowered, (
        "buildAgentPrompt still offers 'paste it here' as an option — "
        "that leaks the key to the LLM provider."
    )
    assert "paste it to me" not in lowered, (
        "buildAgentPrompt still offers 'paste it to me' as an option — "
        "that leaks the key to the LLM provider."
    )

    # Positive guard: the new prompt must include an explicit do-not-
    # paste warning and the presence-only probe.
    assert "do not paste" in lowered or "don't paste" in lowered, (
        "buildAgentPrompt should explicitly tell the user/agent not to paste the API key into chat."
    )
    assert 'test -n "$OPENROUTER_API_KEY"' in src, (
        "buildAgentPrompt should use a presence-only env probe "
        '(`test -n "$OPENROUTER_API_KEY"`) instead of echoing the value.'
    )


def test_cli_handoff_route_does_not_trust_forwarded_host() -> None:
    src = _read("web/src/app/api/cli-handoff/route.ts")

    # The vulnerable rewrite (finding #4) lived inside an
    # ``if (siteUrl.includes("localhost"))`` branch that replaced
    # ``siteUrl`` with ``https://${forwardedHost}``. We strip the
    # comments first so that the security-note comment explaining the
    # fix can freely reference both ``x-forwarded-host`` and
    # ``https://${forwardedHost}`` without tripping the guard.
    code_only_lines: list[str] = []
    in_block_comment = False
    for raw_line in src.splitlines():
        line = raw_line
        if in_block_comment:
            end = line.find("*/")
            if end == -1:
                continue
            line = line[end + 2 :]
            in_block_comment = False
        while "/*" in line:
            start = line.find("/*")
            end = line.find("*/", start + 2)
            if end == -1:
                line = line[:start]
                in_block_comment = True
                break
            line = line[:start] + line[end + 2 :]
        # Drop // line comments, but respect a naive string-literal
        # skip so we don't accidentally chop an http URL embedded in a
        # string. Our route only has plain `//` comments, so the simple
        # rule is sufficient.
        if "//" in line and '"' not in line.split("//", 1)[0]:
            line = line.split("//", 1)[0]
        code_only_lines.append(line)
    code_only = "\n".join(code_only_lines)

    assert "x-forwarded-host" not in code_only.lower(), (
        "cli-handoff route still reads x-forwarded-host in executable "
        "code — that header is attacker-controllable and must not feed "
        "into the handoff URL."
    )
    assert "forwardedHost" not in code_only, (
        "cli-handoff route still references a forwardedHost variable "
        "in executable code — host header poisoning regression."
    )


def test_bundled_skills_do_not_leak_api_key() -> None:
    """Finding #1 also patched the three bundled SKILL.md files."""
    for skill in (
        "src/coarse/_skills/claude_code/SKILL.md",
        "src/coarse/_skills/codex/SKILL.md",
        "src/coarse/_skills/gemini_cli/SKILL.md",
    ):
        src = _read(skill)
        lowered = src.lower()

        assert "paste it to me" not in lowered, (
            f"{skill} still offers 'paste it to me' — that leaks the API key to the LLM provider."
        )

        # The old *instructional* lines (finding #1). The new prompt
        # mentions these commands in a "do NOT run" context, which is
        # fine — we only want the old prescriptive lines gone.
        assert (
            "In the environment: `echo $OPENROUTER_API_KEY` or `printenv OPENROUTER_API_KEY`"
        ) not in src, f"{skill} still prescribes echo/printenv of the key value."
        assert (
            "In a `.env` file in the current directory: `grep OPENROUTER_API_KEY .env`"
        ) not in src, (
            f"{skill} still prescribes grep of the .env file — use presence-only probes instead."
        )

        # Positive guard: new prompt must include the presence-only probe.
        assert 'test -n "$OPENROUTER_API_KEY"' in src, (
            f"{skill} should use the presence-only env probe "
            f'`test -n "$OPENROUTER_API_KEY"` instead of echoing the value.'
        )
