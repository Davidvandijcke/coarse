"use client";

import { useEffect, useRef, useState } from "react";
import { AI_SERVICES, startAiHandoff, type AiService } from "@/lib/aiHandoff";
import type { ReviewJson } from "@/lib/types";

/** Header dropdown that hands the paper + review + structured JSON off to an
 * external AI chat service (Claude, ChatGPT, Gemini, Grok, DeepSeek). */
export default function SubscriptionHandoffMenu({
  reviewId,
  paperTitle,
  paperMarkdown,
  markdown,
  resultJson,
}: {
  reviewId: string;
  paperTitle?: string | null;
  paperMarkdown?: string | null;
  markdown: string;
  resultJson?: ReviewJson | null;
}) {
  const [open, setOpen] = useState(false);
  const [note, setNote] = useState<string | null>(null);
  const ref = useRef<HTMLDivElement>(null);
  const noteTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  useEffect(() => () => {
    if (noteTimer.current) clearTimeout(noteTimer.current);
  }, []);

  function handoff(service: AiService) {
    startAiHandoff(service, reviewId, {
      paperTitle,
      paperMarkdown,
      resultMarkdown: markdown,
      resultJson,
    });
    setOpen(false);
    setNote(
      `Context downloaded + a starter prompt copied. In ${service.label}: start a chat, attach coarse_${reviewId}_context.md, and paste.`,
    );
    if (noteTimer.current) clearTimeout(noteTimer.current);
    noteTimer.current = setTimeout(() => setNote(null), 12000);
  }

  const itemStyle: React.CSSProperties = {
    background: "transparent",
    border: "none",
    color: "var(--chalk)",
    padding: "0.5rem 0.75rem",
    fontFamily: "var(--font-space-mono), monospace",
    fontSize: "1rem",
    letterSpacing: "0.08em",
    cursor: "pointer",
    width: "100%",
    textAlign: "left",
  };

  return (
    <div ref={ref} style={{ position: "relative" }}>
      <button
        onClick={() => setOpen((v) => !v)}
        title="Send the paper + review to your own AI chat (Claude, ChatGPT, Gemini, Grok, DeepSeek)"
        style={{
          background: "transparent",
          border: "1.5px solid var(--chalk)",
          color: "var(--chalk)",
          padding: "0.375rem 0.875rem",
          fontFamily: "var(--font-space-mono), monospace",
          fontSize: "1.05rem",
          letterSpacing: "0.12em",
          textTransform: "uppercase",
          cursor: "pointer",
          whiteSpace: "nowrap",
        }}
      >
        Discuss with your AI
      </button>

      {open && (
        <div
          style={{
            position: "absolute",
            top: "100%",
            right: 0,
            marginTop: "0.25rem",
            background: "var(--board-surface)",
            border: "1px solid var(--tray)",
            borderRadius: "2px",
            zIndex: 20,
            minWidth: "220px",
          }}
        >
          <div
            style={{
              padding: "0.5rem 0.75rem",
              fontFamily: "var(--font-chalk)",
              fontSize: "0.95rem",
              color: "var(--dust)",
              borderBottom: "1px solid var(--tray)",
              lineHeight: 1.4,
            }}
          >
            Downloads the paper + review, then opens:
          </div>
          {AI_SERVICES.map((s) => (
            <button
              key={s.key}
              onClick={() => handoff(s)}
              style={itemStyle}
              onMouseEnter={(e) => (e.currentTarget.style.background = "var(--tray)")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
            >
              {s.label}
            </button>
          ))}
        </div>
      )}

      {note && (
        <div
          style={{
            position: "absolute",
            top: "100%",
            right: 0,
            marginTop: "0.25rem",
            background: "var(--board-surface)",
            border: "1px solid var(--tray)",
            borderRadius: "2px",
            zIndex: 20,
            width: "300px",
            padding: "0.6rem 0.75rem",
            fontFamily: "var(--font-chalk)",
            fontSize: "0.95rem",
            color: "var(--chalk)",
            lineHeight: 1.45,
          }}
        >
          {note}
        </div>
      )}
    </div>
  );
}
