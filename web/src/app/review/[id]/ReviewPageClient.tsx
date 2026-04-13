"use client";

import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import type { Review } from "@/lib/types";
import { PageMarks } from "@/components/charcoal";
import { parseReview } from "@/lib/parseReview";
import ReviewDisplay from "@/components/ReviewDisplay";

export default function ReviewPageClient({ id }: { id: string }) {
  const [review, setReview] = useState<Review | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [accessError, setAccessError] = useState<string | null>(null);
  const searchParams = useSearchParams();
  const token = searchParams.get("token")?.trim() ?? "";

  useEffect(() => {
    let cancelled = false;
    let interval: ReturnType<typeof setInterval> | undefined;

    async function load() {
      const res = await fetch(`/api/review/${id}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        cache: "no-store",
      });

      if (cancelled) return;

      if (res.status === 401) {
        setAccessError("This review needs the full secure review link or review key.");
        setLoading(false);
        return;
      }
      if (res.status === 404) {
        setNotFound(true);
        setLoading(false);
        return;
      }
      if (!res.ok) {
        setAccessError("Failed to load the review. Please try again.");
        setLoading(false);
        return;
      }

      const data = (await res.json()) as Review;
      setReview(data);
      setLoading(false);
      setNotFound(false);
      setAccessError(null);

      if (data.status !== "queued" && data.status !== "running" && interval) {
        clearInterval(interval);
      }
    }

    load();
    interval = setInterval(load, 3000);

    return () => {
      cancelled = true;
      if (interval) clearInterval(interval);
    };
  }, [id, token]);

  const parsed = useMemo(
    () => (review?.result_markdown ? parseReview(review.result_markdown) : null),
    [review?.result_markdown]
  );

  /* ── Loading ───────────────────────────────────────────── */
  if (loading) {
    return (
      <div
        style={{
          background: "var(--board)",
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
            color: "var(--dust)",
            fontSize: "1.1rem",
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
          background: "var(--board)",
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
            fontFamily: "var(--font-serif)",
            fontSize: "1.625rem",
            fontStyle: "italic",
            fontWeight: 700,
            color: "var(--chalk-bright)",
            margin: "0 0 0.75rem",
          }}
        >
          Review not found.
        </p>
        <p
          style={{
            fontFamily: "Georgia, serif",
            fontStyle: "italic",
            color: "var(--dust)",
            fontSize: "1.1rem",
            margin: "0 0 1.25rem",
          }}
        >
          Check your key and try again.
        </p>
        <a
          href="/"
          style={{
            fontFamily: "var(--font-space-mono), monospace",
            fontSize: "0.85rem",
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            color: "var(--yellow-chalk)",
            textDecoration: "none",
          }}
        >
          Submit a new paper →
        </a>
      </div>
    );
  }

  if (accessError) {
    return (
      <div
        style={{
          background: "var(--board)",
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
            fontFamily: "var(--font-serif)",
            fontSize: "1.625rem",
            fontStyle: "italic",
            fontWeight: 700,
            color: "var(--chalk-bright)",
            margin: "0 0 0.75rem",
          }}
        >
          Access token required.
        </p>
        <p
          style={{
            fontFamily: "Georgia, serif",
            fontStyle: "italic",
            color: "var(--dust)",
            fontSize: "1.1rem",
            margin: "0 0 1.25rem",
          }}
        >
          {accessError}
        </p>
        <a
          href="/"
          style={{
            fontFamily: "var(--font-space-mono), monospace",
            fontSize: "0.85rem",
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            color: "var(--yellow-chalk)",
            textDecoration: "none",
          }}
        >
          Back home →
        </a>
      </div>
    );
  }

  if (!review) return null;

  const isDone = review.status === "done";
  const isPending = review.status === "queued" || review.status === "running";

  /* ── Main render ───────────────────────────────────────── */
  return (
    <div style={{ background: "var(--board)", minHeight: "100vh" }}>
      <PageMarks />

      {/* ── In-progress ─────────────────────────────────── */}
      {isPending && (
        <div style={{ paddingTop: "8rem", textAlign: "center" }}>
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
            {review.status === "running" ? "Reading your paper." : "Queued."}
          </h1>
          <div className="scan-track" style={{ maxWidth: "320px", margin: "0 auto 1.5rem" }} />
          <p
            style={{
              fontFamily: "Georgia, serif",
              fontStyle: "italic",
              color: "var(--dust)",
              fontSize: "1.1rem",
            }}
          >
            {review.status === "running"
              ? "Usually 30\u201360 minutes. This page updates automatically."
              : "Processing begins shortly."}
          </p>
        </div>
      )}

      {/* ── Failed ──────────────────────────────────────── */}
      {review.status === "failed" && (
        <div
          style={{
            maxWidth: "600px",
            margin: "0 auto",
            padding: "6rem 2rem",
          }}
        >
          <div
            style={{
              borderLeft: "3px solid var(--red-chalk)",
              paddingLeft: "1.25rem",
            }}
          >
            <p
              style={{
                fontFamily: "var(--font-serif)",
                fontSize: "1.375rem",
                fontStyle: "italic",
                fontWeight: 700,
                color: "var(--red-chalk)",
                margin: "0 0 0.5rem",
              }}
            >
              Review failed.
            </p>
            <p
              style={{
                fontFamily: "Georgia, serif",
                color: "var(--dust)",
                fontStyle: "italic",
                fontSize: "1.1rem",
                margin: "0 0 1rem",
              }}
            >
              {review.error_message ?? "An unexpected error occurred."}
            </p>
            <a
              href="/"
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.85rem",
                letterSpacing: "0.12em",
                textTransform: "uppercase",
                color: "var(--yellow-chalk)",
                textDecoration: "none",
              }}
            >
              Try again →
            </a>
          </div>
        </div>
      )}

      {review.status === "cancelled" && (
        <div
          style={{
            maxWidth: "600px",
            margin: "0 auto",
            padding: "6rem 2rem",
          }}
        >
          <div
            style={{
              borderLeft: "3px solid var(--yellow-chalk)",
              paddingLeft: "1.25rem",
            }}
          >
            <p
              style={{
                fontFamily: "var(--font-serif)",
                fontSize: "1.375rem",
                fontStyle: "italic",
                fontWeight: 700,
                color: "var(--yellow-chalk)",
                margin: "0 0 0.5rem",
              }}
            >
              Review cancelled.
            </p>
            <p
              style={{
                fontFamily: "Georgia, serif",
                color: "var(--dust)",
                fontStyle: "italic",
                fontSize: "1.1rem",
                margin: "0 0 1rem",
              }}
            >
              {review.error_message ?? "This review was cancelled before completion."}
            </p>
            <a
              href="/"
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.85rem",
                letterSpacing: "0.12em",
                textTransform: "uppercase",
                color: "var(--yellow-chalk)",
                textDecoration: "none",
              }}
            >
              Submit a new paper →
            </a>
          </div>
        </div>
      )}

      {/* ── Done: structured display ────────────────────── */}
      {isDone && review.result_markdown && parsed && (
        <ReviewDisplay
          parsed={parsed}
          markdown={review.result_markdown}
          reviewId={review.id}
          accessToken={token}
          paperMarkdown={review.paper_markdown}
          paperTitle={review.paper_title}
          model={review.model}
          domain={review.domain}
          durationSeconds={review.duration_seconds}
          costUsd={review.cost_usd}
        />
      )}

      {/* Fallback: raw markdown if parsing fails */}
      {isDone && review.result_markdown && !parsed && (
        <div style={{ maxWidth: "780px", margin: "0 auto", padding: "3rem 2.5rem 6rem" }}>
          <article className="review-content">
            <ReactMarkdownFallback markdown={review.result_markdown} />
          </article>
        </div>
      )}
    </div>
  );
}

/* Simple fallback for unparseable reviews */
function ReactMarkdownFallback({ markdown }: { markdown: string }) {
  const ReactMarkdown = require("react-markdown").default;
  const remarkGfm = require("remark-gfm").default;
  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]}>
      {markdown}
    </ReactMarkdown>
  );
}
