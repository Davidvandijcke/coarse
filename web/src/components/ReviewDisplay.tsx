"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import type { ParsedReview, DetailedComment } from "@/lib/parseReview";
import { CharcoalRule } from "@/components/charcoal";
import {
  useCommentStatus,
  type CommentStatus,
  type CommentFilter,
} from "@/lib/useCommentStatus";
import PaperPanel from "@/components/PaperPanel";
import { preprocessLatex } from "@/lib/preprocessLatex";

const katexOptions = { strict: false, throwOnError: false };

/* ── Quote block with expand/collapse + "Show in paper" ──── */
function QuoteBlock({
  text,
  onShowInPaper,
}: {
  text: string;
  onShowInPaper?: () => void;
}) {
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
          fontSize: "1.05rem",
          lineHeight: 1.7,
          color: "var(--dust)",
          whiteSpace: "pre-wrap",
        }}
      >
        <ReactMarkdown
          remarkPlugins={[remarkGfm, remarkMath]}
          rehypePlugins={[[rehypeKatex, katexOptions]]}
        >
          {preprocessLatex(shown)}
        </ReactMarkdown>
      </div>
      <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
        {isLong && (
          <button
            onClick={() => setExpanded((v) => !v)}
            style={{
              background: "none",
              border: "none",
              color: "var(--blue-chalk)",
              fontFamily: "var(--font-space-mono), monospace",
              fontSize: "1.05rem",
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              cursor: "pointer",
              padding: "0.25rem 0 0",
            }}
          >
            {expanded ? "Show less" : "Show more"}
          </button>
        )}
        {onShowInPaper && (
          <button
            onClick={onShowInPaper}
            className="show-in-paper-btn"
            style={{
              background: "none",
              border: "none",
              color: "var(--blue-chalk)",
              fontFamily: "var(--font-space-mono), monospace",
              fontSize: "1.05rem",
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              cursor: "pointer",
              padding: "0.25rem 0 0",
            }}
          >
            {"\u2190"} Show in paper
          </button>
        )}
      </div>
    </div>
  );
}

/* ── Status action buttons ─────────────────────────────────── */
const actionBtnStyle: React.CSSProperties = {
  background: "none",
  border: "1px solid var(--tray)",
  borderRadius: "2px",
  cursor: "pointer",
  padding: "0.15rem 0.4rem",
  fontFamily: "var(--font-space-mono), monospace",
  fontSize: "1rem",
  lineHeight: 1,
  transition: "all 0.15s",
};

function StatusButtons({
  status,
  onStatusChange,
}: {
  status: CommentStatus;
  onStatusChange: (s: CommentStatus) => void;
}) {
  return (
    <div style={{ display: "flex", gap: "0.35rem", marginLeft: "auto", flexShrink: 0 }}>
      <button
        onClick={() => onStatusChange(status === "done" ? "active" : "done")}
        title={status === "done" ? "Mark as active" : "Mark as done"}
        style={{
          ...actionBtnStyle,
          color: status === "done" ? "#6B9E6B" : "var(--dust)",
          borderColor: status === "done" ? "#6B9E6B" : "var(--tray)",
        }}
      >
        {"\u2713"}
      </button>
      <button
        onClick={() =>
          onStatusChange(status === "dismissed" ? "active" : "dismissed")
        }
        title={status === "dismissed" ? "Mark as active" : "Dismiss"}
        style={{
          ...actionBtnStyle,
          color: status === "dismissed" ? "var(--red-chalk)" : "var(--dust)",
          borderColor: status === "dismissed" ? "var(--red-chalk)" : "var(--tray)",
        }}
      >
        {"\u00d7"}
      </button>
    </div>
  );
}

