// "Discuss with your AI subscription" handoff.
//
// These external chat services (Claude, ChatGPT, Gemini, Grok, DeepSeek) have no
// public API to start a chat with attachments for an arbitrary third party, so
// the handoff bundles the paper + review + structured JSON into one markdown
// file the user downloads and attaches in their own chat, then opens the
// service. Lets people keep chatting on a subscription they already pay for
// instead of per-token via OpenRouter.

import type { ReviewJson } from "./types";

export interface AiService {
  key: string;
  label: string;
  url: string;
}

export const AI_SERVICES: AiService[] = [
  { key: "claude", label: "Claude", url: "https://claude.ai/new" },
  { key: "chatgpt", label: "ChatGPT", url: "https://chatgpt.com/" },
  { key: "gemini", label: "Gemini", url: "https://gemini.google.com/app" },
  { key: "grok", label: "Grok", url: "https://grok.com/" },
  { key: "deepseek", label: "DeepSeek", url: "https://chat.deepseek.com/" },
];

export const HANDOFF_KICKOFF_PROMPT =
  'I\'ve attached a research paper, an automated peer review of it (by a tool called "coarse"), ' +
  "and the structured review data. Act as an expert referee: help me understand the review, judge " +
  "which comments are actually correct (be willing to say a comment is wrong or overstated), and " +
  "figure out how to revise. Start by summarizing the most important issues.";

export interface HandoffArgs {
  paperTitle?: string | null;
  paperMarkdown?: string | null;
  resultMarkdown?: string | null;
  resultJson?: ReviewJson | null;
}

/** Build the single markdown file bundling paper + review + structured JSON. */
export function buildHandoffMarkdown({
  paperTitle,
  paperMarkdown,
  resultMarkdown,
  resultJson,
}: HandoffArgs): string {
  const lines: string[] = [
    `# Discuss the coarse review of "${paperTitle || "this paper"}"`,
    "",
    HANDOFF_KICKOFF_PROMPT,
    "",
    "This file bundles three things: the paper, the automated review, and (when available) the structured review data.",
    "",
    "---",
    "",
    "## 1. Paper (OCR-extracted markdown)",
    "",
    paperMarkdown?.trim() || "(The paper text was not stored for this review.)",
    "",
    "---",
    "",
    "## 2. Coarse review",
    "",
    resultMarkdown?.trim() || "(No review markdown.)",
  ];
  if (resultJson) {
    lines.push(
      "",
      "---",
      "",
      "## 3. Structured review data (JSON)",
      "",
      "```json",
      JSON.stringify(resultJson, null, 2),
      "```",
    );
  }
  return lines.join("\n");
}

/** Download the bundle, copy the kickoff prompt, and open the chosen service. */
export function startAiHandoff(service: AiService, reviewId: string, args: HandoffArgs): void {
  const md = buildHandoffMarkdown(args);
  const blob = new Blob([md], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `coarse_${reviewId}_context.md`;
  a.click();
  URL.revokeObjectURL(url);

  // Best-effort: copy a kickoff prompt so the user can just paste.
  navigator.clipboard?.writeText(HANDOFF_KICKOFF_PROMPT).catch(() => {});

  window.open(service.url, "_blank", "noopener,noreferrer");
}
