"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import type { ParsedReview, DetailedComment } from "@/lib/parseReview";
import { CharcoalRule } from "@/components/charcoal";

const katexOptions = { strict: false, throwOnError: false };

/* ── Quote block with expand/collapse ──────────────────────── */
function QuoteBlock({ text }: { text: string }) {
  const [expanded, setExpanded] = useState(false);
  const lines = text.split("\n");
  const isLong = lines.length > 4 || text.length > 300;
  const shown = !isLong || expanded ? text : lines.slice(0, 3).join("\n") + "...";

  return (
    <div
      style={{
        borderLeft: "3px solid var(--red-chalk)",
        padding: "0.5rem 0 0.5rem 1rem",
        margin: "0.75rem 0",
        background: "rgba(194, 124, 107, 0.04)",
        borderRadius: "0 2px 2px 0",
      }}
    >
      <div
        style={{
          fontFamily: "Georgia, serif",
          fontStyle: "italic",
          fontSize: "0.9rem",
          lineHeight: 1.7,
          color: "var(--dust)",
          whiteSpace: "pre-wrap",
        }}
      >
        <ReactMarkdown
          remarkPlugins={[remarkGfm, remarkMath]}
          rehypePlugins={[[rehypeKatex, katexOptions]]}
        >
          {shown}
        </ReactMarkdown>
      </div>
      {isLong && (
        <button
          onClick={() => setExpanded((v) => !v)}
          style={{
            background: "none",
            border: "none",
            color: "var(--blue-chalk)",
            fontFamily: "var(--font-space-mono), monospace",
            fontSize: "0.7rem",
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            cursor: "pointer",
            padding: "0.25rem 0 0",
          }}
        >
          {expanded ? "Show less" : "Show more"}
        </button>
      )}
    </div>
  );
}

/* ── Single comment card ───────────────────────────────────── */
function CommentCard({
  comment,
  id,
}: {
  comment: DetailedComment;
  id: string;
}) {
  return (
    <div
      id={id}
      style={{
        scrollMarginTop: "5rem",
        padding: "1.25rem 0",
      }}
    >
      {/* Number + title */}
      <div style={{ display: "flex", alignItems: "baseline", gap: "0.75rem" }}>
        <span
          style={{
            fontFamily: "var(--font-chalk)",
            fontSize: "1.5rem",
            color: "var(--yellow-chalk)",
            lineHeight: 1,
            fontWeight: 700,
          }}
        >
          #{comment.number}
        </span>
        <h3
          style={{
            fontFamily: "var(--font-serif)",
            fontSize: "1rem",
            fontWeight: 400,
            color: "var(--chalk-bright)",
            margin: 0,
            lineHeight: 1.35,
          }}
        >
          {comment.title}
        </h3>
      </div>

      {/* Quote */}
      {comment.quote && <QuoteBlock text={comment.quote} />}

      {/* Feedback */}
      <div
        className="review-content"
        style={{ fontSize: "0.95rem", lineHeight: 1.7, marginTop: "0.5rem" }}
      >
        <ReactMarkdown
          remarkPlugins={[remarkGfm, remarkMath]}
          rehypePlugins={[[rehypeKatex, katexOptions]]}
        >
          {comment.feedback}
        </ReactMarkdown>
      </div>

      {/* Status badge */}
      <span
        style={{
          display: "inline-block",
          marginTop: "0.5rem",
          fontFamily: "var(--font-space-mono), monospace",
          fontSize: "0.6rem",
          letterSpacing: "0.12em",
          textTransform: "uppercase",
          color: "var(--dust)",
          border: "1px solid var(--tray)",
          padding: "0.2rem 0.5rem",
          borderRadius: "2px",
        }}
      >
        {comment.status}
      </span>
    </div>
  );
}

