// Browser-side OpenRouter chat for the per-comment "Discuss" feature.
//
// The user's OpenRouter key lives only in sessionStorage (see openrouterAuth.ts)
// and is streamed directly from the browser to OpenRouter — it never touches our
// servers. This module holds the pure pieces: the system-prompt builder, the SSE
// streaming transport, and the tab-scoped persistence we use to survive the
// OpenRouter OAuth redirect (a full page navigation).

import type { DetailedComment } from "./parseReview";

const OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions";

export interface ChatMessage {
  role: "system" | "user" | "assistant";
  content: string;
}

/** Thrown when OpenRouter rejects the key (401) so the UI can re-prompt login. */
export class OpenRouterAuthError extends Error {
  constructor(message = "OpenRouter rejected the API key") {
    super(message);
    this.name = "OpenRouterAuthError";
  }
}

/** Thrown for any other OpenRouter / network failure. */
export class OpenRouterChatError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "OpenRouterChatError";
  }
}

export interface BuildSystemPromptArgs {
  paperTitle: string;
  paperMarkdown?: string | null;
  domain?: string | null;
  overallFeedbackText: string;
  comment: DetailedComment;
}

/**
 * Build the system prompt that grounds the chat in the whole paper, the overall
 * review, and the one comment under discussion. Because the pipeline's literal
 * per-comment reasoning is not persisted, the prompt instructs the model to
 * reconstruct it AND to be willing to conclude the comment is wrong rather than
 * manufacture authority (guards against the pipeline's confident-but-wrong
 * failure mode).
 */
export function buildChatSystemPrompt({
  paperTitle,
  paperMarkdown,
  domain,
  overallFeedbackText,
  comment,
}: BuildSystemPromptArgs): string {
  const paperBlock = paperMarkdown?.trim()
    ? paperMarkdown.trim()
    : "(The full paper text is unavailable for this review. Work from the quoted passage and feedback below.)";
  const overallBlock = overallFeedbackText.trim() || "(No overall feedback was recorded.)";

  const lines: string[] = [
    'You are an expert academic peer reviewer helping the AUTHOR of a paper engage with ONE specific comment that an automated reviewer (a tool called "coarse") produced about their paper.',
    "",
    "Your job is to help the author understand the comment, judge whether it is actually correct, and decide how to respond or revise.",
    "",
    "How to treat the comment:",
    "- You do NOT have the automated reviewer's literal step-by-step reasoning; it was not recorded. Reconstruct the most plausible reasoning from the paper text and the comment itself, and flag when you are inferring rather than certain.",
    "- The automated reviewer is fallible. It sometimes produces confident-sounding critiques that are wrong, overstated, or based on a misreading. Do NOT assume the comment is correct.",
    "- If the paper does not support the comment, say so plainly and explain why. If the comment is right, help the author fix it concretely. Never manufacture authority or depth that isn't grounded in the actual paper text.",
    "- Quote the paper when it helps. Be concise, specific, and honest.",
    "",
    `Paper title: ${paperTitle || "(untitled)"}`,
  ];
  if (domain) lines.push(`Domain: ${domain}`);
  lines.push(
    "",
    "=== FULL PAPER (markdown) ===",
    paperBlock,
    "=== END PAPER ===",
    "",
    "=== OVERALL REVIEW FEEDBACK ===",
    overallBlock,
    "=== END OVERALL FEEDBACK ===",
    "",
    "=== THE COMMENT UNDER DISCUSSION ===",
    `Title: ${comment.title}`,
    "Quoted passage from the paper:",
    '"""',
    comment.quote || "(no quote provided)",
    '"""',
    "Reviewer's feedback on that passage:",
    '"""',
    comment.feedback || "(no feedback body)",
    '"""',
    "=== END COMMENT ===",
    "",
    "Answer the author's questions about THIS comment.",
  );
  return lines.join("\n");
}

