// Handoff helpers for the "Review with my subscription" button on the
// coarse web form. The flow is:
//
//   1. User uploads PDF via /api/presign + direct Supabase Storage PUT
//      (same path as the regular OpenRouter review — no extraction
//      triggered).
//   2. User clicks "Review with Claude Code / Codex / Gemini CLI".
//   3. Frontend POSTs to /api/cli-handoff which mints a short-lived
//      finalize_token (3h, see FINALIZE_TOKEN_TTL_MINUTES) bound to
//      the paper_id and returns a handoff URL of the form
//      ``https://coarse.ink/h/<token>`` (or localhost in dev).
//   4. A modal renders the two commands the user pastes into their
//      terminal:
//        - one-time skill refresh: `uvx --python 3.12 --from ... coarse install-skills`
//        - the review: `uvx --python 3.12 --from ... coarse-review --handoff
//          <handoff-url> --host claude|codex|gemini [--model ...]
//          [--effort ...]`
//   5. The user's local `coarse-review` command:
//        a. Fetches the bundle from /h/<token> as JSON
//        b. Downloads the raw PDF from the signed URL inside the bundle
//        c. Extracts locally with their OpenRouter key (from
//           ~/.coarse/config.toml or .env)
//        d. Runs the full coarse pipeline, routing every LLM call
//           through the chosen headless CLI
//        e. POSTs the rendered review back to /api/mcp-finalize with
//           the finalize_token
//        f. Prints `https://coarse.ink/review/<paper_id>?token=<t>` —
//           the user clicks it to see the review in the normal web UI.
//           The tokened URL form is required because /api/presign sets
//           `access_token_required=true` on every review row; the
//           mcp-finalize response embeds a signed token so the `view:`
//           line is clickable without any additional token grafting.
//
// No server-side extraction. No OpenRouter key on the web backend. The
// handoff URL is the only thing that crosses the browser→terminal
// boundary, and it's copy-pasted from a modal.

export type ChatHost = "claude-code" | "codex" | "gemini-cli";

export const HOST_LABELS: Record<ChatHost, string> = {
  "claude-code": "Claude Code",
  "codex": "Codex",
  "gemini-cli": "Gemini CLI",
};

export const HOST_GLYPHS: Record<ChatHost, string> = {
  "claude-code": "▶",
  "codex": "◐",
  "gemini-cli": "✦",
};

// Which coarse-review --host flag each ChatHost maps to.
export const HOST_CLI_NAME: Record<ChatHost, "claude" | "codex" | "gemini"> = {
  "claude-code": "claude",
  "codex": "codex",
  "gemini-cli": "gemini",
};

// Default models per host (user can override in the modal).
export const HOST_DEFAULT_MODELS: Record<ChatHost, string[]> = {
  "claude-code": ["claude-opus-4-6", "claude-sonnet-4-6", "claude-haiku-4-5"],
  "codex": ["gpt-5.4", "gpt-5.3-codex", "gpt-5.4-mini", "gpt-5.4-pro"],
  "gemini-cli": [
    "gemini-3.1-pro-preview",
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite-preview",
  ],
};

export const EFFORT_LEVELS = ["low", "medium", "high", "max"] as const;
export type EffortLevel = (typeof EFFORT_LEVELS)[number];

// uvx install specifier used by both `coarse install-skills` and the
// detached `coarse-review` launcher. Stable PyPI semver pin — the
// handoff flow does NOT need the `[mcp]` extra (fastmcp is only used
// by `coarse mcp-upload`, a separate command, and pymupdf4llm is only
// used when `COARSE_EXTRACTION_FAST=1`). Dropping the extra cuts the
// uvx install from ~114 packages to ~60 by removing fastmcp +
// pymupdf4llm and their ~40 transitive dependencies (mcp SDK, uvicorn,
// starlette, httpx-sse, sse-starlette, pydantic-settings,
// python-multipart, etc.). `install-skills` is pure stdlib.
//
// The variable is still called `DEFAULT_MCP_UVX_FROM` for backward
// compatibility with the `test_release_blocker_pin_is_coupled_to_unreleased_version`
// drift test that enforces the pin matches `__version__`.
const DEFAULT_MCP_UVX_FROM = "coarse-ink==1.3.0";

