import { NextRequest, NextResponse } from "next/server";

const PREVIEW_BASIC_AUTH_REALM = 'Basic realm="coarse preview", charset="UTF-8"';

// Fires once per cold start, not once per request — `previewBasicAuthConfig`
// runs inside the middleware hot path, so the guard is cached at module
// scope to keep request latency unaffected.
let previewVarsLeakedIntoProdWarned = false;

function warnIfPreviewVarsLeakedIntoProduction(): void {
  if (previewVarsLeakedIntoProdWarned) return;
  previewVarsLeakedIntoProdWarned = true;
  if (process.env.VERCEL_ENV !== "production") return;
  const leaked: string[] = [];
  if (process.env.PREVIEW_BASIC_AUTH_PASSWORD?.trim()) {
    leaked.push("PREVIEW_BASIC_AUTH_PASSWORD");
  }
  if (process.env.PREVIEW_BASIC_AUTH_USERNAME?.trim()) {
    leaked.push("PREVIEW_BASIC_AUTH_USERNAME");
  }
  if (process.env.VERCEL_AUTOMATION_BYPASS_SECRET?.trim()) {
    leaked.push("VERCEL_AUTOMATION_BYPASS_SECRET");
  }
  if (leaked.length === 0) return;
  // Loud marker so a release deploy with leaked preview config is
  // obvious in Vercel runtime logs. These vars are no-ops on
  // production (every consumer checks `VERCEL_ENV === "preview"`
  // first), but their presence is a misconfiguration worth alerting
  // on — they almost always mean a Vercel "Apply to all environments"
  // toggle got clicked by accident. See deploy/RELEASE_AUDIT.md.
  console.error(
    `[release-audit] Preview-only environment variables are set on the production deployment: ${leaked.join(", ")}. ` +
      `These are no-ops in production code paths but indicate a dashboard misconfiguration. ` +
      `Audit in Vercel → Project → Settings → Environment Variables and unset them for the Production environment.`,
  );
}

function previewBasicAuthConfig() {
  warnIfPreviewVarsLeakedIntoProduction();
  const password = process.env.PREVIEW_BASIC_AUTH_PASSWORD?.trim();
  if (!password || process.env.VERCEL_ENV !== "preview") {
    return null;
  }

  return {
    username: process.env.PREVIEW_BASIC_AUTH_USERNAME?.trim() || "preview",
    password,
  };
}

function isAuthorizedForPreview(request: NextRequest, expectedUser: string, expectedPassword: string) {
  const header = request.headers.get("authorization");
  if (!header?.startsWith("Basic ")) {
    return false;
  }

  try {
    const decoded = atob(header.slice("Basic ".length));
    const separator = decoded.indexOf(":");
    if (separator === -1) {
      return false;
    }

    const username = decoded.slice(0, separator);
    const password = decoded.slice(separator + 1);
    return username === expectedUser && password === expectedPassword;
  } catch {
    return false;
  }
}

function previewAuthChallenge(pathname: string) {
  // API routes get a JSON body so client-side `fetch().json()` calls
  // don't crash the UI with a `SyntaxError: Unexpected token A in JSON
  // at position 0` when they hit an unauthenticated 401 (for example
  // when the browser's cached Basic Auth header isn't sent on a
  // subresource request). Browser navigations still get the plain
  // text + WWW-Authenticate header that drives the native login
  // prompt. The Accept header would be more idiomatic here but
  // `fetch()` calls from the app don't always set it, and the path
  // prefix is a reliable enough discriminator for the preview gate.
  const isApiRoute = pathname.startsWith("/api/");
  if (isApiRoute) {
    return NextResponse.json(
      { error: "Preview is password-protected. Refresh the browser tab and sign in again, then retry." },
      {
        status: 401,
        headers: {
          "WWW-Authenticate": PREVIEW_BASIC_AUTH_REALM,
          "Cache-Control": "no-store",
        },
      },
    );
  }
  return new NextResponse("Authentication required", {
    status: 401,
    headers: {
      "WWW-Authenticate": PREVIEW_BASIC_AUTH_REALM,
      "Cache-Control": "no-store",
    },
  });
}

