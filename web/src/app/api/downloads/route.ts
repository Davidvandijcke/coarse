// GET /api/downloads
//
// Serves a shields.io endpoint-format JSON describing the last-month
// PyPI download count for `coarse-ink`. Used by the README badge via
// `img.shields.io/endpoint?url=https://coarse.ink/api/downloads`.
//
// Why this endpoint exists: shields.io's own `/pypi/dm/<pkg>` proxy
// renders "rate limited by upstream service" on the repo page whenever
// shields.io's 24h badge cache expires while pypistats.org happens to
// be throttling the shields.io proxy (frequent on low-traffic packages
// where shields.io's cache warms rarely). We cannot fix that from the
// outside — but we CAN run our own proxy:
//
//   shields.io /endpoint  ->  this route  ->  pypistats
//
// Two caching layers give us bulletproof availability:
//
// 1. Vercel CDN caches this route's response with s-maxage=21600 (6h)
//    + stale-while-revalidate=604800 (7d). shields.io hits the route
//    at most a handful of times per day; everything else is CDN cache.
//
// 2. If pypistats is rate-limited when the CDN revalidates, we throw a
//    500, which Vercel's CDN treats as "revalidation failed" and keeps
//    serving the previous successful response for up to 7 days.
//
// End result: the badge shows the most recent count we have. If
// pypistats is unreachable for 7 consecutive days we'd need another
// fix, but that's well beyond the occasional throttle window the
// default shields.io proxy can't handle.
//
// Excludes mirror traffic (pypistats "recent" returns non-mirror
// counts), so the number is not inflated by bandersnatch replication.

import { NextResponse } from "next/server";

const PYPI_PACKAGE = "coarse-ink";
const PYPISTATS_URL = `https://pypistats.org/api/packages/${PYPI_PACKAGE}/recent`;

// Edge > Node for this since we're just proxying one fetch. Less cold-start
// overhead, faster responses, and Vercel's CDN edge cache pairs cleanly.
export const runtime = "edge";
// Explicit - this route is meant to be cached by Vercel's CDN, not Next.js's
// data cache (which would swallow 429s and serve stale responses at the route
// level instead). We handle SWR via response headers below.
export const dynamic = "force-dynamic";

type ShieldsEndpoint = {
  schemaVersion: 1;
  label: string;
  message: string;
  color: string;
  cacheSeconds?: number;
};

function formatCount(n: number): string {
  if (n >= 1_000_000) {
    return `${(n / 1_000_000).toFixed(1).replace(/\.0$/, "")}M`;
  }
  if (n >= 1_000) {
    return `${(n / 1_000).toFixed(1).replace(/\.0$/, "")}k`;
  }
  return n.toString();
}

function badge(count: number): ShieldsEndpoint {
  return {
    schemaVersion: 1,
    label: "downloads",
    message: `${formatCount(count)}/month`,
    color: "blue",
    cacheSeconds: 21600,
  };
}

export async function GET() {
  let count: number;
  try {
    const resp = await fetch(PYPISTATS_URL, {
      // Bypass Next.js fetch cache - we want Vercel CDN edge cache (below),
      // not Next.js's in-route cache which behaves differently on errors.
      cache: "no-store",
      headers: {
        // pypistats honors a User-Agent; identify ourselves so they can
        // contact us if we misbehave.
        "User-Agent": "coarse-downloads-badge (+https://github.com/Davidvandijcke/coarse)",
      },
    });
    if (!resp.ok) {
      // 429, 5xx, anything non-2xx. Throw so the CDN keeps serving the
      // last successful response via stale-while-revalidate.
      throw new Error(`pypistats ${resp.status}`);
    }
    const data = (await resp.json()) as {
      data?: { last_month?: number };
    };
    const monthly = data?.data?.last_month;
    if (typeof monthly !== "number" || !Number.isFinite(monthly)) {
      throw new Error("unexpected pypistats response shape");
    }
    count = monthly;
  } catch (err) {
    // Return 500 so Vercel's CDN falls back to serving the last stale
    // cache entry (stale-while-revalidate=7d). If there's no cache yet
    // (very first request after deploy), shields.io will render its own
    // generic error - one-off cosmetic blip, next call recovers.
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "upstream unreachable" },
      {
        status: 500,
        headers: {
          // Don't let the error response poison the CDN cache.
          "Cache-Control": "no-store",
        },
      },
    );
  }

  return NextResponse.json(badge(count), {
    headers: {
      "Cache-Control":
        "public, s-maxage=21600, stale-while-revalidate=604800, max-age=0",
      // Tell shields.io its own cache TTL.
      "Content-Type": "application/json; charset=utf-8",
    },
  });
}