export function resolvePinnedUvFrom(): string {
  const raw = (process.env.NEXT_PUBLIC_COARSE_UVX_FROM ?? "").trim();
  if (!raw) return DEFAULT_MCP_UVX_FROM;
  // Allowlist for `NEXT_PUBLIC_COARSE_UVX_FROM` overrides. Accepts:
  //   1. Plain semver pin: `coarse-ink==1.3.0` (production default).
  //   2. `[mcp]` extra form for operators who want the MCP path.
  //   3. Commit-sha git ref for pinned dev testing.
  //   4. `@dev` or `@main` branch ref — self-updating Preview default,
  //      lets Vercel Preview always track HEAD of `dev` without having
  //      to rotate the env var on every push.
  // Branch refs are locked to `dev` and `main` only so a leaked env
  // var can't be pointed at an attacker-controlled fork.
  const exactVersion = /^coarse-ink(\[mcp\])?==[A-Za-z0-9.+-]+$/;
  const exactCommit =
    /^coarse-ink(\[mcp\])?\s*@\s*git\+https:\/\/github\.com\/Davidvandijcke\/coarse@[0-9a-f]{7,40}$/i;
  const exactBranch =
    /^coarse-ink(\[mcp\])?\s*@\s*git\+https:\/\/github\.com\/Davidvandijcke\/coarse@(dev|main)$/i;
  if (exactVersion.test(raw) || exactCommit.test(raw) || exactBranch.test(raw)) return raw;
  return DEFAULT_MCP_UVX_FROM;
}

export const MCP_UVX_FROM = resolvePinnedUvFrom();

