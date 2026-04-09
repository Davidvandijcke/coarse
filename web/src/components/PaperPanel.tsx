"use client";

import { useEffect, useRef, useMemo, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { splitIntoBlocks, findQuoteInBlocks } from "@/lib/quoteMatch";
import { preprocessLatex } from "@/lib/preprocessLatex";

const katexOptions = { strict: false, throwOnError: false };

export default function PaperPanel({
  markdown,
  highlightQuote,
  onClose,
  reviewId,
}: {
  markdown: string;
  highlightQuote: string | null;
  onClose: () => void;
  reviewId?: string;
}) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const blocks = useMemo(() => splitIntoBlocks(preprocessLatex(markdown)), [markdown]);

  const scrollToQuote = useCallback(
    (quote: string) => {
      const blockIndex = findQuoteInBlocks(quote, blocks);
      if (blockIndex === null) return;

      const container = scrollRef.current;
      if (!container) return;

      const el = container.querySelector(
        `[data-paper-block="${blockIndex}"]`
      ) as HTMLElement | null;
      if (!el) return;

      // Remove previous highlights
      container
        .querySelectorAll(".paper-block-highlight")
        .forEach((e) => e.classList.remove("paper-block-highlight"));

      el.classList.add("paper-block-highlight");
      el.scrollIntoView({ behavior: "smooth", block: "center" });

      // Remove highlight after animation
      setTimeout(() => el.classList.remove("paper-block-highlight"), 2500);
    },
    [blocks]
  );

  useEffect(() => {
    if (highlightQuote) {
      // Small delay to allow panel to render/open first
      const t = setTimeout(() => scrollToQuote(highlightQuote), 150);
      return () => clearTimeout(t);
    }
  }, [highlightQuote, scrollToQuote]);

  return (
    <div
      className="paper-panel"
      style={{
        width: "45%",
        flexShrink: 0,
        position: "sticky",
        top: "4.5rem",
        height: "calc(100vh - 4.5rem)",
        overflowY: "auto",
        borderRight: "1px solid var(--tray)",
      }}
    >
      {/* Header */}
      <div
        style={{
          position: "sticky",
          top: 0,
          background: "var(--board)",
          borderBottom: "1px solid var(--tray)",
          padding: "0.5rem 1rem",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          zIndex: 5,
        }}
      >
        <span
          style={{
            fontFamily: "var(--font-space-mono), monospace",
            fontSize: "0.95rem",
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            color: "var(--dust)",
          }}
        >
          Paper
        </span>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <button
            onClick={() => {
              const blob = new Blob([markdown], { type: "text/markdown" });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = `paper_${reviewId || "export"}.md`;
              a.click();
              URL.revokeObjectURL(url);
            }}
            style={{
              background: "none",
              border: "none",
              color: "var(--dust)",
              cursor: "pointer",
              fontFamily: "var(--font-space-mono), monospace",
              fontSize: "0.85rem",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              padding: "0.25rem",
            }}
            aria-label="Download paper markdown"
          >
            Download
          </button>
          <button
            onClick={onClose}
            style={{
              background: "none",
              border: "none",
              color: "var(--dust)",
              cursor: "pointer",
              fontFamily: "var(--font-space-mono), monospace",
              fontSize: "1.05rem",
              padding: "0.25rem",
            }}
            aria-label="Close paper panel"
          >
            {"\u00d7"}
          </button>
        </div>
      </div>

      {/* Paper content */}
      <div
        ref={scrollRef}
        className="review-content"
        style={{
          padding: "1rem 1.25rem 3rem",
          fontSize: "1rem",
          lineHeight: 1.7,
        }}
      >
        {blocks.map((block, i) => (
          <div key={i} data-paper-block={i} id={`paper-block-${i}`}>
            <ReactMarkdown
              remarkPlugins={[remarkGfm, remarkMath]}
              rehypePlugins={[[rehypeKatex, katexOptions]]}
            >
              {block}
            </ReactMarkdown>
          </div>
        ))}
      </div>
    </div>
  );
}