/* ── Sidebar TOC ───────────────────────────────────────────── */
function Sidebar({
  parsed,
  activeId,
  onNavigate,
}: {
  parsed: ParsedReview;
  activeId: string | null;
  onNavigate: (id: string) => void;
}) {
  return (
    <nav
      className="review-sidebar"
      style={{
        position: "sticky",
        top: "4.5rem",
        alignSelf: "flex-start",
        width: "220px",
        flexShrink: 0,
        maxHeight: "calc(100vh - 5.5rem)",
        overflowY: "auto",
        paddingRight: "1rem",
        borderRight: "1px solid var(--tray)",
      }}
    >
      {/* Overall Feedback link */}
      <button
        onClick={() => onNavigate("overall-feedback")}
        style={{
          display: "block",
          width: "100%",
          textAlign: "left",
          background: "none",
          border: "none",
          padding: "0.4rem 0.5rem",
          cursor: "pointer",
          fontFamily: "var(--font-chalk)",
          fontSize: "0.95rem",
          color:
            activeId === "overall-feedback"
              ? "var(--yellow-chalk)"
              : "var(--dust)",
          transition: "color 0.15s",
          borderRadius: "2px",
        }}
      >
        Overall Feedback
      </button>

      {/* Divider */}
      <div
        style={{
          height: "1px",
          background: "var(--tray)",
          margin: "0.5rem 0.5rem",
        }}
      />

      {/* Comment links */}
      <div
        style={{
          fontFamily: "var(--font-space-mono), monospace",
          fontSize: "0.65rem",
          letterSpacing: "0.08em",
          textTransform: "uppercase",
          color: "var(--dust)",
          padding: "0.25rem 0.5rem 0.5rem",
        }}
      >
        Comments ({parsed.detailedComments.length})
      </div>
      {parsed.detailedComments.map((c) => {
        const cid = `comment-${c.number}`;
        const isActive = activeId === cid;
        return (
          <button
            key={c.number}
            onClick={() => onNavigate(cid)}
            style={{
              display: "block",
              width: "100%",
              textAlign: "left",
              background: isActive ? "var(--board-surface)" : "none",
              border: "none",
              padding: "0.35rem 0.5rem",
              cursor: "pointer",
              fontFamily: "Georgia, serif",
              fontSize: "0.75rem",
              lineHeight: 1.4,
              color: isActive ? "var(--chalk-bright)" : "var(--dust)",
              transition: "all 0.15s",
              borderRadius: "2px",
              borderLeft: isActive
                ? "2px solid var(--yellow-chalk)"
                : "2px solid transparent",
            }}
          >
            <span style={{ color: "var(--yellow-chalk)", fontWeight: 700 }}>
              {c.number}.
            </span>{" "}
            {c.title.length > 40 ? c.title.slice(0, 40) + "..." : c.title}
          </button>
        );
      })}
    </nav>
  );
}