function shellQuote(value: string): string {
  return `'${value.replace(/'/g, `'\\''`)}'`;
}

// Short install-guide URLs for users who don't have the chosen CLI yet.
export const HOST_INSTALL_URL: Record<ChatHost, string> = {
  "claude-code": "https://claude.ai/download",
  "codex": "https://github.com/openai/codex",
  "gemini-cli": "https://github.com/google-gemini/gemini-cli",
};

export const HOST_LAUNCH_LABEL: Record<ChatHost, string> = {
  "claude-code": "Try opening Claude Code desktop app",
  "codex": "Try opening Codex desktop app",
  "gemini-cli": "Open Gemini CLI",
};

export const HOST_LAUNCH_HINT: Record<ChatHost, string> = {
  "claude-code":
    "Only works if you have the Claude desktop app installed (not the terminal-only Claude Code CLI). If nothing happens, use the commands above.",
  "codex":
    "Only works if you have the Codex desktop app installed. If nothing happens, use the commands above.",
  "gemini-cli":
    "Copy the commands above and run them in your terminal.",
};

/**
 * Build the natural-language prompt the coding agent will execute.
 * Same text used in the codex://new?prompt=... deep link AND in the
 * code block users paste into Claude Code / Gemini CLI terminals.
 *
 * ``logFile`` is the per-review unique log path so parallel reviews in
 * the same terminal don't clobber each other and so the agent can
 * correlate a tail/rg invocation to a specific review. Derived from
 * the paper UUID by buildCliCommands.
 *
 * ``attachCmd`` is the new signal-driven wait command (``coarse-review
 * --attach <logFile>``) that replaces the old per-60s-tail polling
 * loop. It blocks in a single Bash invocation until the detached
 * review exits, streaming the log and emitting heartbeats every 30s
 * so Claude Code's Bash tool sees stdout activity. One agent-visible
 * Bash call covers the full 10-25min wait instead of 10-25 separate
 * per-poll approval prompts.
 */
export function buildAgentPrompt(args: {
  setupCmd: string;
  runCmd: string;
  attachCmd: string;
  logFile: string;
}): string {
  const { setupCmd, runCmd, attachCmd, logFile } = args;
  const configCmd = setupCmd.replace("coarse install-skills --all --force", "coarse setup");
  return (
    `Please review an academic paper for me using the coarse-review skill. ` +
    `The paper is a REMOTE resource — its source URL is already embedded ` +
    `in the command below. Do NOT search for a local PDF, do NOT ask me ` +
    `for a file path, and do NOT try to interpret the URL as a filename.\n\n` +
    `STEP 0 — Check whether \`uvx\` is available. Run ` +
    `\`command -v uvx || command -v uv\`. If neither command exists, ` +
    `install uv first with \`curl -LsSf https://astral.sh/uv/install.sh | sh\`, ` +
    `then run \`export PATH="$HOME/.local/bin:$PATH"\` in the current shell. ` +
    `coarse requires Python 3.12+, so if needed install it with ` +
    `\`uv python install 3.12\`. If \`uv\` exists but \`uvx\` does not, ` +
    `use \`uv tool run --python 3.12 --from ...\` ` +
    `wherever the steps below say \`uvx --python 3.12 --from ...\`. Do NOT get stuck on ` +
    `\`uvx: command not found\` or an older system Python.\n\n` +
    `STEP 1 — Refresh the coarse-review skill files. ` +
    `Run this command to copy the pinned coarse-review skill bundle into ` +
    `your Claude Code / Codex / Gemini CLI skill folder. This uses uvx, ` +
    `so it does not permanently install ` +
    `coarse-ink into your global environment. If the exact command below ` +
    `reports \`No such command 'install-skills'\`, that's a known ` +
    `version-skew and is safe to ignore — the review runs the same way ` +
    `either way because uvx is already loading the coarse bundle via ` +
    `\`--from\`.\n\n` +
    `${setupCmd}\n\n` +
    `STEP 2 — Check for an OpenRouter API key. ` +
    `Run \`echo $OPENROUTER_API_KEY\` and \`grep OPENROUTER_API_KEY .env 2>/dev/null\`. ` +
    `If neither shows a key, tell me:\n\n` +
    `  "I need an OpenRouter API key for the Mistral OCR extraction step ` +
    `(~$0.10 per paper). You have three options:\n` +
    `   1. Get a key at https://openrouter.ai/settings/keys and paste it ` +
    `here — I'll save it to ~/.coarse/config.toml for you with:\n` +
    `      ${configCmd}\n` +
    `   2. Set it yourself: export OPENROUTER_API_KEY=sk-or-v1-... in your ` +
    `shell, then re-ask me.\n` +
    `   3. If you explicitly prefer project-local storage, add it to a ` +
    `.env file in your current directory: OPENROUTER_API_KEY=sk-or-v1-...\n` +
    `   Which would you like?"\n\n` +
    `If I paste a key (it should start with sk-or-), save it to ` +
    `~/.coarse/config.toml via \`${configCmd}\` unless I explicitly ask ` +
    `for project-local .env storage.\n\n` +
    `STEP 3 — Launch the detached review. Run the EXACT command below, ` +
    `verbatim. Do not substitute, rewrite, or interpret any argument — ` +
    `every piece is already filled in. The \`--handoff\` URL is the ` +
    `paper source; coarse-review downloads the paper from that URL ` +
    `over the network at the start of the pipeline. You do NOT need ` +
    `to, and MUST NOT, search the filesystem (no \`find\`, no ` +
    `\`glob\`, no \`ls /tmp\`, no \`FindFiles\`) for a local paper, ` +
    `and you do NOT need to ask me for a paper path. This command ` +
    `returns immediately (within 2 seconds) after printing ` +
    `\`Review PID: <N>\` and \`Log file: ${logFile}\`. Run it:\n\n` +
    `  ${runCmd}\n\n` +
    `STEP 4 — Wait for the review to finish with a single blocking ` +
    `bash call. The review takes 10-25 minutes end-to-end. Instead of ` +
    `polling \`tail\` every 60 seconds (which generates one permission ` +
    `prompt per poll), use coarse-review's built-in \`--attach\` ` +
    `watcher, which blocks in a single command until the worker ` +
    `exits:\n\n` +
    `  ${attachCmd}\n\n` +
    `The attach command streams the log to stdout as it's written and ` +
    `prints a \`[attach] pid=<N> elapsed=<mm:ss> — waiting…\` heartbeat ` +
    `every 30 seconds of log idleness so the bash tool sees stdout ` +
    `activity and doesn't think the command is hung. It exits ` +
    `automatically when the review process exits. IMPORTANT: run it ` +
    `with a long bash-tool timeout — at least **2700000 ms (45 min)** ` +
    `in Claude Code's \`Bash\` tool via the \`timeout\` parameter, ` +
    `\`--timeout 2700\` in Codex, or the equivalent in Gemini CLI. ` +
    `The 45-minute recommendation leaves ~20 minutes of margin on top ` +
    `of the 10-25 minute review runtime for cold starts, slow models, ` +
    `very long papers, and \`--effort max\` runs. 30 minutes used to ` +
    `be the recommendation and it was tight — every agent's tool ` +
    `timeout is a wall clock, not an idle-stream cap, so a 25-minute ` +
    `review with a 30-minute cap leaves only 5 minutes of safety ` +
    `margin. Bump to 60 minutes if you're reviewing a book-length ` +
    `paper or you've picked the largest model. Do NOT re-run the ` +
    `\`--detach\` command from STEP 3 if the attach call returns ` +
    `early — that would spawn a second worker against the same ` +
    `handoff URL. If attach exits because the bash tool timed out ` +
    `(not because the review finished), just re-run the EXACT same ` +
    `attach command again — it's idempotent and will re-attach to ` +
    `the same running worker.\n\n` +
    `Attach exit codes tell you what happened:\n` +
    `  - 0 — review completed successfully, \`view:\` + \`local:\` ` +
    `lines are in the log\n` +
    `  - 1 — review reported a failure marker; show me the error from ` +
    `the log\n` +
    `  - 2 — review process died without a completion marker (silent ` +
    `crash); show me the last 50 log lines so I can diagnose\n` +
    `  - 3 — pidfile missing (launcher never started); re-run STEP 3\n` +
    `  - 124 — attach's own 30-min timeout tripped (very unusual); ` +
    `re-run the attach command to continue waiting\n\n` +
    `STEP 5 — When attach exits with code 0, read the completion ` +
    `footer from the log. Run \`rg '^  view:|^  local:' ${logFile}\`. ` +
    `The \`local:\` line is the exact markdown path written by ` +
    `coarse-review. If \`view:\` is present, it's the canonical web ` +
    `URL and already includes the signed access token — use it ` +
    `as-is. If the log says \`view: unavailable\`, report that the ` +
    `web callback failed and use only the \`local:\` path. Do NOT ` +
    `try to discover another web URL, and do NOT run broad ` +
    `\`find\`, \`locate\`, or \`lsof\` searches trying to rediscover ` +
    `the review file.\n\n` +
    `Note: this runs locally on my machine using my own Claude Code, ` +
    `Codex, or Gemini CLI account. coarse.ink does not receive or ` +
    `store my provider login, and my provider's terms, limits, and ` +
    `policies apply.\n\n` +
    `When attach has exited cleanly (code 0) and you've read the ` +
    `completion footer, show me:\n` +
    `  - The review URL (the \`view:\` line) — render it as a ` +
    `clickable markdown link like \`[Open review](\${viewUrl})\` so ` +
    `I can click it in the chat instead of copy-pasting. If the ` +
    `terminal environment and my platform clearly support it, also ` +
    `offer (don't execute without asking) to open the URL in my ` +
    `default browser — \`open "\${viewUrl}"\` on macOS, ` +
    `\`xdg-open "\${viewUrl}"\` on Linux, \`start "" "\${viewUrl}"\` ` +
    `on Windows. Skip the offer entirely in cloud sandbox sessions ` +
    `where there is no graphical display.\n` +
    `  - The local markdown path (the \`local:\` line)\n` +
    `  - A summary of the recommendation (accept / revise / reject)\n` +
    `  - The top 3 macro issues from the overview section`
  );
}

