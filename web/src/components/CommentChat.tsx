"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import type { DetailedComment } from "@/lib/parseReview";
import { preprocessLatex } from "@/lib/preprocessLatex";
import ModelPicker from "@/components/ModelPicker";
import OpenRouterLoginButton from "@/components/OpenRouterLoginButton";
import {
  buildChatSystemPrompt,
  clearPersistedChat,
  OpenRouterAuthError,
  savePersistedChat,
  streamChatCompletion,
  type ChatMessage,
} from "@/lib/openrouterChat";

const katexOptions = { strict: false, throwOnError: false };
// Fallback when a review has no recorded model (matches the home page default).
const FALLBACK_MODEL = "anthropic/claude-opus-4.8";

function normalizeModel(model?: string | null): string {
  const m = (model ?? "").replace(/^openrouter\//, "").trim();
  // The chat always routes through OpenRouter, which needs a "provider/model"
  // ID. A review's model can instead be a CLI-handoff marker
  // ("coarse-review-cli:codex") or a bare host-CLI model ("claude-opus-4-6"),
  // neither of which OpenRouter accepts — fall back to a known-good default.
  if (!m || !m.includes("/")) return FALLBACK_MODEL;
  return m;
}

const EXAMPLE_PROMPTS = [
  "Is this critique actually correct?",
  "How should I revise to address it?",
  "Where in the paper does this apply?",
];

export interface CommentChatProps {
  reviewId: string;
  comment: DetailedComment;
  paperTitle: string;
  paperMarkdown?: string | null;
  domain?: string | null;
  overallFeedbackText: string;
  commentSeverity?: string | null;
  commentConfidence?: string | null;
  defaultModel: string;
  initialMessages?: ChatMessage[];

  apiKey: string;
  hasKey: boolean;
  keyNotice?: string | null;
  onSetKey: (key: string) => void;
  onStartLogin: () => void;
  onLogout: () => void;
  onClose: () => void;
}

export default function CommentChat({
  reviewId,
  comment,
  paperTitle,
  paperMarkdown,
  domain,
  overallFeedbackText,
  commentSeverity,
  commentConfidence,
  defaultModel,
  initialMessages,
  apiKey,
  hasKey,
  keyNotice,
  onSetKey,
  onStartLogin,
  onLogout,
  onClose,
}: CommentChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages ?? []);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [model, setModel] = useState(() => normalizeModel(defaultModel));
  const abortRef = useRef<AbortController | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Persist for OAuth-redirect survival (tab-scoped). Skip during streaming so a
  // long response doesn't trigger a sessionStorage write per token; the final
  // state persists when `streaming` flips false, and handleLogin persists
  // explicitly before any redirect.
  useEffect(() => {
    if (streaming) return;
    savePersistedChat(reviewId, { commentNumber: comment.number, messages });
  }, [reviewId, comment.number, messages, streaming]);

  // Keep the transcript pinned to the latest content.
  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, streaming]);

  const handleClose = useCallback(() => {
    abortRef.current?.abort();
    onClose();
  }, [onClose]);

  // Close on Escape (also aborts any in-flight stream via handleClose).
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") handleClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [handleClose]);

  // Lock background scroll while the sheet is open.
  useEffect(() => {
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, []);

  // Focus the composer once a key is present.
  useEffect(() => {
    if (hasKey) inputRef.current?.focus();
  }, [hasKey]);

  const handleLogin = useCallback(() => {
    // Make sure the in-progress thread is on disk before the redirect navigates away.
    savePersistedChat(reviewId, { commentNumber: comment.number, messages });
    onStartLogin();
  }, [reviewId, comment.number, messages, onStartLogin]);

  const send = useCallback(
    async (raw: string) => {
      const text = raw.trim();
      if (!text || streaming || !hasKey) return;
      setError(null);
      setInput("");

      const history: ChatMessage[] = [...messages, { role: "user", content: text }];
      // Append an empty assistant bubble we stream into.
      setMessages([...history, { role: "assistant", content: "" }]);
      setStreaming(true);

      const system: ChatMessage = {
        role: "system",
        content: buildChatSystemPrompt({
          paperTitle,
          paperMarkdown,
          domain,
          overallFeedbackText,
          comment,
          severity: commentSeverity,
          confidence: commentConfidence,
        }),
      };

      const controller = new AbortController();
      abortRef.current = controller;

      try {
        let acc = "";
        for await (const delta of streamChatCompletion({
          apiKey,
          model,
          messages: [system, ...history],
          signal: controller.signal,
        })) {
          acc += delta;
          setMessages((prev) => {
            const next = prev.slice();
            next[next.length - 1] = { role: "assistant", content: acc };
            return next;
          });
        }
        if (!acc.trim()) {
          setMessages((prev) => prev.slice(0, -1));
          setError("No response from the model. Try again or switch models.");
        }
      } catch (err) {
        setMessages((prev) => prev.slice(0, -1)); // drop the streaming bubble
        if (err instanceof OpenRouterAuthError) {
          onLogout();
          setError("Your OpenRouter session expired. Log in again to continue.");
        } else {
          setError(err instanceof Error ? err.message : "Something went wrong.");
        }
      } finally {
        setStreaming(false);
        abortRef.current = null;
      }
    },
    [
      streaming,
      hasKey,
      messages,
      apiKey,
      model,
      paperTitle,
      paperMarkdown,
      domain,
      overallFeedbackText,
      comment,
      commentSeverity,
      commentConfidence,
      onLogout,
    ],
  );

  const onInputKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send(input);
    }
  };

  const visibleMessages = messages.filter((m) => m.role !== "system");

  return (
    <>
      <div onClick={handleClose} style={backdropStyle} aria-hidden="true" />
      <aside
        style={sheetStyle}
        role="dialog"
        aria-modal="true"
        aria-label={`Discuss: ${comment.title}`}
      >
        {/* Header */}
        <div style={headerStyle}>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={kickerStyle}>
              Discuss ·{" "}
              {comment.number >= 0 ? `comment #${comment.number}` : "overall feedback"}
            </div>
            <div style={titleStyle}>{comment.title}</div>
          </div>
          <button onClick={handleClose} aria-label="Close chat" style={closeBtnStyle}>
            {"×"}
          </button>
        </div>

        {/* Model picker + key control */}
        {hasKey && (
          <div
            style={{
              padding: "0.55rem 1.25rem",
              borderBottom: "1px solid var(--tray)",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: "0.75rem",
            }}
          >
            <ModelDisclosure model={model} onChange={setModel} />
            <button
              onClick={onLogout}
              title="Disconnect your OpenRouter key (it isn't stored beyond this tab)"
              style={{
                background: "none",
                border: "none",
                color: "var(--dust)",
                fontFamily: "var(--font-chalk)",
                fontSize: "0.9rem",
                textDecoration: "underline",
                cursor: "pointer",
                flexShrink: 0,
                whiteSpace: "nowrap",
              }}
            >
              Disconnect key
            </button>
          </div>
        )}

        {/* Body */}
        <div ref={scrollRef} style={bodyStyle}>
          {!hasKey ? (
            <KeyGate
              apiKey={apiKey}
              keyNotice={keyNotice}
              onSetKey={onSetKey}
              onLogin={handleLogin}
              onLogout={onLogout}
            />
          ) : (
            <>
              {visibleMessages.length === 0 && (
                <EmptyHint
                  disabled={streaming}
                  hasPaper={!!paperMarkdown?.trim()}
                  onPick={(p) => send(p)}
                />
              )}
              {visibleMessages.map((m, i) => (
                <MessageBubble
                  key={i}
                  role={m.role}
                  content={m.content}
                  streaming={
                    streaming && m.role === "assistant" && i === visibleMessages.length - 1
                  }
                />
              ))}
            </>
          )}
          {error && <div style={errorStyle}>{error}</div>}
        </div>

        {/* Input */}
        {hasKey && (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              send(input);
            }}
            style={inputBarStyle}
          >
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onInputKeyDown}
              placeholder="Ask about this comment…"
              rows={2}
              aria-label="Message"
              style={textareaStyle}
            />
            {streaming ? (
              <button type="button" onClick={() => abortRef.current?.abort()} style={sendBtnStyle}>
                Stop
              </button>
            ) : (
              <button type="submit" disabled={!input.trim()} style={sendBtnStyle}>
                Send
              </button>
            )}
          </form>
        )}
      </aside>
    </>
  );
}

