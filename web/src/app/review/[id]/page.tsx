"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { createClient } from "@/lib/supabase";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Review } from "@/lib/types";
import { CharcoalRule, PageMarks } from "@/components/charcoal";

export default function ReviewPage() {
  const { id } = useParams<{ id: string }>();
  const [review, setReview] = useState<Review | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [copied, setCopied] = useState(false);
  const [keyVisible, setKeyVisible] = useState(false);
  const supabase = createClient();

  useEffect(() => {
    async function load() {
      const { data } = await supabase
        .from("reviews")
        .select("*")
        .eq("id", id)
        .single();

      if (!data) {
        setNotFound(true);
      } else {
        setReview(data as Review);
      }
      setLoading(false);
    }

    load();

    const channel = supabase
      .channel(`review-${id}`)
      .on(
        "postgres_changes",
        { event: "UPDATE", schema: "public", table: "reviews", filter: `id=eq.${id}` },
        (payload) => {
          setReview((prev) => (prev ? { ...prev, ...payload.new } : null));
        }
      )
      .subscribe();

    return () => { supabase.removeChannel(channel); };
  }, [id]);

  function copyLink() {
    navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  /* ── Loading ───────────────────────────────────────────── */
  if (loading) {
    return (
      <div
        style={{
          background: "var(--paper)",
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <span
          style={{
            fontFamily: "Georgia, serif",
            fontStyle: "italic",
            color: "var(--muted)",
            fontSize: "0.9375rem",
          }}
        >
          Loading<span className="blink">_</span>
        </span>
      </div>
    );
  }

  /* ── Not found ─────────────────────────────────────────── */
  if (notFound) {
    return (
      <div
        style={{
          background: "var(--paper)",
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "2rem",
          textAlign: "center",
        }}
      >
        <p
          style={{
            fontFamily: "var(--font-playfair), Georgia, serif",
            fontSize: "1.625rem",
            fontStyle: "italic",
            fontWeight: 700,
            color: "var(--ink)",
            margin: "0 0 0.75rem",
          }}
        >
          Review not found.
        </p>
        <p
          style={{
            fontFamily: "Georgia, serif",
            fontStyle: "italic",
            color: "var(--muted)",
            fontSize: "0.9375rem",
            margin: "0 0 1.25rem",
          }}
        >
          Check your key and try again.
        </p>
        <a
          href="/"
          style={{
            fontFamily: "var(--font-space-mono), monospace",
            fontSize: "0.6875rem",
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            color: "var(--accent)",
            textDecoration: "none",
          }}
        >
          Submit a new paper →
        </a>
      </div>
    );
  }

  if (!review) return null;

  const isDone = review.status === "done";
  const isPending = review.status === "queued" || review.status === "running";

  /* ── Main render ───────────────────────────────────────── */
  return (
    <div style={{ background: "var(--paper)", minHeight: "100vh" }}>
      <PageMarks />
      {/* ── Header ──────────────────────────────────────── */}
      <header
        style={{
          borderBottom: "2px solid var(--ink)",
          padding: "0.875rem 2.5rem",
          display: "flex",
          alignItems: "baseline",
          justifyContent: "space-between",
          position: "sticky",
          top: 0,
          background: "var(--paper)",
          zIndex: 10,
        }}
      >
        <a
          href="/"
          style={{
            fontFamily: "var(--font-playfair), Georgia, serif",
            fontSize: "1.25rem",
            fontWeight: 700,
            letterSpacing: "-0.02em",
            textDecoration: "none",
            color: "var(--ink)",
          }}
        >
          &lsquo;coarse
        </a>
        <div style={{ display: "flex", alignItems: "center", gap: "1.5rem" }}>
          <a
            href="https://github.com/Davidvandijcke/coarse"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              fontFamily: "var(--font-space-mono), monospace",
              fontSize: "0.5625rem",
              letterSpacing: "0.12em",
              textTransform: "uppercase",
              color: "var(--ink)",
              textDecoration: "none",
              border: "1.5px solid var(--border)",
              padding: "0.375rem 0.875rem",
            }}
          >
            GitHub ↗
          </a>
          {/* Key toggle */}
          <button
            onClick={() => setKeyVisible((v) => !v)}
            style={{
              background: "transparent",
              border: "none",
              fontFamily: "var(--font-space-mono), monospace",
              fontSize: "0.5625rem",
              letterSpacing: "0.12em",
              textTransform: "uppercase",
              color: "var(--muted)",
              cursor: "pointer",
              padding: 0,
            }}
          >
            {keyVisible ? "Hide key" : "Review key"}
          </button>
          {isDone && (
            <button
              onClick={copyLink}
              style={{
                background: "transparent",
                border: "1.5px solid var(--ink)",
                color: "var(--ink)",
                padding: "0.375rem 1rem",
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.5625rem",
                letterSpacing: "0.12em",
                textTransform: "uppercase",
                cursor: "pointer",
              }}
            >
              {copied ? "Copied" : "Copy link"}
            </button>
          )}
        </div>
      </header>

      {/* Collapsible key strip */}
      {keyVisible && (
        <div
          style={{
            background: "var(--light)",
            borderBottom: "1px solid var(--border)",
            padding: "0.875rem 2.5rem",
            display: "flex",
            alignItems: "center",
            gap: "2rem",
          }}
        >
          <span
            style={{
              fontFamily: "var(--font-space-mono), monospace",
              fontSize: "0.5625rem",
              letterSpacing: "0.15em",
              textTransform: "uppercase",
              color: "var(--muted)",
              whiteSpace: "nowrap",
            }}
          >
            Review key
          </span>
          <span
            style={{
              fontFamily: "var(--font-space-mono), monospace",
              fontSize: "0.875rem",
              color: "var(--ink)",
              wordBreak: "break-all",
              flex: 1,
            }}
          >
            {id}
          </span>
        </div>
      )}

      <main
        style={{
          maxWidth: "780px",
          margin: "0 auto",
          padding: "3rem 2.5rem 6rem",
        }}
      >
        {/* ── In-progress ─────────────────────────────────── */}
        {isPending && (
          <div style={{ paddingTop: "4rem", textAlign: "center" }}>
            <h1
              style={{
                fontFamily: "var(--font-playfair), Georgia, serif",
                fontSize: "clamp(2.5rem, 6vw, 4rem)",
                fontStyle: "italic",
                fontWeight: 700,
                lineHeight: 1.1,
                letterSpacing: "-0.02em",
                margin: "0 0 2rem",
                color: "var(--ink)",
              }}
            >
              {review.status === "running" ? "Reading your paper." : "Queued."}
            </h1>
            <div className="scan-track" style={{ maxWidth: "320px", margin: "0 auto 1.5rem" }} />
            <p
              style={{
                fontFamily: "Georgia, serif",
                fontStyle: "italic",
                color: "var(--muted)",
                fontSize: "0.9375rem",
              }}
            >
              {review.status === "running"
                ? "Usually 1–3 minutes. This page updates automatically."
                : "Processing begins shortly."}
            </p>
          </div>
        )}

        {/* ── Failed ──────────────────────────────────────── */}
        {review.status === "failed" && (
          <div
            style={{
              borderLeft: "3px solid var(--accent)",
              paddingLeft: "1.25rem",
              marginTop: "3rem",
            }}
          >
            <p
              style={{
                fontFamily: "var(--font-playfair), Georgia, serif",
                fontSize: "1.375rem",
                fontStyle: "italic",
                fontWeight: 700,
                color: "var(--accent)",
                margin: "0 0 0.5rem",
              }}
            >
              Review failed.
            </p>
            <p
              style={{
                fontFamily: "Georgia, serif",
                color: "var(--muted)",
                fontStyle: "italic",
                fontSize: "0.9375rem",
                margin: "0 0 1rem",
              }}
            >
              {review.error_message ?? "An unexpected error occurred."}
            </p>
            <a
              href="/"
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.6875rem",
                letterSpacing: "0.12em",
                textTransform: "uppercase",
                color: "var(--accent)",
                textDecoration: "none",
              }}
            >
              Try again →
            </a>
          </div>
        )}

        {/* ── Done ────────────────────────────────────────── */}
        {isDone && review.result_markdown && (
          <>
            {/* Paper header */}
            {review.paper_title && (
              <h1
                style={{
                  fontFamily: "var(--font-playfair), Georgia, serif",
                  fontSize: "clamp(1.625rem, 4vw, 2.5rem)",
                  fontWeight: 700,
                  lineHeight: 1.15,
                  letterSpacing: "-0.02em",
                  margin: "0 0 1.25rem",
                  color: "var(--ink)",
                }}
              >
                {review.paper_title}
              </h1>
            )}

            {/* Meta row */}
            <div
              style={{
                display: "flex",
                gap: "2rem",
                flexWrap: "wrap",
                marginBottom: "2rem",
              }}
            >
              {review.domain && (
                <span
                  style={{
                    fontFamily: "var(--font-space-mono), monospace",
                    fontSize: "0.625rem",
                    letterSpacing: "0.12em",
                    textTransform: "uppercase",
                    color: "var(--muted)",
                    borderBottom: "1px solid var(--border)",
                    paddingBottom: "0.125rem",
                  }}
                >
                  {review.domain}
                </span>
              )}
              {review.duration_seconds && (
                <span
                  style={{
                    fontFamily: "var(--font-space-mono), monospace",
                    fontSize: "0.625rem",
                    letterSpacing: "0.1em",
                    color: "var(--muted)",
                  }}
                >
                  {review.duration_seconds}s
                </span>
              )}
              {review.cost_usd && (
                <span
                  style={{
                    fontFamily: "var(--font-space-mono), monospace",
                    fontSize: "0.625rem",
                    letterSpacing: "0.1em",
                    color: "var(--muted)",
                  }}
                >
                  ${Number(review.cost_usd).toFixed(2)}
                </span>
              )}
            </div>

            <CharcoalRule />

            {/* Review article */}
            <article
              className="review-content"
              style={{ marginTop: "2rem" }}
            >
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {review.result_markdown}
              </ReactMarkdown>
            </article>

            {/* Footer */}
            <div style={{ marginTop: "4rem" }}>
              <CharcoalRule />
              <div
                style={{
                  padding: "1.5rem 0",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  flexWrap: "wrap",
                  gap: "1rem",
                }}
              >
                <span
                  style={{
                    fontFamily: "var(--font-playfair), Georgia, serif",
                    fontSize: "1rem",
                    fontStyle: "italic",
                    color: "var(--muted)",
                  }}
                >
                  Generated by{" "}
                  <a
                    href="/"
                    style={{ color: "var(--ink)", textDecoration: "none", fontWeight: 700 }}
                  >
                    &lsquo;coarse
                  </a>
                  . Of course.
                </span>
                <button
                  onClick={copyLink}
                  style={{
                    background: "transparent",
                    border: "1.5px solid var(--ink)",
                    color: "var(--ink)",
                    padding: "0.4375rem 1.125rem",
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
              <CharcoalRule />
            </div>
          </>
        )}
      </main>
    </div>
  );
}
