"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import type { Review } from "@/lib/types";
import { CharcoalRule, PageMarks } from "@/components/charcoal";
import { buildReviewKey, buildReviewPath, buildReviewUrl } from "@/lib/reviewAccess";

export default function StatusPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [review, setReview] = useState<Review | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [copied, setCopied] = useState(false);
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);
  const [cancelling, setCancelling] = useState(false);
  const [accessError, setAccessError] = useState<string | null>(null);
  const token = searchParams.get("token")?.trim() ?? "";
  const hasSecureAccess = token.length > 0;

  useEffect(() => {
    let cancelled = false;
    let interval: ReturnType<typeof setInterval>;

    async function fetchStatus() {
      const res = await fetch(`/api/review/${id}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        cache: "no-store",
      });

      if (cancelled) return;

      if (res.status === 401) {
        setAccessError("This review needs the full secure review link or review key.");
        setLoading(false);
        clearInterval(interval);
        return;
      }
      if (res.status === 404) {
        setNotFound(true);
        setLoading(false);
        clearInterval(interval);
        return;
      }
      if (!res.ok) {
        let message = "Failed to load the review status. Please try again.";
        try {
          const body = (await res.json()) as { error?: string };
          if (body.error) message = body.error;
        } catch {}
        setAccessError(message);
        setLoading(false);
        clearInterval(interval);
        return;
      }

      const data = (await res.json()) as Review;
      setReview(data);
      setLoading(false);
      setNotFound(false);
      setAccessError(null);
      if (data.status === "done") {
        clearInterval(interval);
        if (!cancelled) {
          router.push(buildReviewPath("review", id, token));
        }
      }
      if (data.status === "cancelled") {
          clearInterval(interval);
      }
    }

    fetchStatus();
    interval = setInterval(fetchStatus, 3000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [id, router, token]);

  function copyLink() {
    navigator.clipboard.writeText(
      buildReviewUrl(window.location.origin, "review", id, token),
    );
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  async function handleCancel() {
    setCancelling(true);
    try {
      const res = await fetch("/api/cancel", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ id }),
      });
      if (res.ok) {
        setShowCancelConfirm(false);
        setCancelling(false);
        setReview((prev) =>
          prev
            ? { ...prev, status: "cancelled", error_message: "Review cancelled by user" }
            : prev,
        );
      } else {
        setCancelling(false);
        setShowCancelConfirm(false);
      }
    } catch {
      setCancelling(false);
      setShowCancelConfirm(false);
    }
  }

  const isFailed = review?.status === "failed";
  const isCancelled = review?.status === "cancelled";
  const isRunning = review?.status === "running";
  const isActive = review && !isFailed && !isCancelled && review.status !== "done";

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
            fontSize: "1.1rem",
          }}
        >
          Loading<span className="blink">_</span>
        </span>
      </div>
    );
  }

  if (accessError) {
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
            fontSize: "2rem",
            fontStyle: "italic",
            fontWeight: 700,
            color: "var(--ink)",
            margin: "0 0 1rem",
          }}
        >
          Access token required.
        </p>
        <p
          style={{
            fontFamily: "Georgia, serif",
            fontStyle: "italic",
            color: "var(--muted)",
            fontSize: "1.05rem",
            margin: 0,
          }}
        >
          {accessError}
        </p>
      </div>
    );
  }

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
            fontSize: "2rem",
            fontStyle: "italic",
            fontWeight: 700,
            color: "var(--ink)",
            margin: "0 0 1rem",
          }}
        >
          Review not found.
        </p>
        <p
          style={{
            fontFamily: "Georgia, serif",
            fontStyle: "italic",
            color: "var(--muted)",
            fontSize: "1.05rem",
            margin: 0,
          }}
        >
          Check the review key and try again.
        </p>
      </div>
    );
  }

  // Cancel confirmation screen
  if (showCancelConfirm) {
    return (
      <div style={{ background: "var(--paper)", minHeight: "100vh" }}>
        <PageMarks />
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
            Cancel review?
          </h1>

          <p
            style={{
              fontFamily: "Georgia, serif",
              fontSize: "1rem",
              lineHeight: 1.65,
              color: "var(--muted)",
              fontStyle: "italic",
              margin: "0 0 2.5rem",
            }}
          >
            Are you sure? You will not be able to see your results.
          </p>

          <div style={{ display: "flex", gap: "1rem" }}>
            <button
              onClick={handleCancel}
              disabled={cancelling}
              style={{
                background: "var(--ink)",
                border: "1.5px solid var(--ink)",
                color: "var(--paper)",
                padding: "0.5rem 1.5rem",
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.85rem",
                letterSpacing: "0.12em",
                textTransform: "uppercase",
                cursor: cancelling ? "default" : "pointer",
                opacity: cancelling ? 0.5 : 1,
              }}
            >
              {cancelling ? "Cancelling..." : "Yes, cancel"}
            </button>
            <button
              onClick={() => setShowCancelConfirm(false)}
              disabled={cancelling}
              style={{
                background: "transparent",
                border: "1.5px solid var(--border)",
                color: "var(--ink)",
                padding: "0.5rem 1.5rem",
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.85rem",
                letterSpacing: "0.12em",
                textTransform: "uppercase",
                cursor: cancelling ? "default" : "pointer",
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
              fontSize: "0.85rem",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              color: "var(--muted)",
            }}
          >
            {isCancelled ? "cancelled" : isFailed ? "failed" : isRunning ? "reviewing" : "queued"}
          </span>
          <a
            href="https://github.com/Davidvandijcke/coarse"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              fontFamily: "var(--font-space-mono), monospace",
              fontSize: "0.85rem",
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
        {!isFailed && !isCancelled ? (
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
                fontSize: "1rem",
                color: "var(--muted)",
                margin: "0.25rem 0 0",
                fontStyle: "italic",
              }}
            >
              We&apos;ll email you when it&apos;s done.
            </p>
          </>
        ) : isCancelled ? (
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
              Review cancelled.
            </h1>
            <p
              style={{
                fontFamily: "Georgia, serif",
                fontSize: "1rem",
                lineHeight: 1.65,
                color: "var(--muted)",
                fontStyle: "italic",
                margin: 0,
              }}
            >
              The queued job was marked cancelled. If work had already started,
              the worker may take a little time to wind down.
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
                fontSize: "1.1rem",
                lineHeight: 1.65,
                color: "var(--muted)",
                fontStyle: "italic",
                margin: "0 0 1.25rem",
              }}
            >
              {review?.error_message ?? "An unexpected error occurred."}
            </p>
            <p
              style={{
                fontFamily: "var(--font-chalk)",
                fontSize: "1rem",
                color: "var(--muted)",
                margin: "0 0 1.25rem",
              }}
            >
              Please try resubmitting, or post your issue on the{" "}
              <a
                href="https://github.com/Davidvandijcke/coarse/issues"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "var(--accent)", textDecoration: "underline", textUnderlineOffset: "2px" }}
              >
                Github
              </a>
              .
            </p>
            <a
              href="/"
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.85rem",
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
                fontSize: "0.85rem",
                letterSpacing: "0.18em",
                textTransform: "uppercase",
                color: "var(--muted)",
                margin: "0 0 0.625rem",
              }}
            >
              {hasSecureAccess ? "Your review key — save this" : "Legacy review link"}
            </p>
            <p
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "1.05rem",
                color: "var(--ink)",
                wordBreak: "break-all",
                margin: "0 0 0.875rem",
                lineHeight: 1.5,
              }}
            >
              {hasSecureAccess ? buildReviewKey(id, token) : id}
            </p>
            <button
              onClick={copyLink}
              style={{
                background: "transparent",
                border: "1.5px solid var(--ink)",
                color: "var(--ink)",
                padding: "0.4375rem 1.125rem",
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.85rem",
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
              fontSize: "1.05rem",
              color: "var(--muted)",
              marginTop: "1.25rem",
            }}
          >
            This page will redirect automatically when your review is ready.
          </p>
        </div>

        {/* Cancel review — only show for active (non-failed) reviews */}
        {isActive && hasSecureAccess && (
          <div style={{ marginTop: "2.5rem" }}>
            <button
              onClick={() => setShowCancelConfirm(true)}
              style={{
                background: "transparent",
                border: "none",
                padding: 0,
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.85rem",
                letterSpacing: "0.12em",
                textTransform: "uppercase",
                color: "var(--muted)",
                cursor: "pointer",
                textDecoration: "underline",
                textUnderlineOffset: "2px",
              }}
            >
              Cancel review
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