/**
 * Build the best available launch URL for each host.
 *
 * - **Codex**: ``codex://new?prompt=<text>`` deep link with pre-filled
 *   prompt — the user just clicks "send" in the Codex app.
 *   (See https://developers.openai.com/codex/app/commands)
 * - **Claude Code**: ``claude://`` opens the app but has NO prompt
 *   parameter (feature requested, not shipped). Clipboard fallback.
 * - **Gemini CLI**: ``gemini2://`` opens the app but has NO prompt
 *   parameter documented. Clipboard fallback.
 */
export function buildLaunchUrl(args: {
  host: ChatHost;
  runCmd: string;
  setupCmd: string;
  attachCmd: string;
  logFile: string;
}): string {
  const { host, runCmd, setupCmd, attachCmd, logFile } = args;
  const prompt = buildAgentPrompt({ setupCmd, runCmd, attachCmd, logFile });

  if (host === "codex") {
    // Codex supports codex://new?prompt=<text> deep links that pre-fill
    // the composer in the desktop app.
    return `codex://new?prompt=${encodeURIComponent(prompt)}`;
  }
  // Claude Code and Gemini CLI don't support prompt params in their
  // URL schemes. Open the app (claude://) and rely on clipboard, or
  // for Gemini show manual instructions only.
  if (host === "claude-code") return "claude://";
  return "";
}

/**
 * Handoff bundle returned by POST /api/cli-handoff. The frontend uses
 * this to render the copy-paste modal.
 */
export interface CliHandoffBundle {
  token: string;
  paper_id: string;
  handoff_url: string;
  host: ChatHost | null;
  finalize_token_ttl_minutes: number;
}

/**
 * POST /api/cli-handoff — mints a finalize token bound to a paper_id.
 * Takes no OpenRouter key and does not trigger server-side extraction.
 */
