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

export function middleware(request: NextRequest) {
  const previewAuth = previewBasicAuthConfig();
  if (
    previewAuth &&
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
