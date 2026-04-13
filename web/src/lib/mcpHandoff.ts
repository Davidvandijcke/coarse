// Handoff helpers for the "Review with my subscription" button on the
// coarse web form. The flow is:
//
//   1. User uploads PDF via /api/presign + direct Supabase Storage PUT
//      (same path as the regular OpenRouter review — no extraction
//      triggered).
//   2. User clicks "Review with Claude Code / Codex / Gemini CLI".
//   3. Frontend POSTs to /api/cli-handoff which mints a short-lived
//      finalize_token (60 min) bound to the paper_id and returns a
//      handoff URL of the form ``coarse.vercel.app/h/<token>``.
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
//        f. Prints `https://coarse.vercel.app/review/<paper_id>` —
//           the user clicks it to see the review in the normal web UI.
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

const DEFAULT_MCP_UVX_FROM = "coarse-ink[mcp]==1.2.2";

export function resolvePinnedUvFrom(): string {
  const raw = (process.env.NEXT_PUBLIC_COARSE_UVX_FROM ?? "").trim();
  if (!raw) return DEFAULT_MCP_UVX_FROM;
  const exactVersion = /^coarse-ink\[mcp\]==[A-Za-z0-9.+-]+$/;
  const exactCommit =
    /^coarse-ink\[mcp\]\s*@\s*git\+https:\/\/github\.com\/Davidvandijcke\/coarse@[0-9a-f]{7,40}$/i;
  if (exactVersion.test(raw) || exactCommit.test(raw)) return raw;
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
  "claude-code": "Open Claude Code",
  "codex": "Open Codex",
  "gemini-cli": "Open Gemini CLI",
};

export const HOST_LAUNCH_HINT: Record<ChatHost, string> = {
  "claude-code":
    "Opens Claude Code and copies the review command to your clipboard. Paste it (⌘V) and hit send.",
  "codex":
    "Opens Codex with the review command pre-filled. Just hit send.",
  "gemini-cli":
    "Copy the commands below and run them in your terminal.",
};

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
/**
 * Build the natural-language prompt the coding agent will execute.
 * Same text used in the codex://new?prompt=... deep link AND in the
 * code block users paste into Claude Code / Gemini CLI terminals.
 */
export function buildAgentPrompt(args: {
  setupCmd: string;
  runCmd: string;
}): string {
  const { setupCmd, runCmd } = args;
  const configCmd = setupCmd.replace("coarse install-skills --all --force", "coarse setup");
  return (
    `Please review an academic paper for me using the coarse-review skill.\n\n` +
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
    `coarse-ink into your global environment:\n\n` +
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
    `STEP 3 — Start the review with coarse-review's built-in detached ` +
    `launcher. The review takes 10-25 minutes, which exceeds most agent ` +
    `tool timeouts, so use this exact command:\n\n` +
    `  ${runCmd}\n\n` +
    `This command returns immediately with the Review PID and writes all ` +
    `output to \`/tmp/coarse-review.log\`.\n\n` +
    `Then poll the log file every 60-90 seconds with ` +
    `\`tail -20 /tmp/coarse-review.log\` to check progress. Do NOT ` +
    `re-run the command in the foreground. Do NOT kill the process because ` +
    `you think it hung; it takes a genuine 10-25 minutes.\n\n` +
    `STEP 4 — When the run finishes, use ONLY the final log lines to ` +
    `locate the artifacts. Do NOT do a broad filesystem search. ` +
    `Run \`rg '^  view:|^  local:' /tmp/coarse-review.log\`. ` +
    `The \`local:\` line is the exact markdown path written by ` +
    `coarse-review, even when uvx runs from a temporary directory. ` +
    `If \`local:\` is present, read that file directly. If \`view:\` is ` +
    `present, use that as the canonical web URL. If the log says ` +
    `\`view: unavailable\`, report that the web callback failed and use ` +
    `only the \`local:\` path. Do NOT try to discover another web URL. ` +
    `Do NOT run global ` +
    `\`find\`, \`locate\`, \`lsof\`, or whole-computer searches trying to ` +
    `discover the review file.\n\n` +
    `Note: this runs locally on my machine using my own Claude Code, ` +
    `Codex, or Gemini CLI account. coarse.ink does not receive or store ` +
    `my provider login, and my provider's terms, limits, and policies ` +
    `apply.\n\n` +
    `When the log shows "PUBLISHED TO COARSE WEB" or "REVIEW ` +
    `COMPLETE", the review is done. Show me:\n` +
    `  - The review URL (search for 'view:' in the log)\n` +
    `  - The local markdown path (search for 'local:' in the log)\n` +
    `  - A summary of the recommendation (accept / revise / reject)\n` +
    `  - The top 3 macro issues from the overview section`
  );
}

export function buildLaunchUrl(args: {
  host: ChatHost;
  runCmd: string;
  setupCmd: string;
}): string {
  const { host, runCmd, setupCmd } = args;
  const prompt = buildAgentPrompt({ setupCmd, runCmd });

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

// Public URL of the coarse MCP server (legacy — only used by /mcp
// landing page for users who want the older Claude.ai connector path).
// Kept as an exported constant so the /mcp page still renders; the new
// CLI handoff flow doesn't reference it.
export const MCP_SERVER_URL =
  process.env.NEXT_PUBLIC_MCP_SERVER_URL ?? "https://coarse.vercel.app/mcp";

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
 * Build the two shell commands the user needs to paste into their
 * terminal. The setup command is idempotent; the run command includes
 * whatever model/effort overrides the user selected in the modal.
 */
export function buildCliCommands(args: {
  handoffUrl: string;
  host: ChatHost;
  model: string;
  effort: EffortLevel;
}): { setupCmd: string; runCmd: string } {
  const { handoffUrl, host, model, effort } = args;
  const cliName = HOST_CLI_NAME[host];
  const quotedUvFrom = shellQuote(MCP_UVX_FROM);
  const setupCmd = `uvx --python 3.12 --from ${quotedUvFrom} coarse install-skills --all --force`;
  const runCmd =
    `uvx --python 3.12 --from ${quotedUvFrom} coarse-review --detach --log-file /tmp/coarse-review.log --handoff ${handoffUrl}` +
    ` --host ${cliName}` +
    ` --model ${model}` +
    ` --effort ${effort}`;
  return { setupCmd, runCmd };
}
