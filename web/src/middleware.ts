import { NextRequest, NextResponse } from "next/server";

const PREVIEW_BASIC_AUTH_REALM = 'Basic realm="coarse preview", charset="UTF-8"';

function previewBasicAuthConfig() {
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

function previewAuthChallenge() {
  return new NextResponse("Authentication required", {
    status: 401,
    headers: {
      "WWW-Authenticate": PREVIEW_BASIC_AUTH_REALM,
      "Cache-Control": "no-store",
    },
  });
}

// Token-based machine-to-machine endpoints the CLI / Codex-cloud /
// Modal worker hit WITHOUT a browser session. Exempted from the
// preview Basic Auth gate because:
//
//   1. They already enforce token-based auth of their own (single-use
//      handoff token, finalize_token, MCP handoff_secret, Modal
//      webhook secret) — the preview gate would be a redundant layer
//      on capabilities that are already bound to per-submission
//      cryptographic tokens.
//   2. The callers (Codex cloud sandbox, Modal worker) cannot
//      realistically send HTTP Basic Auth credentials, so without
//      this exemption the preview deploy cannot run the CLI /
//      subscription handoff flow end-to-end.
//   3. Vercel's edge-level Deployment Protection (Tier 0.2) is a
//      separate gate addressed by the `x-vercel-protection-bypass`
//      query params appended in `/api/cli-handoff/route.ts`. Exempting
//      these routes from the middleware does NOT open them up past
//      Vercel's own login wall.
//
// Keep this list narrow — broader matches would leak the browser UI
// surface (landing page, /status/*, /review/*) past the preview gate.
const HANDOFF_EXEMPT_PREFIXES = [
  "/h/",
  "/api/mcp-finalize",
  "/api/mcp-extract",
  "/api/mcp-handoff",
];

function isHandoffExemptPath(pathname: string): boolean {
  for (const prefix of HANDOFF_EXEMPT_PREFIXES) {
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
    return previewAuthChallenge();
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
