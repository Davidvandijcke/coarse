"""Regression guards for web-side security findings.

These tests don't exercise Next.js — the web package has no JS test
runner. Instead they read the TypeScript source verbatim and assert
that the specific unsafe strings Codex security flagged are gone.
Cheaper than adding a vitest dependency for a handful of grep-style
assertions, and enough to catch an accidental revert during review.

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

    # The vulnerable rewrite (finding #4) read an attacker-controllable
    # header and interpolated it into the handoff URL. Guard against:
    #
    #   (a) the exact vulnerable expression (``https://${forwardedHost}``),
    #   (b) any ``request.headers.get(...)`` call whose argument is a
    #       forwarding / host header, anywhere in the file — comments
    #       included. That's a deliberately strict check: a comment that
    #       legitimately needs to reference the old pattern should
    #       rephrase it (e.g. "the previous code read x-forwarded-host
    #       from request.headers") rather than dropping a call-syntax
    #       fragment a future reviewer might cargo-cult.
    #
    # This replaces an earlier hand-rolled TS-comment stripper that had
    # two obvious edge-case holes ( ``/*`` inside a string literal, and
    # trailing ``//`` comments on lines containing ``"``). The
    # substring-only version covers the same attack surface with
    # zero parser surface.
    # x-forwarded-for is intentionally NOT in this list: line 56 reads
    # it for rate-limit IP extraction, which doesn't feed into any URL
    # and isn't a host-header-poisoning vector.
    banned_header_calls = (
        'request.headers.get("x-forwarded-host")',
        'request.headers.get("x-forwarded-proto")',
        'request.headers.get("forwarded")',
        'request.headers.get("host")',
        'request.headers.get("x-original-host")',
    )
    for needle in banned_header_calls:
        assert needle not in src, (
            f"cli-handoff route contains `{needle}` — forwarded / host "
            "headers are attacker-controllable and must not feed into "
            "the handoff URL or any siteUrl derivation. Rephrase any "
            "prose reference in a comment to avoid literal call syntax."
        )

    assert "`https://${forwardedHost}`" not in src, (
        "cli-handoff route still interpolates a forwardedHost into a "
        "`https://...` template literal — host header poisoning regression."
    )
    assert "`http://${forwardedHost}`" not in src, (
        "cli-handoff route still interpolates a forwardedHost into a "
        "`http://...` template literal — host header poisoning regression."
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
