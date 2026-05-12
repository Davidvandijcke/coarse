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

// Use Next.js ISR — the response rebuilds at most every 6h and Vercel's CDN
// serves the cached rendering to everyone else. On ISR revalidation failure
// (e.g. pypistats throttles us), Vercel serves the stale-but-valid cache.
//
// We deliberately do NOT use `dynamic = "force-dynamic"` or the edge runtime:
// both strip the `s-maxage` + `stale-while-revalidate` directives we rely on
// for graceful-degradation. Default Node runtime + explicit `revalidate` gives
// Next.js full control of edge caching.
export const revalidate = 21600;

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
      // Match the route-level revalidate so Next.js and Vercel agree
      // on the cache window for the pypistats call itself. Avoids a
      // conflict with `revalidate = 21600` above (setting cache:
      // "no-store" on the fetch would force the route dynamic).
      next: { revalidate: 21600 },
      headers: {
        // pypistats honors a User-Agent; identify ourselves so they can
        // contact us if we misbehave.
        "User-Agent":
          "coarse-downloads-badge (+https://github.com/Davidvandijcke/coarse)",
      },
    });
    if (!resp.ok) {
      // 429, 5xx, anything non-2xx. Throw so Next.js/Vercel keep
      // serving the last successful render via stale-while-revalidate.
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
    // cache entry (stale-while-revalidate=7d). The no-store header
    // keeps the error itself out of cache; any previously-cached 2xx
    // keeps serving until either pypistats recovers or 7 days pass.
    // If there's no cache yet (very first request after deploy),
    // shields.io will render its own generic error — one-off cosmetic
    // blip, next call recovers.
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "upstream unreachable" },
      { status: 500, headers: { "Cache-Control": "no-store" } },
    );
  }

  // Explicit Cache-Control belt-and-braces for the Vercel CDN layer.
  // Next.js' route-level `revalidate` sets similar semantics but
  // making them explicit protects against silent framework changes
  // and tells downstream caches (shields.io's own proxy) exactly
  // what we expect.
  return NextResponse.json(badge(count), {
    headers: {
      "Cache-Control":
        "public, s-maxage=21600, stale-while-revalidate=604800",
      "Content-Type": "application/json; charset=utf-8",
      // CDN-Cache-Control targets Vercel's edge specifically, which
      // honors it even when Cache-Control is also present.
      "CDN-Cache-Control":
        "public, s-maxage=21600, stale-while-revalidate=604800",
    },
  });
}