// Token-based endpoints that enforce their own auth downstream and
// should therefore skip the preview Basic Auth gate. Three categories:
//
//   1. **Machine-to-machine handoff routes** (`/h/`, `/api/mcp-*`) —
//      the CLI / Codex-cloud sandbox / Modal worker hit these WITHOUT
//      a browser session. They already enforce token-based auth of
//      their own (single-use handoff token, finalize_token, MCP
//      handoff_secret, Modal webhook secret) — the preview gate would
//      be a redundant layer on capabilities already bound to
//      per-submission cryptographic tokens. And the callers cannot
//      realistically send HTTP Basic Auth credentials, so without
//      this exemption the preview deploy cannot run the CLI /
//      subscription handoff flow end-to-end.
//
//   2. **Signed-token review viewing** (`/review/`, `/api/review/`) —
//      users reach these via a per-paper signed URL minted by
//      `mcp-finalize`. `/api/review/[id]` enforces the signed token
//      via `hasValidReviewAccessToken` (`reviewAuth.ts`), and
//      `/review/[id]` is a client-side shell that fetches the API.
//      Anyone who has the signed URL already has capability; gating
//      it again behind Basic Auth just blocks the intended recipient
//      (the user who ran the subscription handoff) from opening the
//      finished review on a preview deploy. Without this exemption
//      the `view:` URL the CLI prints at the end of a successful
//      handoff cannot be opened.
//
//   3. Vercel's edge-level Deployment Protection (Tier 0.2) is a
//      separate gate addressed by the `x-vercel-protection-bypass`
//      query params appended via `appendPreviewBypassQuery` in
//      `/api/cli-handoff` and `/h/[token]`. Exempting these routes
//      from the middleware does NOT open them up past Vercel's own
//      login wall.
//
// Keep this list narrow — broader matches would leak the browser UI
// surface (landing page, /status/*) past the preview gate.
const HANDOFF_EXEMPT_PREFIXES = [
  "/h/",
  "/api/mcp-finalize",
  "/api/mcp-extract",
  "/api/mcp-handoff",
  "/review/",
  "/api/review/",
];

function isHandoffExemptPath(pathname: string): boolean {
  for (const rawPrefix of HANDOFF_EXEMPT_PREFIXES) {
    // Normalize so `"/h/"` and `"/h"` both behave the same: strip a
    // single trailing slash, then match on either the exact path or
    // a proper subpath (prefix + "/" + rest). This avoids the bug
    // where a trailing-slash prefix like `"/h/"` silently composed
    // to `"/h//"` in the `startsWith` arm and never matched any real
    // URL, leaving `/h/<token>` unexempted despite being in the list.
    // The segment-boundary check also prevents `/help` or `/health`
    // from falsely matching the `/h` prefix.
    const prefix = rawPrefix.endsWith("/") ? rawPrefix.slice(0, -1) : rawPrefix;
    if (pathname === prefix || pathname.startsWith(`${prefix}/`)) {
      return true;
    }
  }
  return false;
}

export function middleware(request: NextRequest) {
  const previewAuth = previewBasicAuthConfig();
  if (
    previewAuth &&
    !isHandoffExemptPath(request.nextUrl.pathname) &&
    !isAuthorizedForPreview(request, previewAuth.username, previewAuth.password)
  ) {
    return previewAuthChallenge(request.nextUrl.pathname);
  }

  if (!request.nextUrl.pathname.startsWith("/api/")) {
    return NextResponse.next();
  }

  const origin = request.headers.get("origin");
  const host = request.headers.get("host");

  if (origin) {
    let originHost: string;
    try {
      originHost = new URL(origin).host;
    } catch {
      return NextResponse.json(
        { error: "Invalid origin" },
        { status: 403 },
      );
    }
    if (originHost !== host) {
      return NextResponse.json(
        { error: "Cross-origin requests not allowed" },
        { status: 403 },
      );
    }
  }

  if (request.method === "OPTIONS") {
    return new NextResponse(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": origin ?? "",
        "Access-Control-Allow-Methods": "POST",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Max-Age": "86400",
      },
    });
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|robots.txt|sitemap.xml).*)",
  ],
};
