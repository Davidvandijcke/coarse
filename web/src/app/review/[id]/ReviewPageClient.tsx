"use client";

import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import type { Review } from "@/lib/types";
import { PageMarks } from "@/components/charcoal";
import { parseReview } from "@/lib/parseReview";
import ReviewDisplay from "@/components/ReviewDisplay";
import { REVIEW_RETURN_TOKEN_KEY } from "@/lib/useOpenRouterKey";
import { SiteLanguageProvider, useSiteLanguageContext, coerceSiteLocale } from "@/lib/i18n";

export default function ReviewPageClient({ id }: { id: string }) {
  // The site-language context must sit ABOVE every consumer (this body + the
  // ReviewDisplay tree), so the provider wraps the body here and the actual
  // page content lives in ReviewPageBody, which reads the context (mirrors
  // page.tsx's PageBody pattern).
  return (
    <SiteLanguageProvider>
      <ReviewPageBody id={id} />
    </SiteLanguageProvider>
  );
}

function ReviewPageBody({ id }: { id: string }) {
  const { t, applyInitialLocale } = useSiteLanguageContext();
  const [review, setReview] = useState<Review | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [accessError, setAccessError] = useState<string | null>(null);
  const searchParams = useSearchParams();
  const urlToken = searchParams.get("token")?.trim() ?? "";
  const stashKey = `${REVIEW_RETURN_TOKEN_KEY}:${id}`;
  // The access token lives in ?token=, but an OpenRouter OAuth redirect (or any
  // reload of a URL that lost the param) can drop it. We stash the token per
  // review in sessionStorage and recover it whenever the URL has none, so a
  // token-gated review stays accessible across reloads within the tab.
  const token = useMemo(() => {
    if (urlToken) return urlToken;
    if (typeof window === "undefined") return "";
    try {
      return window.sessionStorage.getItem(stashKey)?.trim() ?? "";
    } catch {
      return "";
    }
  }, [urlToken, stashKey]);

  // Persist the token (per review) so a later token-less load can recover it.
  useEffect(() => {
    if (!urlToken) return;
    try {
      window.sessionStorage.setItem(stashKey, urlToken);
    } catch {
      /* ignore */
    }
  }, [urlToken, stashKey]);

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
        setAccessError(t("reviewClientAccessErrorNeedsKey"));
        setLoading(false);
        return;
      }
      if (res.status === 404) {
        setNotFound(true);
        setLoading(false);
        return;
      }
      if (!res.ok) {
        let message = t("reviewClientLoadFailed");
        try {
          const body = (await res.json()) as { error?: string };
          if (body.error) message = body.error;
        } catch {}
        setAccessError(message);
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
    // Mount-only poller: `t` is read only inside closures for error text at
    // call time, so it's intentionally omitted from the deps — including it
    // would tear down + re-fetch the poll on every site-language toggle.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, token]);

  // Render a review opened from its email link in the language it was created
  // in, even on a device with no stored preference. The review *content* is
  // already in its language (baked into result_json); this aligns the UI chrome
  // to match. A visitor's explicit choice still wins (see applyInitialLocale).
  useEffect(() => {
    if (!review) return;
    const code =
      review.site_language ||
      review.review_language ||
      review.result_json?.language?.site_language ||
      review.result_json?.language?.review_language ||
      null;
    const locale = coerceSiteLocale(code);
    if (locale) applyInitialLocale(locale);
  }, [review, applyInitialLocale]);

  const parsed = useMemo(
    () =>
      review?.result_markdown
        ? parseReview(review.result_markdown, review.review_language)
        : null,
    [review?.result_markdown, review?.review_language]
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
          {t("reviewClientLoading")}<span className="blink">_</span>
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
          {t("reviewClientNotFoundHeading")}
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
          {t("reviewClientNotFoundBody")}
        </p>
        <a
          href="/"
          style={{
            fontFamily: "var(--font-space-mono), monospace",
            fontSize: "0.92rem",
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            color: "var(--yellow-chalk)",
            textDecoration: "none",
          }}
        >
          {t("reviewClientSubmitNewPaper")}
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
          {t("reviewClientAccessTokenRequired")}
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
            fontSize: "0.92rem",
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            color: "var(--yellow-chalk)",
            textDecoration: "none",
          }}
        >
          {t("reviewClientBackHome")}
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
            {review.status === "running" ? t("reviewClientReadingHeading") : t("reviewClientQueuedHeading")}
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
              ? t("reviewClientRunningBody")
              : t("reviewClientQueuedBody")}
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
              {t("reviewClientFailedHeading")}
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
              {review.error_message ?? t("reviewClientUnexpectedError")}
            </p>
            <a
              href="/"
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.92rem",
                letterSpacing: "0.12em",
                textTransform: "uppercase",
                color: "var(--yellow-chalk)",
                textDecoration: "none",
              }}
            >
              {t("reviewClientTryAgain")}
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
              {t("reviewClientCancelledHeading")}
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
              {review.error_message ?? t("reviewClientCancelledBody")}
            </p>
            <a
              href="/"
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.92rem",
                letterSpacing: "0.12em",
                textTransform: "uppercase",
                color: "var(--yellow-chalk)",
                textDecoration: "none",
              }}
            >
              {t("reviewClientSubmitNewPaper")}
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
          resultJson={review.result_json}
          reviewLanguage={review.review_language ?? review.result_json?.language?.review_language ?? null}
          paperLanguage={review.paper_language ?? review.result_json?.language?.paper_language ?? null}
          textDirectionCol={review.text_direction ?? review.result_json?.language?.text_direction ?? null}
          paperLanguageSource={
            review.paper_language_source ?? review.result_json?.language?.paper_language_source ?? null
          }
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