/* ── Download dropdown ─────────────────────────────────────── */
function DownloadMenu({
  markdown,
  title,
}: {
  markdown: string;
  title: string;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node))
        setOpen(false);
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const slug = title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/_+$/, "");

  function downloadMd() {
    const blob = new Blob([markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${slug}_review.md`;
    a.click();
    URL.revokeObjectURL(url);
    setOpen(false);
  }

  function printPdf() {
    window.print();
    setOpen(false);
  }

  const btnStyle: React.CSSProperties = {
    background: "transparent",
    border: "none",
    color: "var(--chalk)",
    padding: "0.5rem 0.75rem",
    fontFamily: "var(--font-space-mono), monospace",
    fontSize: "0.65rem",
    letterSpacing: "0.1em",
    textTransform: "uppercase",
    cursor: "pointer",
    width: "100%",
    textAlign: "left",
  };

  return (
    <div ref={ref} style={{ position: "relative" }}>
      <button
        onClick={() => setOpen((v) => !v)}
        style={{
          background: "transparent",
          border: "1.5px solid var(--chalk)",
          color: "var(--chalk)",
          padding: "0.375rem 0.875rem",
          fontFamily: "var(--font-space-mono), monospace",
          fontSize: "0.5625rem",
          letterSpacing: "0.12em",
          textTransform: "uppercase",
          cursor: "pointer",
        }}
      >
        Download
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
            minWidth: "140px",
          }}
        >
          <button
            onClick={downloadMd}
            style={btnStyle}
            onMouseEnter={(e) =>
              (e.currentTarget.style.background = "var(--tray)")
            }
            onMouseLeave={(e) =>
              (e.currentTarget.style.background = "transparent")
            }
          >
            Markdown (.md)
          </button>
          <button
            onClick={printPdf}
            style={btnStyle}
            onMouseEnter={(e) =>
              (e.currentTarget.style.background = "var(--tray)")
            }
            onMouseLeave={(e) =>
              (e.currentTarget.style.background = "transparent")
            }
          >
            Print / PDF
          </button>
        </div>
      )}
    </div>
  );
}

/* ── Main ReviewDisplay ────────────────────────────────────── */
export default function ReviewDisplay({
  parsed,
  markdown,
  domain,
  durationSeconds,
  costUsd,
}: {
  parsed: ParsedReview;
  markdown: string;
  domain?: string | null;
  durationSeconds?: number | null;
  costUsd?: number | null;
}) {
  const [activeId, setActiveId] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const mainRef = useRef<HTMLDivElement>(null);

  /* ── IntersectionObserver for active sidebar highlight ──── */
  useEffect(() => {
    const sections = mainRef.current?.querySelectorAll("[data-nav-id]");
    if (!sections?.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActiveId(
              (entry.target as HTMLElement).dataset.navId ?? null
            );
          }
        }
      },
      { rootMargin: "-20% 0px -60% 0px", threshold: 0 }
    );

    sections.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, [parsed]);

  const navigate = useCallback((id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  }, []);

  function copyLink() {
    navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <>
      {/* ── Header ──────────────────────────────────────────── */}
      <header
        className="review-header"
        style={{
          borderBottom: "1px solid var(--tray)",
          padding: "0.75rem 2rem",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          position: "sticky",
          top: 0,
          background: "var(--board)",
          zIndex: 10,
        }}
      >
        <a
          href="/"
          style={{
            fontFamily: "var(--font-serif)",
            fontSize: "1.15rem",
            fontWeight: 700,
            letterSpacing: "-0.02em",
            textDecoration: "none",
            color: "var(--chalk-bright)",
          }}
        >
          &lsquo;coarse
        </a>

        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          {/* Comment count badge */}
          <span
            style={{
              fontFamily: "var(--font-chalk)",
              fontSize: "0.95rem",
              color: "var(--yellow-chalk)",
            }}
          >
            {parsed.detailedComments.length} comments
          </span>

          <button
            onClick={copyLink}
            style={{
              background: "transparent",
              border: "1.5px solid var(--chalk)",
              color: "var(--chalk)",
              padding: "0.375rem 0.875rem",
              fontFamily: "var(--font-space-mono), monospace",
              fontSize: "0.5625rem",
              letterSpacing: "0.12em",
              textTransform: "uppercase",
              cursor: "pointer",
            }}
          >
            {copied ? "Copied" : "Share"}
          </button>

          <DownloadMenu markdown={markdown} title={parsed.title} />

          <a
            href="https://github.com/Davidvandijcke/coarse"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              fontFamily: "var(--font-space-mono), monospace",
              fontSize: "0.5625rem",
              letterSpacing: "0.12em",
              textTransform: "uppercase",
              color: "var(--dust)",
              textDecoration: "none",
            }}
          >
            GitHub
          </a>
        </div>
      </header>

      {/* ── Body: sidebar + main ────────────────────────────── */}
      <div
        style={{
          display: "flex",
          maxWidth: "1100px",
          margin: "0 auto",
          padding: "2rem 2rem 4rem",
          gap: "2rem",
        }}
      >
        {/* Sidebar */}
        <Sidebar
          parsed={parsed}
          activeId={activeId}
          onNavigate={navigate}
        />

        {/* Main content */}
        <main
          ref={mainRef}
          className="review-main"
          style={{ flex: 1, minWidth: 0 }}
        >
          {/* Paper title */}
          <h1
            style={{
              fontFamily: "var(--font-serif)",
              fontSize: "clamp(1.5rem, 3.5vw, 2.25rem)",
              fontWeight: 700,
              lineHeight: 1.15,
              letterSpacing: "-0.02em",
              margin: "0 0 1rem",
              color: "var(--chalk-bright)",
            }}
          >
            {parsed.title}
          </h1>

          {/* Meta row */}
          <div
            style={{
              display: "flex",
              gap: "1.5rem",
              flexWrap: "wrap",
              marginBottom: "1.5rem",
            }}
          >
            {parsed.metadata.date && (
              <MetaTag label="Date" value={parsed.metadata.date} />
            )}
            {(domain || parsed.metadata.domain) && (
              <MetaTag
                label="Domain"
                value={(domain || parsed.metadata.domain).replace(/_/g, " / ")}
              />
            )}
            {durationSeconds != null && (
              <MetaTag label="Time" value={`${durationSeconds}s`} />
            )}
            {costUsd != null && (
              <MetaTag label="Cost" value={`$${Number(costUsd).toFixed(2)}`} />
            )}
          </div>

          <CharcoalRule />

          {/* ── Overall Feedback ───────────────────────────── */}
          <section
            id="overall-feedback"
            data-nav-id="overall-feedback"
            style={{ scrollMarginTop: "5rem", marginTop: "1.5rem" }}
          >
            <h2
              style={{
                fontFamily: "var(--font-serif)",
                fontSize: "1.1rem",
                fontWeight: 400,
                color: "var(--chalk-bright)",
                margin: "0 0 1rem",
                paddingBottom: "0.3rem",
                borderBottom: "1px solid var(--tray)",
              }}
            >
              Overall Feedback
            </h2>

            {parsed.overallFeedback.summary && (
              <div
                className="review-content"
                style={{ marginBottom: "1rem", fontSize: "0.95rem" }}
              >
                <ReactMarkdown
                  remarkPlugins={[remarkGfm, remarkMath]}
                  rehypePlugins={[[rehypeKatex, katexOptions]]}
                >
                  {parsed.overallFeedback.summary}
                </ReactMarkdown>
              </div>
            )}

            {parsed.overallFeedback.issues.map((issue, i) => (
              <div
                key={i}
                style={{
                  background: "var(--board-surface)",
                  borderRadius: "2px",
                  border: "1px solid var(--tray)",
                  padding: "1rem 1.25rem",
                  marginBottom: "0.75rem",
                }}
              >
                <h3
                  style={{
                    fontFamily: "var(--font-serif)",
                    fontSize: "0.95rem",
                    fontWeight: 700,
                    color: "var(--chalk-bright)",
                    margin: "0 0 0.5rem",
                    lineHeight: 1.35,
                  }}
                >
                  {issue.title}
                </h3>
                <div
                  className="review-content"
                  style={{ fontSize: "0.9rem", lineHeight: 1.7 }}
                >
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm, remarkMath]}
                    rehypePlugins={[[rehypeKatex, katexOptions]]}
                  >
                    {issue.body}
                  </ReactMarkdown>
                </div>
              </div>
            ))}
          </section>

          <CharcoalRule />

          {/* ── Detailed Comments ──────────────────────────── */}
          <section style={{ marginTop: "1.5rem" }}>
            <h2
              style={{
                fontFamily: "var(--font-serif)",
                fontSize: "1.1rem",
                fontWeight: 400,
                color: "var(--chalk-bright)",
                margin: "0 0 0.5rem",
                paddingBottom: "0.3rem",
                borderBottom: "1px solid var(--tray)",
              }}
            >
              Detailed Comments ({parsed.detailedComments.length})
            </h2>

            {parsed.detailedComments.map((comment) => {
              const cid = `comment-${comment.number}`;
              return (
                <div key={comment.number} data-nav-id={cid}>
                  <CommentCard comment={comment} id={cid} />
                  <div
                    style={{
                      height: "1px",
                      background: "var(--tray)",
                      margin: "0.25rem 0",
                    }}
                  />
                </div>
              );
            })}
          </section>

          {/* ── Footer ─────────────────────────────────────── */}
          <div style={{ marginTop: "3rem" }}>
            <CharcoalRule />
            <div
              style={{
                padding: "1.25rem 0",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                flexWrap: "wrap",
                gap: "1rem",
              }}
            >
              <span
                style={{
                  fontFamily: "var(--font-serif)",
                  fontSize: "0.95rem",
                  fontStyle: "italic",
                  color: "var(--dust)",
                }}
              >
                Generated by{" "}
                <a
                  href="/"
                  style={{
                    color: "var(--chalk-bright)",
                    textDecoration: "none",
                    fontWeight: 700,
                  }}
                >
                  &lsquo;coarse
                </a>
                . Of course.
              </span>
              <button
                onClick={copyLink}
                style={{
                  background: "transparent",
                  border: "1.5px solid var(--chalk)",
                  color: "var(--chalk)",
                  padding: "0.375rem 1rem",
                  fontFamily: "var(--font-space-mono), monospace",
                  fontSize: "0.5625rem",
                  letterSpacing: "0.12em",
                  textTransform: "uppercase",
                  cursor: "pointer",
                }}
              >
                {copied ? "Copied" : "Share this review"}
              </button>
            </div>
          </div>
        </main>
      </div>
    </>
  );
}

/* ── Small helpers ──────────────────────────────────────────── */
function MetaTag({ label, value }: { label: string; value: string }) {
  return (
    <span
      style={{
        fontFamily: "var(--font-space-mono), monospace",
        fontSize: "0.6rem",
        letterSpacing: "0.1em",
        textTransform: "uppercase",
      }}
    >
      <span style={{ color: "var(--dust)" }}>{label} </span>
      <span style={{ color: "var(--chalk)" }}>{value}</span>
    </span>
  );
}