/* ── Model disclosure ──────────────────────────────────────── */
function ModelDisclosure({
  model,
  onChange,
}: {
  model: string;
  onChange: (m: string) => void;
}) {
  const [open, setOpen] = useState(false);
  return (
    <div>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        style={{
          background: "none",
          border: "none",
          cursor: "pointer",
          padding: 0,
          fontFamily: "var(--font-space-mono), monospace",
          fontSize: "0.95rem",
          color: "var(--dust)",
          letterSpacing: "0.04em",
        }}
      >
        Model: <span style={{ color: "var(--chalk-bright)" }}>{model}</span>{" "}
        {open ? "▴" : "▾"}
      </button>
      {open && (
        <div style={{ marginTop: "0.6rem" }}>
          <ModelPicker
            value={model}
            onChange={(m) => {
              onChange(m);
              setOpen(false);
            }}
          />
        </div>
      )}
    </div>
  );
}

/* ── Key gate ──────────────────────────────────────────────── */
function KeyGate({
  apiKey,
  keyNotice,
  onSetKey,
  onLogin,
  onLogout,
}: {
  apiKey: string;
  keyNotice?: string | null;
  onSetKey: (key: string) => void;
  onLogin: () => void;
  onLogout: () => void;
}) {
  const [draft, setDraft] = useState("");
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "0.9rem" }}>
      <p style={{ fontFamily: "Georgia, serif", fontSize: "1rem", lineHeight: 1.6, color: "var(--dust)", margin: 0 }}>
        Connect OpenRouter to chat about this comment. Your key is sent straight to
        OpenRouter — never to our servers — and clears when you close this tab.
      </p>
      <OpenRouterLoginButton apiKey={apiKey} onLogin={onLogin} onLogout={onLogout} />
      <p style={{ fontFamily: "var(--font-chalk)", fontSize: "1rem", color: "var(--dust)", margin: 0 }}>
        — or paste a key —
      </p>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (draft.trim()) onSetKey(draft);
        }}
        style={{ display: "flex", gap: "0.5rem" }}
      >
        <input
          type="password"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="sk-or-v1-…"
          aria-label="OpenRouter API key"
          className="field-line-mono"
          style={{ flex: 1, fontSize: "1rem" }}
        />
        <button type="submit" disabled={!draft.trim()} style={sendBtnStyle}>
          Use key
        </button>
      </form>
      <p style={{ fontFamily: "var(--font-chalk)", fontSize: "0.95rem", color: "var(--dust)", margin: 0 }}>
        OAuth keys stay in this tab only and clear when you close it. Never saved on our servers.
      </p>
      {keyNotice && (
        <p style={{ fontFamily: "var(--font-chalk)", fontSize: "0.95rem", color: "var(--blue-chalk)", margin: 0 }}>
          {keyNotice}
        </p>
      )}
    </div>
  );
}