export async function mintCliHandoff(
  paperId: string,
  host: ChatHost,
  handoffSecret: string,
): Promise<CliHandoffBundle> {
  const resp = await fetch("/api/cli-handoff", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ paper_id: paperId, host, handoff_secret: handoffSecret }),
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ error: "Unknown error" }));
    throw new Error(err.error ?? `cli-handoff failed with HTTP ${resp.status}`);
  }
  return (await resp.json()) as CliHandoffBundle;
}

/**
 * Shared return shape for both `buildCliCommands` (browser React path
 * with host/model/effort already chosen) and `buildHandoffLandingCommands`
 * (server-side `/h/[token]/route.ts` HTML landing page that lets the
 * user edit the command before running).
 */
export interface HandoffCliCommands {
  setupCmd: string;
  runCmd: string;
  attachCmd: string;
  logFile: string;
}

/**
 * Build the core per-review handoff commands that are **host-agnostic**
 * (no --host/--model/--effort appended). Used by the `/h/[token]`
 * landing-page HTML renderer, which wants to show the user a command
 * they can edit themselves to add host/model/effort flags rather than
 * having them pre-baked by whatever modal host was selected in the
 * browser.
 *
 * Shared with `buildCliCommands` below so the two surfaces can't
 * drift — same uvx pin, same log-file scheme, same attach command,
 * same shell-quoting rules.
 *
 * The log file is derived from ``paperId`` so parallel reviews
 * launched from the same shell (or stacked attempts against the same
 * handoff) don't clobber each other's output. The format is
 * ``/tmp/coarse-review-<paperId>.log`` — just the UUID, not the full
 * tokened review key, because ``ps aux`` and ``/tmp`` listings are
 * the wrong place for an access token.
 */
export function buildHandoffLandingCommands(args: {
  handoffUrl: string;
  paperId: string;
}): HandoffCliCommands {
  const { handoffUrl, paperId } = args;
  const quotedUvFrom = shellQuote(MCP_UVX_FROM);
  const logFile = `/tmp/coarse-review-${paperId}.log`;
  // The handoff URL MUST be single-quoted in the shell. After the
  // Vercel Deployment Protection bypass landed in #121, the URL can
  // contain `?x-vercel-protection-bypass=<secret>&x-vercel-set-bypass-cookie=true`
  // — and that unquoted `&` makes the shell background the first
  // part of the command, so `coarse-review --handoff <first-part>`
  // runs immediately against a truncated URL (→ 404 or 401 because
  // the bypass token is gone) and `x-vercel-set-bypass-cookie=true`
  // runs as a foreground "command" that fails with "command not
  // found". Paste-in-terminal users hit this the moment bypass was
  // configured on preview. The uvx pin and the log file are wrapped
  // in single quotes for the same reason — defence-in-depth against
  // future additions to either value (e.g. a paper_id with shell
  // metacharacters, or a pinned version string that gains a `&`).
  const quotedHandoffUrl = shellQuote(handoffUrl);
  const quotedLogFile = shellQuote(logFile);
  const setupCmd = `uvx --python 3.12 --from ${quotedUvFrom} coarse install-skills --all --force`;
  const runCmd = `uvx --python 3.12 --from ${quotedUvFrom} coarse-review --detach --log-file ${quotedLogFile} --handoff ${quotedHandoffUrl}`;
  // Single blocking watch command that replaces the legacy per-60s
  // tail polling loop. See buildAgentPrompt STEP 4 and the
  // _run_attach docstring in src/coarse/cli_review.py for the full
  // contract (heartbeats, pidfile discovery, exit codes 0/1/2/3/124/130).
  const attachCmd = `uvx --python 3.12 --from ${quotedUvFrom} coarse-review --attach ${quotedLogFile}`;
  return { setupCmd, runCmd, attachCmd, logFile };
}

/**
 * Build the two shell commands the user needs to paste into their
 * terminal. The setup command is idempotent; the run command includes
 * whatever model/effort overrides the user selected in the modal.
 *
 * Layered on top of `buildHandoffLandingCommands` — the host-agnostic
 * base commands, then the host/model/effort flags appended to the run
 * command.
 */
export function buildCliCommands(args: {
  handoffUrl: string;
  host: ChatHost;
  model: string;
  effort: EffortLevel;
  paperId: string;
}): HandoffCliCommands {
  const { handoffUrl, host, model, effort, paperId } = args;
  const cliName = HOST_CLI_NAME[host];
  const base = buildHandoffLandingCommands({ handoffUrl, paperId });
  const runCmd = `${base.runCmd} --host ${cliName} --model ${model} --effort ${effort}`;
  return { ...base, runCmd };
}
