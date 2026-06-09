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
  base: string;
  /** URL query param that prefills the composer, or null if unsupported. We
   * can't paste into a cross-origin page's input, so this service-side param
   * is the only way to prefill; clipboard is the fallback when it's null. */
  promptParam: string | null;
}

export const AI_SERVICES: AiService[] = [
  { key: "claude", label: "Claude", base: "https://claude.ai/new", promptParam: "q" },
  { key: "chatgpt", label: "ChatGPT", base: "https://chatgpt.com/", promptParam: "q" },
  { key: "grok", label: "Grok", base: "https://grok.com/", promptParam: "q" },
  // Gemini / DeepSeek have no native URL prefill — open clean, rely on clipboard.
  { key: "gemini", label: "Gemini", base: "https://gemini.google.com/app", promptParam: null },
  { key: "deepseek", label: "DeepSeek", base: "https://chat.deepseek.com/", promptParam: null },
];

// Phrased to stay sensible even if a service auto-submits the prefilled prompt
// before the file is attached (e.g. ChatGPT's ?q=).
export const HANDOFF_KICKOFF_PROMPT =
  'I\'m sharing a research paper plus an automated peer review of it (by a tool called "coarse") ' +
  "as an attached markdown file. Act as an expert referee: help me judge which review comments are " +
  "actually correct — be willing to say a comment is wrong or overstated — and how I should revise. " +
  "I'll attach the file next; if you don't see it yet, just ask me for it.";

/** Build the URL to open, prefilling the prompt via the service's query param
 * when it supports one. */
export function serviceUrl(service: AiService, prompt: string): string {
  if (!service.promptParam) return service.base;
  const sep = service.base.includes("?") ? "&" : "?";
  return `${service.base}${sep}${service.promptParam}=${encodeURIComponent(prompt)}`;
}

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

  // Always copy the kickoff prompt as the universal fallback (and for the
  // services whose URL can't prefill it).
  navigator.clipboard?.writeText(HANDOFF_KICKOFF_PROMPT).catch(() => {});

  window.open(serviceUrl(service, HANDOFF_KICKOFF_PROMPT), "_blank", "noopener,noreferrer");
}