/* ── Single comment card ───────────────────────────────────── */
function CommentCard({
  comment,
  id,
  commentStatus,
  onStatusChange,
  onShowInPaper,
}: {
  comment: DetailedComment;
  id: string;
  commentStatus: CommentStatus;
  onStatusChange: (s: CommentStatus) => void;
  onShowInPaper?: () => void;
}) {
  const [showDismissed, setShowDismissed] = useState(false);
  const isDone = commentStatus === "done";
  const isDismissed = commentStatus === "dismissed";

  return (
    <div
      id={id}
      style={{
        scrollMarginTop: "5rem",
        padding: "1.25rem 0",
        opacity: isDismissed ? 0.35 : isDone ? 0.6 : 1,
        transition: "opacity 0.2s",
      }}
    >
      {/* Number + title + action buttons */}
      <div style={{ display: "flex", alignItems: "baseline", gap: "0.75rem" }}>
        <span
          style={{
            fontFamily: "var(--font-chalk)",
            fontSize: "1.5rem",
            color: isDone ? "#6B9E6B" : "var(--yellow-chalk)",
            lineHeight: 1,
            fontWeight: 700,
          }}
        >
          {isDone ? "\u2713" : `#${comment.number}`}
        </span>
        <h3
          style={{
            fontFamily: "var(--font-serif)",
            fontSize: "1rem",
            fontWeight: 400,
            color: "var(--chalk-bright)",
            margin: 0,
            lineHeight: 1.35,
            textDecoration: isDone ? "line-through" : "none",
            flex: 1,
          }}
        >
          {comment.title}
        </h3>
        <StatusButtons status={commentStatus} onStatusChange={onStatusChange} />
      </div>

      {/* Collapsed content for dismissed */}
      {isDismissed && !showDismissed ? (
        <button
          onClick={() => setShowDismissed(true)}
          style={{
            background: "none",
            border: "none",
            color: "var(--dust)",
            fontFamily: "var(--font-space-mono), monospace",
            fontSize: "1rem",
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            cursor: "pointer",
            padding: "0.5rem 0 0",
          }}
        >
          Show details
        </button>
      ) : (
        <>
          {/* Quote */}
          {comment.quote && (
            <QuoteBlock text={comment.quote} onShowInPaper={onShowInPaper} />
          )}

          {/* Feedback */}
          <div
            className="review-content"
            style={{ fontSize: "1.1rem", lineHeight: 1.7, marginTop: "0.5rem" }}
          >
            <ReactMarkdown
              remarkPlugins={[remarkGfm, remarkMath]}
              rehypePlugins={[[rehypeKatex, katexOptions]]}
            >
              {preprocessLatex(comment.feedback)}
            </ReactMarkdown>
          </div>

          {/* Status badge */}
          <span
            style={{
              display: "inline-block",
              marginTop: "0.5rem",
              fontFamily: "var(--font-space-mono), monospace",
              fontSize: "1.1rem",
              letterSpacing: "0.12em",
              textTransform: "uppercase",
              color: isDone
                ? "#6B9E6B"
                : isDismissed
                  ? "var(--red-chalk)"
                  : "var(--dust)",
              border: `1px solid ${isDone ? "#6B9E6B" : isDismissed ? "var(--red-chalk)" : "var(--tray)"}`,
              padding: "0.2rem 0.5rem",
              borderRadius: "2px",
            }}
          >
            {isDone ? "Done" : isDismissed ? "Dismissed" : comment.status}
          </span>

          {/* Collapse button for dismissed */}
          {isDismissed && showDismissed && (
            <button
              onClick={() => setShowDismissed(false)}
              style={{
                background: "none",
                border: "none",
                color: "var(--dust)",
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "1rem",
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                cursor: "pointer",
                padding: "0 0 0 0.75rem",
              }}
            >
              Hide
            </button>
          )}
        </>
      )}
    </div>
  );
}

/* ── Filter tabs ───────────────────────────────────────────── */
const FILTERS: { key: CommentFilter; label: string }[] = [
  { key: "all", label: "All" },
  { key: "active", label: "Active" },
  { key: "done", label: "Done" },
  { key: "dismissed", label: "Dismissed" },
];

function FilterTabs({
  current,
  onChange,
}: {
  current: CommentFilter;
  onChange: (f: CommentFilter) => void;
}) {
  return (
    <div
      style={{
        display: "flex",
        gap: "0.25rem",
        padding: "0.25rem 0.5rem 0.5rem",
        flexWrap: "wrap",
      }}
    >
      {FILTERS.map(({ key, label }) => (
        <button
          key={key}
          onClick={() => onChange(key)}
          style={{
            background: "none",
            border: "none",
            cursor: "pointer",
            fontFamily: "var(--font-space-mono), monospace",
            fontSize: "1.05rem",
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            color: current === key ? "var(--yellow-chalk)" : "var(--dust)",
            padding: "0.15rem 0.3rem",
            borderBottom:
              current === key ? "1px solid var(--yellow-chalk)" : "1px solid transparent",
            transition: "all 0.15s",
          }}
        >
          {label}
        </button>
      ))}
    </div>
  );
}

