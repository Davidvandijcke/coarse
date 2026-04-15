function normalizeOrigin(rawUrl: string): string | null {
  const trimmed = rawUrl.trim();
  if (!trimmed) return null;
  try {
    return new URL(trimmed).origin.replace(/\/$/, "");
  } catch {
    return null;
  }
}

function configuredSiteOrigin(): string | null {
  const explicitOrigin = normalizeOrigin(process.env.NEXT_PUBLIC_SITE_URL ?? "");
  if (explicitOrigin) return explicitOrigin;

  const vercelUrl = (process.env.NEXT_PUBLIC_VERCEL_URL ?? "").trim();
  if (!vercelUrl) return null;

  return normalizeOrigin(`https://${vercelUrl}`);
}

export function getSiteOriginForRequest(requestUrl: string): string {
  const requestOrigin = normalizeOrigin(requestUrl);
  if (!requestOrigin) {
    return configuredSiteOrigin() ?? "https://coarse.ink";
  }

  // Preview deployments often inherit production-facing defaults such as
  // NEXT_PUBLIC_SITE_URL=coarse.ink. Prefer the concrete preview request
  // origin so generated links stay on the deployment being tested.
  if (process.env.VERCEL_ENV === "preview") {
    return requestOrigin;
  }

  return configuredSiteOrigin() ?? requestOrigin;
}

/**
 * Append the Vercel Protection Bypass for Automation query params to
 * a URL when `VERCEL_ENV === "preview"` and a bypass secret is
 * configured. No-op otherwise, so production URLs stay clean.
 *
 * This is the shared helper used by any route that generates a URL
 * the CLI / Codex-cloud sandbox / Modal worker will fetch WITHOUT a
 * browser session (no SSO cookie, no login wall credential), and
 * needs to get past Vercel's edge-level Deployment Protection.
 *
 * Current call sites:
 *
 *   1. `/api/cli-handoff/route.ts` → handoff URL (`.../h/<token>`)
 *      fetched by the CLI to pull the paper bundle (#121).
 *   2. `/h/[token]/route.ts` → callback URL (`.../api/mcp-finalize`)
 *      POSTed by the CLI to upload the finished review (#127).
 *
 * Both URLs are exempt from the repo-owned Basic Auth middleware
 * (see `HANDOFF_EXEMPT_PREFIXES` in `web/src/middleware.ts` after
 * #122 + #125), but both need this query-param bypass to get past
 * the separate Vercel edge gate when Vercel Authentication or
 * Password Protection is enabled on the preview environment.
 *
 * The `x-vercel-set-bypass-cookie=true` flag is harmless on non-
 * browser clients (Vercel just ignores the set-cookie directive)
 * and lets browsers that follow the URL pick up a bypass cookie for
 * subsequent requests in the same session.
 *
 * Ref: Vercel → Deployment Protection → Protection Bypass for Automation.
 */
export function appendPreviewBypassQuery(url: string): string {
  const bypassSecret = process.env.VERCEL_AUTOMATION_BYPASS_SECRET ?? "";
  if (process.env.VERCEL_ENV !== "preview" || !bypassSecret) {
    return url;
  }
  const separator = url.includes("?") ? "&" : "?";
  return `${url}${separator}x-vercel-protection-bypass=${encodeURIComponent(bypassSecret)}&x-vercel-set-bypass-cookie=true`;
}

export function getVisibleSiteHost(): string {
  if (typeof window !== "undefined" && window.location.host) {
    return window.location.host;
  }

  const origin = configuredSiteOrigin();
  if (!origin) return "this site";

  try {
    return new URL(origin).host;
  } catch {
    return "this site";
  }
}