/* ── Empty hint ────────────────────────────────────────────── */
function EmptyHint({
  onPick,
  disabled,
  hasPaper,
}: {
  onPick: (p: string) => void;
  disabled: boolean;
  hasPaper: boolean;
}) {
  return (
    <div style={{ color: "var(--dust)" }}>
      <p style={{ fontFamily: "Georgia, serif", fontStyle: "italic", fontSize: "1rem", lineHeight: 1.6, margin: "0 0 0.75rem" }}>
        Ask anything about this comment. Each message sends{" "}
        {hasPaper ? "the full paper" : "the quoted passage and feedback"} as context
        and runs on your OpenRouter credits.
      </p>
      {!hasPaper && (
        <p style={{ fontFamily: "var(--font-chalk)", fontSize: "0.95rem", lineHeight: 1.55, margin: "0 0 0.75rem", color: "var(--dust)" }}>
          The full paper text isn&apos;t stored for this review, so answers rely on
          the quoted passage and feedback only.
        </p>
      )}
      <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem", alignItems: "flex-start" }}>
        {EXAMPLE_PROMPTS.map((p) => (
          <button
            key={p}
            type="button"
            disabled={disabled}
            onClick={() => onPick(p)}
            style={{
              background: "transparent",
              border: "1px solid var(--tray)",
              borderRadius: "2px",
              padding: "0.35rem 0.6rem",
              cursor: disabled ? "default" : "pointer",
              fontFamily: "var(--font-chalk)",
              fontSize: "0.95rem",
              color: "var(--chalk)",
              textAlign: "left",
            }}
          >
            {p}
          </button>
        ))}
      </div>
    </div>
  );
}