interface OpenRouterStreamChunk {
  choices?: Array<{ delta?: { content?: string } }>;
  error?: { message?: string };
}

async function safeErrorDetail(res: Response): Promise<string> {
  try {
    const data = (await res.json()) as { error?: { message?: string } };
    return data?.error?.message ?? "";
  } catch {
    return "";
  }
}

export interface StreamChatArgs {
  apiKey: string;
  model: string;
  messages: ChatMessage[];
  signal?: AbortSignal;
}

/**
 * Stream a chat completion straight from the browser to OpenRouter, yielding
 * content deltas as they arrive. Aborting the signal ends the generator
 * cleanly. `temperature` is intentionally omitted — some reasoning models 400
 * when it is supplied (same rationale as models.py::supports_temperature).
 */
export async function* streamChatCompletion({
  apiKey,
  model,
  messages,
  signal,
}: StreamChatArgs): AsyncGenerator<string, void, unknown> {
  let res: Response;
  try {
    res = await fetch(OPENROUTER_CHAT_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
        ...(typeof window !== "undefined"
          ? { "HTTP-Referer": window.location.origin, "X-Title": "coarse" }
          : {}),
      },
      body: JSON.stringify({ model, messages, stream: true }),
      signal,
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") return;
    throw new OpenRouterChatError(
      err instanceof Error ? err.message : "Network error contacting OpenRouter",
    );
  }

  if (res.status === 401) throw new OpenRouterAuthError();
  if (!res.ok || !res.body) {
    const detail = await safeErrorDetail(res);
    throw new OpenRouterChatError(detail || `OpenRouter request failed (${res.status})`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      let newlineIndex: number;
      while ((newlineIndex = buffer.indexOf("\n")) !== -1) {
        const line = buffer.slice(0, newlineIndex).trim();
        buffer = buffer.slice(newlineIndex + 1);
        // Skip blanks and SSE keep-alive comments (": OPENROUTER PROCESSING").
        if (!line || line.startsWith(":")) continue;
        if (!line.startsWith("data:")) continue;
        const data = line.slice(5).trim();
        if (data === "[DONE]") return;
        let parsed: OpenRouterStreamChunk;
        try {
          parsed = JSON.parse(data) as OpenRouterStreamChunk;
        } catch {
          continue; // ignore partial / non-JSON fragments
        }
        if (parsed.error) {
          throw new OpenRouterChatError(parsed.error.message || "OpenRouter stream error");
        }
        const delta = parsed.choices?.[0]?.delta?.content;
        if (delta) yield delta;
      }
    }
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") return;
    throw err;
  } finally {
    try {
      reader.releaseLock();
    } catch {
      /* already released */
    }
  }
}

// --- Tab-scoped chat persistence -------------------------------------------
//
// Persist only enough to survive the OpenRouter OAuth redirect: which comment's
// chat was open and its messages. sessionStorage is tab-scoped and clears on tab
// close, matching the key's lifetime.

export interface PersistedChat {
  commentNumber: number;
  messages: ChatMessage[];
}

function chatStorageKey(reviewId: string): string {
  return `coarse-chat-${reviewId}`;
}

export function loadPersistedChat(reviewId: string): PersistedChat | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.sessionStorage.getItem(chatStorageKey(reviewId));
    if (!raw) return null;
    const parsed = JSON.parse(raw) as PersistedChat;
    if (parsed && typeof parsed.commentNumber === "number" && Array.isArray(parsed.messages)) {
      return parsed;
    }
    return null;
  } catch {
    return null;
  }
}

export function savePersistedChat(reviewId: string, chat: PersistedChat): void {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.setItem(chatStorageKey(reviewId), JSON.stringify(chat));
  } catch {
    /* sessionStorage full / unavailable — non-fatal */
  }
}

export function clearPersistedChat(reviewId: string): void {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.removeItem(chatStorageKey(reviewId));
  } catch {
    /* noop */
  }
}
