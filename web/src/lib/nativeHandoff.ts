import { languageName } from "@/lib/languages";
import { MCP_UVX_FROM, type ChatHost } from "@/lib/mcpHandoff";

const quote = (value: string) => `'${value.replace(/'/g, `'\\''`)}'`;

export function nativePilotAvailable(host: ChatHost, deepLiteratureSearch = false): boolean {
  return process.env.NEXT_PUBLIC_NATIVE_REVIEW_PILOT === "1" &&
    (host === "codex" || host === "claude-code") && !deepLiteratureSearch;
}

export function buildNativePrompt(args: {
  handoffUrl: string;
  paperId: string;
  host: ChatHost;
  reviewLanguage?: string;
  authorNotes?: string;
}): string {
  if (args.host === "gemini-cli") throw new Error("Native pilot supports Codex and Claude Code");
  const host = args.host === "codex" ? "codex" : "claude";
  const runner = `uvx --python 3.12 --from ${quote(MCP_UVX_FROM)} coarse-native`;
  const workspace = quote(`.coarse-native/${args.paperId}`);
  const language = languageName(args.reviewLanguage);
  const languageArg = language ? ` --language ${quote(language)}` : "";
  const notesArg = args.authorNotes ? ` --author-notes ${quote(args.authorNotes)}` : "";
  return `Review this paper with the Coarse native app pilot. Use native subagents in this app ` +
    `for review reasoning, inheriting my current app model and reasoning settings. ` +
    `Use Coarse only for preparation, checkpoint validation, and publication.\n\n` +
    `Check that uvx is available; use uv tool run if uv is installed without uvx. ` +
    `Install the native skill alongside the existing headless skill:\n\n` +
    `\`\`\`sh\n${runner} install-skill --host ${host}\n\`\`\`\n\n` +
    `Read the SKILL.md path returned by that command and follow it in this conversation. ` +
    `If the app cannot run native subagents, report that limitation. ` +
    `Do not launch codex exec, claude -p, or the headless coarse-review runner.\n\n` +
    `Prepare the remote paper using this exact runner prefix:\n\n` +
    `\`\`\`sh\n${runner} prepare --handoff ${quote(args.handoffUrl)} --host ${host} ` +
    `--workspace ${workspace}${languageArg}${notesArg}\n\`\`\`\n\n` +
    `The handoff argument is a bare URL inside shell quotes. Remove any Markdown link ` +
    `presentation wrapper without changing its destination or query parameters; this formatting ` +
    `correction is authorized. PDF extraction uses the existing configured OCR key, or supplied ` +
    `pre-extracted Markdown. Never print credentials.\n\n` +
    `After preparation, use its returned runner_prefix for next, submit, status, and publish. ` +
    `Resume the returned workspace if interrupted. Delegate independent pending tasks to native ` +
    `subagents, validate every returned JSON response with submit, and repeat next until ready. ` +
    `The skill defines the complete protocol and publication rules. Publish the validated review ` +
    `back to this website and show me its confirmed URL.`;
}

export function nativeLaunchUrl(host: ChatHost, prompt: string): string {
  if (host === "codex") return `codex://new?prompt=${encodeURIComponent(prompt)}`;
  if (host === "claude-code") return "claude://";
  throw new Error("Native pilot supports Codex and Claude Code");
}
