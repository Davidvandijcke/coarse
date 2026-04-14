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
    # After #126 the handoff URL and log file are shell-quoted in the
    # runCmd/attachCmd templates so the Vercel protection-bypass `&`
    # in the URL doesn't background the first half of the command.
    # See test_handoff_run_command_quotes_url_for_shell below for the
    # detailed regression context.
    assert "const quotedHandoffUrl = shellQuote(handoffUrl);" in handoff_lib
    assert "const quotedLogFile = shellQuote(logFile);" in handoff_lib
    assert (
        "uvx --python 3.12 --from ${quotedUvFrom} coarse-review --detach "
        "--log-file ${quotedLogFile} --handoff ${quotedHandoffUrl}" in handoff_lib
    )
    # Signal-driven wait: buildCliCommands must emit the matching
    # `--attach` command with the quoted log file. This replaces the
    # legacy per-60s tail polling loop.
    assert (
        "uvx --python 3.12 --from ${quotedUvFrom} coarse-review --attach ${quotedLogFile}"
        in handoff_lib
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

    # The /h/<token> landing-page HTML renderer shares its core runCmd
    # derivation with `buildCliCommands` via `buildHandoffLandingCommands`
    # so the two surfaces can't drift on uvx pin, log-file scheme, or
    # attach-command shape. The landing page shows a host-agnostic run
    # command (no --host/--model/--effort flags); the browser flow
    # appends those via the full `buildCliCommands`.
    assert 'import { buildHandoffLandingCommands } from "@/lib/mcpHandoff";' in handoff_route
    assert (
        "const { setupCmd, runCmd, attachCmd, logFile } = buildHandoffLandingCommands({"
        in handoff_route
    )
    # mcpHandoff.ts itself must define the shared helper so the refactor
    # can't be silently reverted to inline command construction.
    assert "export function buildHandoffLandingCommands(" in handoff_lib
    assert "export interface HandoffCliCommands {" in handoff_lib
    assert (
        "Runs locally on your machine using your own Claude Code, Codex, or Gemini CLI account."
        in handoff_route
    )
    # Temporary git-ref pin — MUST flip back to a semver in the release PR.
    # See the RELEASE BLOCKER note at the top of CHANGELOG.md ## Unreleased.
    assert "coarse-ink[mcp] @ git+https://github.com/Davidvandijcke/coarse@" in handoff_lib
    assert "@feat/mcp-server" not in handoff_lib
    assert "@feat/mcp-server" not in handoff_route


def test_submit_route_handoff_retry_checks_review_status() -> None:
    """Regression: /api/submit's handoff-secret-consumed (403) retry branch
    must SELECT reviews.status before returning success.

    Before this guard, a client that hit Modal dispatch failure then
    retried would see the 403 branch + existing review_emails row and
    get a fake 200 response — even though the underlying review was
    in status='failed' and the /status/<id> page showed the real
    failure. That behavior was documented as a MEDIUM UX finding in
    the pre-PR review; this drift test pins the fix so a future
    refactor can't quietly revert to silent-success-on-failure.

    Asserts the shape of the check: the 403 branch must SELECT
    ``status, error_message`` on the reviews row AND compare
    ``reviewState.status === "failed"`` in code. If either guard is
    removed, a future edit may re-introduce the fake-200 bug and
    this test will fail loudly pointing at the exact pattern to
    restore.
    """
    submit_route = _read("web/src/app/api/submit/route.ts")

    assert "if (handoffAuth.status === 403)" in submit_route
    # The 403 branch must SELECT status + error_message before
    # returning success — without this lookup, the retry has no way
    # to tell a true idempotent success from a failed-then-retried
    # scenario.
    assert '.select("status, error_message")' in submit_route
    # The explicit status='failed' check is the load-bearing guard.
    # The string is pinned verbatim so any refactor that omits the
    # check (or silently loosens the comparison to truthy rather
    # than explicit equality) trips this test.
    assert 'reviewState.status === "failed"' in submit_route
    # Failure responses must return 503, not a fake 200.
    assert "{ status: 503 }" in submit_route


def test_preview_middleware_exempts_handoff_routes() -> None:
    """Regression: the preview Basic Auth gate must skip handoff routes.

    `web/src/middleware.ts` gates every non-static path behind HTTP
    Basic Auth when `VERCEL_ENV=preview` and `PREVIEW_BASIC_AUTH_PASSWORD`
    is set. The CLI / Codex-cloud handoff flow fetches `GET /h/<token>`
    and POSTs `/api/mcp-finalize` without a browser session and cannot
    send Basic Auth, so those routes must short-circuit the gate via
    `isHandoffExemptPath` before the auth challenge runs — otherwise
    every preview handoff returns 401 to the CLI and the detached
    worker crashes without writing a pidfile (the exact failure mode
    that prompted #121 for the Vercel-edge Deployment Protection layer;
    this test pins the analogous fix for the middleware layer).

    Pinned verbatim so a future refactor that drops the exemption, or
    that moves the gate before the check, fails loudly pointing at the
    correct function to restore.
    """
    middleware = _read("web/src/middleware.ts")

    # The helper itself must exist and include at minimum the two
    # routes the CLI actually touches (GET /h/<token> and POST
    # /api/mcp-finalize), plus the MCP-server handoff pair.
    assert "HANDOFF_EXEMPT_PREFIXES" in middleware
    assert '"/h/"' in middleware
    assert '"/api/mcp-finalize"' in middleware
    assert '"/api/mcp-extract"' in middleware
    assert '"/api/mcp-handoff"' in middleware
    assert "function isHandoffExemptPath" in middleware

    # And the Basic Auth gate must check the exempt list BEFORE calling
    # `isAuthorizedForPreview` — otherwise the exemption is a no-op.
    # The expected shape is `!isHandoffExemptPath(... ) && !isAuthorizedForPreview(...)`.
    assert "!isHandoffExemptPath(request.nextUrl.pathname)" in middleware

    # Drift guard: the browser UI routes (landing page, /status, /review)
    # must NOT be in the exempt list — they exist only to be gated.
    assert '"/status/"' not in middleware
    assert '"/review/"' not in middleware
    assert '"/api/cli-handoff"' not in middleware

    # The match function must normalize trailing slashes before
    # composing `prefix + "/"` — otherwise a prefix like `"/h/"`
    # silently becomes `"/h//"` and never matches a real URL, so
    # `/h/<token>` gets 401'd by the preview gate despite being in
    # the exempt list. This is the exact bug we shipped in #122 and
    # that broke the handoff flow end-to-end on the preview deploy
    # even after #124. Pin the normalization so it can't regress.
    assert (
        'rawPrefix.endsWith("/")' in middleware
        or "rawPrefix.endsWith('/')" in middleware
        or ".slice(0, -1)" in middleware
    ), (
        "isHandoffExemptPath must strip a trailing slash from exempt "
        "prefixes before composing `${prefix}/` for the startsWith "
        "check — otherwise `/h/<token>` is never exempted."
    )


def test_handoff_run_command_quotes_url_for_shell() -> None:
    """Regression: after #121 appended the Vercel Deployment Protection
    bypass query params, the handoff URL contains
    ``?x-vercel-protection-bypass=<secret>&x-vercel-set-bypass-cookie=true``.
    The unquoted ``&`` made the shell background the first part of the
    pasted command and run ``x-vercel-set-bypass-cookie=true`` as a
    bogus foreground command — Codex tripped on this exact failure
    mode on a live preview handoff.

    ``buildHandoffLandingCommands`` must wrap ``handoffUrl`` in single
    quotes (via the ``shellQuote`` helper) before embedding it in
    ``runCmd``. Pin the quoting so a future refactor can't drop it.
    """
    import re

    handoff_lib = _read("web/src/lib/mcpHandoff.ts")

    # The helper must call shellQuote on handoffUrl specifically, not
    # just on MCP_UVX_FROM.
    assert "shellQuote(handoffUrl)" in handoff_lib, (
        "buildHandoffLandingCommands must call shellQuote(handoffUrl) "
        "before embedding the URL in runCmd. Otherwise the `&` in the "
        "Vercel protection-bypass query string backgrounds the first "
        "part of the command when the user pastes it into bash/zsh."
    )

    # The bare unquoted form MUST NOT appear in any command template.
    # `--handoff ${handoffUrl}` (no quotes) is the exact bug we're
    # fixing. Use a regex to tolerate whitespace drift.
    bad_pattern = re.compile(r"--handoff\s+\$\{handoffUrl\}")
    assert not bad_pattern.search(handoff_lib), (
        "Found `--handoff ${handoffUrl}` (unquoted) in a command template. "
        "Wrap handoffUrl in `shellQuote(...)` before embedding it."
    )

    # The fixed form must appear — `--handoff ${quotedHandoffUrl}` or
    # equivalent local binding that sources from shellQuote(handoffUrl).
    good_pattern = re.compile(r"--handoff\s+\$\{quotedHandoffUrl\}")
    assert good_pattern.search(handoff_lib), (
        "Expected `--handoff ${quotedHandoffUrl}` in a command template (the quoted form)."
    )


def test_preview_middleware_exempt_match_semantics() -> None:
    """Functional regression: reimplements the JS match logic in Python
    and runs a positive + negative suite against the actual prefix list
    parsed from ``web/src/middleware.ts``. Catches the "trailing-slash
    prefix never matches" bug even if the source is refactored into a
    different shape, as long as the prefix list itself stays parseable.

    The string-content assertions above pin the shape of the code;
    this test pins the observable behavior.
    """
    import re

    middleware = _read("web/src/middleware.ts")

    match = re.search(
        r"const\s+HANDOFF_EXEMPT_PREFIXES\s*=\s*\[([^\]]*)\]",
        middleware,
        re.DOTALL,
    )
    assert match, "could not parse HANDOFF_EXEMPT_PREFIXES from middleware.ts"
    prefixes = re.findall(r'"([^"]+)"', match.group(1))
    assert prefixes, "HANDOFF_EXEMPT_PREFIXES appears empty"

    def is_exempt(pathname: str) -> bool:
        for raw in prefixes:
            prefix = raw[:-1] if raw.endswith("/") else raw
            if pathname == prefix or pathname.startswith(f"{prefix}/"):
                return True
        return False

    # Positive cases: these paths MUST be exempt or the CLI handoff
    # breaks end-to-end behind the preview Basic Auth middleware.
    for exempt_path in (
        "/h/00000000-0000-0000-0000-000000000000",
        "/h/abc123",
        "/api/mcp-finalize",
        "/api/mcp-extract",
        "/api/mcp-handoff",
    ):
        assert is_exempt(exempt_path), (
            f"expected {exempt_path!r} to be exempt from the preview "
            "Basic Auth gate — if this fails the CLI handoff will 401 "
            "on preview deploys with PREVIEW_BASIC_AUTH_PASSWORD set"
        )

    # Negative cases: browser UI must STAY behind the gate, and
    # prefix normalization must NOT false-match sibling paths.
    for protected_path in (
        "/",
        "/status/12345",
        "/review/12345",
        "/api/cli-handoff",
        "/api/presign",
        "/api/submit",
        "/api/status",
        "/api/delete",
        "/api/cancel",
        "/help",  # must not false-match the `/h` prefix after normalization
        "/health",
        "/hqueue",
    ):
        assert not is_exempt(protected_path), (
            f"expected {protected_path!r} to be GATED by the preview "
            "Basic Auth middleware, but the exempt check let it "
            "through — this is a prefix-match false-positive and "
            "would leak the browser UI past the preview gate"
        )


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
