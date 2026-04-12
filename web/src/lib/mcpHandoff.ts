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
//        - one-time setup: `pipx install coarse-ink[mcp] && coarse
//          setup && coarse install-skills`
//        - the review: `coarse-review --handoff <handoff-url> --host
//          claude|codex|gemini [--model ...] [--effort ...]`
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
  "codex": ["gpt-5-codex", "gpt-5", "gpt-5.1", "gpt-5-codex-mini"],
  "gemini-cli": ["gemini-3-pro", "gemini-3-flash", "gemini-2.5-pro"],
};

export const EFFORT_LEVELS = ["low", "medium", "high", "max"] as const;
export type EffortLevel = (typeof EFFORT_LEVELS)[number];

// Short install-guide URLs for users who don't have the chosen CLI yet.
export const HOST_INSTALL_URL: Record<ChatHost, string> = {
  "claude-code": "https://claude.ai/download",
  "codex": "https://github.com/openai/codex",
  "gemini-cli": "https://github.com/google-gemini/gemini-cli",
};

// Desktop-app deep-link URL and web fallback for each host. The
// launch flow tries the desktop-app scheme first (which opens the
// native app on macOS/Windows if installed); on platforms that don't
// support custom URL schemes the browser ignores the open() silently
// and we just rely on the clipboard copy.
export const HOST_APP_URL: Record<ChatHost, string> = {
  "claude-code": "claude://",
  "codex": "codex://",
  "gemini-cli": "gemini2://",
};

export const HOST_WEB_FALLBACK: Record<ChatHost, string | null> = {
  "claude-code": "https://claude.ai/new",
  "codex": "https://chatgpt.com/codex",
  "gemini-cli": null,
};

export const HOST_LAUNCH_LABEL: Record<ChatHost, string> = {
  "claude-code": "Open Claude Code",
  "codex": "Open Codex",
  "gemini-cli": "Open Gemini CLI",
};

export const HOST_LAUNCH_HINT: Record<ChatHost, string> = {
  "claude-code":
    "Opens the Claude Code app (or web) with the review command copied to your clipboard. Paste it and Claude will run the full review.",
  "codex":
    "Opens the Codex app (or web) with the review command copied to your clipboard. Paste it and Codex will run the full review.",
  "gemini-cli":
    "Opens the Gemini app with the review command copied to your clipboard. Paste it and Gemini will run the full review.",
};

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
): Promise<CliHandoffBundle> {
  const resp = await fetch("/api/cli-handoff", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ paper_id: paperId, host }),
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
  const setupCmd = "pipx install 'coarse-ink[mcp]' && coarse setup && coarse install-skills";
  const runCmd =
    `coarse-review --handoff ${handoffUrl}` +
    ` --host ${cliName}` +
    ` --model ${model}` +
    ` --effort ${effort}`;
  return { setupCmd, runCmd };
}
