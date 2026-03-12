"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase";
import type { Review } from "@/lib/types";
import { CharcoalRule, PageMarks } from "@/components/charcoal";

export default function StatusPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [review, setReview] = useState<Review | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const supabase = createClient();

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;

    async function fetchStatus() {
      const { data } = await supabase
        .from("reviews")
        .select("id, status, error_message")
        .eq("id", id)
        .single();

      if (data) {
        setReview(data as Review);
        setLoading(false);
        if (data.status === "done") {
          clearInterval(interval);
          router.push(`/review/${id}`);
        }
      }
    }

    fetchStatus();
    interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, [id, router]);

  function copyLink() {
    navigator.clipboard.writeText(`${window.location.origin}/review/${id}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  const isFailed = review?.status === "failed";
  const isRunning = review?.status === "running";

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

  return (
    <div style={{ background: "var(--paper)", minHeight: "100vh" }}>
      <PageMarks />
      {/* Header */}
      <header
        style={{
          borderBottom: "2px solid var(--ink)",
          padding: "0.875rem 2.5rem",
          display: "flex",
          alignItems: "baseline",
          justifyContent: "space-between",
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
        <div style={{ display: "flex", alignItems: "center", gap: "1.25rem" }}>
          <span
            style={{
              fontFamily: "var(--font-space-mono), monospace",
              fontSize: "0.625rem",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              color: "var(--muted)",
            }}
          >
            {isFailed ? "failed" : isRunning ? "reviewing" : "queued"}
          </span>
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
        </div>
      </header>

      {/* Main */}
      <main
        style={{
          maxWidth: "560px",
          margin: "0 auto",
          padding: "5rem 2.5rem 6rem",
        }}
      >
        {!isFailed ? (
          <>
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
              {isRunning ? "Reading your paper." : "Queued."}
            </h1>

            {/* Scanning line */}
            <div className="scan-track" style={{ marginBottom: "2rem" }} />

            <p
              style={{
                fontFamily: "Georgia, serif",
                fontSize: "1rem",
                lineHeight: 1.65,
                color: "var(--muted)",
                fontStyle: "italic",
                margin: "0 0 0.5rem",
              }}
            >
              {isRunning
                ? "Running the review pipeline (usually 30–60 minutes)."
                : "Your review is queued and will start shortly."}
            </p>

            <p
              style={{
                fontFamily: "Georgia, serif",
                fontSize: "0.875rem",
                color: "var(--muted)",
                margin: "0.25rem 0 0",
                fontStyle: "italic",
              }}
            >
              We&apos;ll email you when it&apos;s done.
            </p>
          </>
        ) : (
          <>
            <h1
              style={{
                fontFamily: "var(--font-playfair), Georgia, serif",
                fontSize: "clamp(2.5rem, 6vw, 4rem)",
                fontStyle: "italic",
                fontWeight: 700,
                lineHeight: 1.1,
                letterSpacing: "-0.02em",
                margin: "0 0 1.5rem",
                color: "var(--accent)",
              }}
            >
              Failed.
            </h1>
            <p
              style={{
                fontFamily: "Georgia, serif",
                fontSize: "0.9375rem",
                lineHeight: 1.65,
                color: "var(--muted)",
                fontStyle: "italic",
                margin: "0 0 1.25rem",
              }}
            >
              {review?.error_message ?? "An unexpected error occurred."}
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
          </>
        )}

        {/* Key box */}
        <div style={{ marginTop: "3.5rem" }}>
          <CharcoalRule />
          <div style={{ padding: "1.5rem 0" }}>
            <p
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.5625rem",
                letterSpacing: "0.18em",
                textTransform: "uppercase",
                color: "var(--muted)",
                margin: "0 0 0.625rem",
              }}
            >
              Your review key — save this
            </p>
            <p
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.9rem",
                color: "var(--ink)",
                wordBreak: "break-all",
                margin: "0 0 0.875rem",
                lineHeight: 1.5,
              }}
            >
              {id}
            </p>
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
              {copied ? "Copied" : "Copy link"}
            </button>
          </div>
          <CharcoalRule />
          <p
            style={{
              fontFamily: "Georgia, serif",
              fontStyle: "italic",
              fontSize: "0.9rem",
              color: "var(--muted)",
              marginTop: "1.25rem",
            }}
          >
            This page will redirect automatically when your review is ready.
          </p>
        </div>
      </main>
    </div>
  );
}