/* ── Message bubble ────────────────────────────────────────── */
function MessageBubble({
  role,
  content,
  streaming,
}: {
  role: ChatMessage["role"];
  content: string;
  streaming: boolean;
}) {
  const isUser = role === "user";
  return (
    <div
      style={{
        margin: "0 0 1rem",
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
      }}
    >
      <div
        style={{
          maxWidth: "92%",
          background: isUser ? "var(--tray)" : "transparent",
          borderRadius: "6px",
          padding: isUser ? "0.5rem 0.75rem" : 0,
          color: "var(--chalk)",
        }}
      >
        {isUser ? (
          <span style={{ whiteSpace: "pre-wrap", fontSize: "1rem", lineHeight: 1.55 }}>{content}</span>
        ) : (
          <div className="review-content" style={{ fontSize: "1rem", lineHeight: 1.6 }}>
            <ReactMarkdown
              remarkPlugins={[remarkGfm, remarkMath]}
              rehypePlugins={[[rehypeKatex, katexOptions]]}
            >
              {preprocessLatex(content)}
            </ReactMarkdown>
            {streaming && <span className="blink">{"▍"}</span>}
          </div>
        )}
      </div>
    </div>
  );
}

/* ── Styles ────────────────────────────────────────────────── */
const backdropStyle: React.CSSProperties = {
  position: "fixed",
  inset: 0,
  background: "rgba(0,0,0,0.45)",
  zIndex: 1000,
};

const sheetStyle: React.CSSProperties = {
  position: "fixed",
  top: 0,
  right: 0,
  height: "100vh",
  width: "min(480px, 96vw)",
  zIndex: 1001,
  background: "var(--board-surface)",
  borderLeft: "1px solid var(--tray)",
  display: "flex",
  flexDirection: "column",
  boxShadow: "-8px 0 28px rgba(0,0,0,0.35)",
};

const headerStyle: React.CSSProperties = {
  padding: "1rem 1.25rem",
  borderBottom: "1px solid var(--tray)",
  display: "flex",
  alignItems: "flex-start",
  gap: "0.75rem",
  flexShrink: 0,
};

const kickerStyle: React.CSSProperties = {
  fontFamily: "var(--font-space-mono), monospace",
  fontSize: "0.85rem",
  letterSpacing: "0.12em",
  textTransform: "uppercase",
  color: "var(--dust)",
};

const titleStyle: React.CSSProperties = {
  fontFamily: "var(--font-serif)",
  fontSize: "1.05rem",
  color: "var(--chalk-bright)",
  marginTop: "0.2rem",
  lineHeight: 1.3,
};

const closeBtnStyle: React.CSSProperties = {
  background: "none",
  border: "none",
  color: "var(--dust)",
  fontSize: "1.5rem",
  lineHeight: 1,
  cursor: "pointer",
  padding: "0 0.25rem",
  flexShrink: 0,
};

const bodyStyle: React.CSSProperties = {
  flex: 1,
  overflowY: "auto",
  padding: "1.1rem 1.25rem",
};

const inputBarStyle: React.CSSProperties = {
  borderTop: "1px solid var(--tray)",
  padding: "0.85rem 1.25rem",
  display: "flex",
  gap: "0.5rem",
  alignItems: "flex-end",
  flexShrink: 0,
};

const textareaStyle: React.CSSProperties = {
  flex: 1,
  resize: "none",
  maxHeight: "8rem",
  background: "var(--board)",
  border: "1px solid var(--tray)",
  borderRadius: "2px",
  color: "var(--chalk)",
  fontFamily: "Georgia, serif",
  fontSize: "1rem",
  lineHeight: 1.5,
  padding: "0.5rem 0.6rem",
};

const sendBtnStyle: React.CSSProperties = {
  background: "var(--yellow-chalk)",
  color: "var(--board)",
  border: "none",
  borderRadius: "2px",
  padding: "0.5rem 1rem",
  fontFamily: "var(--font-space-mono), monospace",
  fontSize: "0.95rem",
  letterSpacing: "0.08em",
  textTransform: "uppercase",
  cursor: "pointer",
  flexShrink: 0,
};

const errorStyle: React.CSSProperties = {
  marginTop: "0.5rem",
  borderLeft: "3px solid var(--red-chalk)",
  paddingLeft: "0.75rem",
  fontFamily: "var(--font-chalk)",
  fontSize: "0.95rem",
  color: "var(--red-chalk)",
};