/* ── Sidebar TOC ───────────────────────────────────────────── */
function Sidebar({
  parsed,
  activeId,
  onNavigate,
  getStatus,
  remaining,
  filter,
  onFilterChange,
}: {
  parsed: ParsedReview;
  activeId: string | null;
  onNavigate: (id: string) => void;
  getStatus: (n: number) => CommentStatus;
  remaining: number;
  filter: CommentFilter;
  onFilterChange: (f: CommentFilter) => void;
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
          fontSize: "1.1rem",
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

      {/* Comment header with remaining count */}
      <div
        style={{
          fontFamily: "var(--font-space-mono), monospace",
          fontSize: "1rem",
          letterSpacing: "0.08em",
          textTransform: "uppercase",
          color: "var(--dust)",
          padding: "0.25rem 0.5rem 0",
        }}
      >
        Comments ({remaining}/{parsed.detailedComments.length} remaining)
      </div>

      {/* Filter tabs */}
      <FilterTabs current={filter} onChange={onFilterChange} />

      {/* Comment links */}
      {parsed.detailedComments.map((c) => {
        const cid = `comment-${c.number}`;
        const isActive = activeId === cid;
        const cs = getStatus(c.number);

        // Filter visibility
        if (filter !== "all" && cs !== filter) return null;

        const isDone = cs === "done";
        const isDismissed = cs === "dismissed";

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
              fontSize: "1.05rem",
              lineHeight: 1.4,
              color: isActive
                ? "var(--chalk-bright)"
                : isDismissed
                  ? "var(--dust)"
                  : "var(--dust)",
              opacity: isDismissed ? 0.4 : 1,
              transition: "all 0.15s",
              borderRadius: "2px",
              borderLeft: isActive
                ? "2px solid var(--yellow-chalk)"
                : "2px solid transparent",
              textDecoration: isDone ? "line-through" : "none",
            }}
          >
            <span
              style={{
                color: isDone ? "#6B9E6B" : "var(--yellow-chalk)",
                fontWeight: 700,
              }}
            >
              {isDone ? "\u2713" : `${c.number}.`}
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
  reviewId,
  model,
}: {
  markdown: string;
  reviewId: string;
  model?: string | null;
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

  const modelSlug = (model || "unknown")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/_+$/, "");

  function downloadMd() {
    const blob = new Blob([markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `coarse_${reviewId}_${modelSlug}.md`;
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
    fontSize: "1rem",
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
          fontSize: "1.05rem",
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

/* ── Header button style ──────────────────────────────────── */
const headerBtnStyle: React.CSSProperties = {
  background: "transparent",
  border: "1.5px solid var(--chalk)",
  color: "var(--chalk)",
  padding: "0.375rem 0.875rem",
  fontFamily: "var(--font-space-mono), monospace",
  fontSize: "1.05rem",
  letterSpacing: "0.12em",
  textTransform: "uppercase",
  cursor: "pointer",
};

/* ── Main ReviewDisplay ────────────────────────────────────── */
export default function ReviewDisplay({
  parsed,
  markdown,
  reviewId,
  paperMarkdown,
  paperTitle,
  model,
  domain,
  durationSeconds,
  costUsd,
}: {
  parsed: ParsedReview;
  markdown: string;
  reviewId: string;
  paperMarkdown?: string | null;
  paperTitle?: string | null;
  model?: string | null;
  domain?: string | null;
  durationSeconds?: number | null;
  costUsd?: number | null;
}) {
  const router = useRouter();
  const [activeId, setActiveId] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [paperPanelOpen, setPaperPanelOpen] = useState(!!paperMarkdown);
  const [highlightQuote, setHighlightQuote] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);

  // Open paper panel by default when paper markdown becomes available
  useEffect(() => {
    if (paperMarkdown) setPaperPanelOpen(true);
  }, [paperMarkdown]);
  const mainRef = useRef<HTMLDivElement>(null);

  const { getStatus, setStatus, remaining, filter, setFilter } =
    useCommentStatus(reviewId, parsed.detailedComments.length);

  const hasPaper = !!paperMarkdown;

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
  }, [parsed, paperPanelOpen]);

  const navigate = useCallback((id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  }, []);

  function copyLink() {
    navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function handleShowInPaper(quote: string) {
    if (!hasPaper) return;
    if (!paperPanelOpen) setPaperPanelOpen(true);
    // Bump the quote to trigger re-search even if same quote clicked twice
    setHighlightQuote(null);
    setTimeout(() => setHighlightQuote(quote), 50);
  }

  async function handleDelete() {
    setDeleting(true);
    try {
      const res = await fetch("/api/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: reviewId }),
      });
      if (res.ok) {
        router.push("/");
      } else {
        setDeleting(false);
        setShowDeleteConfirm(false);
      }
    } catch {
      setDeleting(false);
      setShowDeleteConfirm(false);
    }
  }

  /* ── Delete confirmation screen ─────────────────────────── */
  if (showDeleteConfirm) {
    return (
      <div style={{ background: "var(--board)", minHeight: "100vh" }}>
        <header
          style={{
            borderBottom: "1px solid var(--tray)",
            padding: "0.75rem 2rem",
            display: "flex",
            alignItems: "center",
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
        </header>

        <main
          style={{
            maxWidth: "560px",
            margin: "0 auto",
            padding: "5rem 2.5rem 6rem",
          }}
        >
          <h1
            style={{
              fontFamily: "var(--font-serif)",
              fontSize: "clamp(2.5rem, 6vw, 4rem)",
              fontStyle: "italic",
              fontWeight: 700,
              lineHeight: 1.1,
              letterSpacing: "-0.02em",
              margin: "0 0 2rem",
              color: "var(--chalk-bright)",
            }}
          >
            Delete review?
          </h1>

          <p
            style={{
              fontFamily: "Georgia, serif",
              fontSize: "1rem",
              lineHeight: 1.65,
              color: "var(--dust)",
              fontStyle: "italic",
              margin: "0 0 2.5rem",
            }}
          >
            Are you sure? You will not be able to see your results.
          </p>

          <div style={{ display: "flex", gap: "1rem" }}>
            <button
              onClick={handleDelete}
              disabled={deleting}
              style={{
                background: "var(--red-chalk)",
                border: "1.5px solid var(--red-chalk)",
                color: "var(--board)",
                padding: "0.5rem 1.5rem",
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.85rem",
                letterSpacing: "0.12em",
                textTransform: "uppercase",
                cursor: deleting ? "default" : "pointer",
                opacity: deleting ? 0.5 : 1,
              }}
            >
              {deleting ? "Deleting..." : "Yes, delete"}
            </button>
            <button
              onClick={() => setShowDeleteConfirm(false)}
              disabled={deleting}
              style={{
                background: "transparent",
                border: "1.5px solid var(--tray)",
                color: "var(--chalk)",
                padding: "0.5rem 1.5rem",
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.85rem",
                letterSpacing: "0.12em",
                textTransform: "uppercase",
                cursor: deleting ? "default" : "pointer",
              }}
            >
              Go back
            </button>
          </div>
        </main>
      </div>
    );
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
              fontSize: "1.1rem",
              color: "var(--yellow-chalk)",
            }}
          >
            {remaining}/{parsed.detailedComments.length} remaining
          </span>

          {/* Paper toggle */}
          {hasPaper && (
            <button
              onClick={() => setPaperPanelOpen((v) => !v)}
              style={headerBtnStyle}
            >
              {paperPanelOpen ? "Hide Paper" : "Show Paper"}
            </button>
          )}

          <button onClick={copyLink} style={headerBtnStyle}>
            {copied ? "Copied" : "Share"}
          </button>

          <DownloadMenu markdown={markdown} reviewId={reviewId} model={model} />

          <a
            href="https://github.com/Davidvandijcke/coarse"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              fontFamily: "var(--font-space-mono), monospace",
              fontSize: "1.05rem",
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

      {/* ── Body: paper panel + sidebar + main ────────────── */}
      <div
        style={{
          display: "flex",
          maxWidth: paperPanelOpen ? "100%" : "1100px",
          margin: "0 auto",
          padding: paperPanelOpen ? "0 0 4rem" : "2rem 2rem 4rem",
          gap: paperPanelOpen ? "0" : "2rem",
          transition: "max-width 0.2s",
        }}
      >
        {/* Paper panel */}
        {paperPanelOpen && paperMarkdown && (
          <PaperPanel
            markdown={paperMarkdown}
            highlightQuote={highlightQuote}
            onClose={() => setPaperPanelOpen(false)}
            reviewId={reviewId}
          />
        )}

        {/* Sidebar */}
        <div style={{ padding: paperPanelOpen ? "2rem 0 0 1.5rem" : "0" }}>
          <Sidebar
            parsed={parsed}
            activeId={activeId}
            onNavigate={navigate}
            getStatus={getStatus}
            remaining={remaining}
            filter={filter}
            onFilterChange={setFilter}
          />
        </div>

        {/* Main content */}
        <main
          ref={mainRef}
          className="review-main"
          style={{
            flex: 1,
            minWidth: 0,
            padding: paperPanelOpen ? "2rem 2rem 0 1.5rem" : "0",
          }}
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
            Review of {paperTitle || parsed.title}
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
            {model && (
              <MetaTag label="Model" value={formatModelName(model)} />
            )}
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
                  {preprocessLatex(parsed.overallFeedback.summary)}
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
                    fontSize: "1.1rem",
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
                  style={{ fontSize: "1.05rem", lineHeight: 1.7 }}
                >
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm, remarkMath]}
                    rehypePlugins={[[rehypeKatex, katexOptions]]}
                  >
                    {preprocessLatex(issue.body)}
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
              const cs = getStatus(comment.number);

              // Filter visibility (hide via display:none to preserve scroll)
              const visible = filter === "all" || cs === filter;

              return (
                <div
                  key={comment.number}
                  data-nav-id={cid}
                  style={{ display: visible ? "block" : "none" }}
                >
                  <CommentCard
                    comment={comment}
                    id={cid}
                    commentStatus={cs}
                    onStatusChange={(s) => setStatus(comment.number, s)}
                    onShowInPaper={
                      hasPaper && comment.quote
                        ? () => handleShowInPaper(comment.quote)
                        : undefined
                    }
                  />
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
                  fontSize: "1.1rem",
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
                  fontSize: "1.05rem",
                  letterSpacing: "0.12em",
                  textTransform: "uppercase",
                  cursor: "pointer",
                }}
              >
                {copied ? "Copied" : "Share this review"}
              </button>
            </div>
            <div style={{ marginTop: "1.5rem", textAlign: "right" }}>
              <button
                onClick={() => setShowDeleteConfirm(true)}
                style={{
                  background: "transparent",
                  border: "none",
                  padding: 0,
                  fontFamily: "var(--font-space-mono), monospace",
                  fontSize: "1.05rem",
                  letterSpacing: "0.12em",
                  textTransform: "uppercase",
                  color: "var(--dust)",
                  cursor: "pointer",
                  textDecoration: "underline",
                  textUnderlineOffset: "2px",
                }}
              >
                Delete review
              </button>
            </div>
          </div>
        </main>
      </div>
    </>
  );
}

/* ── Small helpers ──────────────────────────────────────────── */

/** Strip provider prefixes (openrouter/, google/, etc.) and show the model name */
function formatModelName(raw: string): string {
  // e.g. "openrouter/qwen/qwen3.5-plus-02-15" → "qwen/qwen3.5-plus-02-15"
  //      "google/gemini-3-flash-preview"        → "gemini-3-flash-preview"
  const providers = ["openrouter/", "openai/", "anthropic/", "google/", "mistral/", "perplexity/"];
  let name = raw;
  for (const p of providers) {
    if (name.startsWith(p)) {
      name = name.slice(p.length);
      break;
    }
  }
  return name;
}

function MetaTag({ label, value }: { label: string; value: string }) {
  return (
    <span
      style={{
        fontFamily: "var(--font-space-mono), monospace",
        fontSize: "1.1rem",
        letterSpacing: "0.1em",
        textTransform: "uppercase",
      }}
    >
      <span style={{ color: "var(--dust)" }}>{label} </span>
      <span style={{ color: "var(--chalk)" }}>{value}</span>
    </span>
  );
}
