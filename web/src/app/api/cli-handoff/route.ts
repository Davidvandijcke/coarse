// POST /api/cli-handoff
//
// Mints a handoff token for the CLI flow (Claude Code / Codex / Gemini CLI).
// Unlike /api/mcp-handoff, this route does NOT trigger server-side extraction
// — extraction happens locally on the user's machine when they run
// `coarse-review --handoff <url>`. All we need to mint is:
//
//   1. A row in mcp_handoff_tokens (single-use finalize token, 60-min TTL) —
//      the same table the older MCP flow uses, since the finalize semantics
//      are identical.
//
// The GET /h/<token> endpoint then serves the full bundle (paper_id +
// signed PDF download URL + finalize_token + callback_url) to whoever
// hits it with the token, so the CLI doesn't have to persist anything
// between the browser click and the `coarse-review` invocation.
//
// Request body:
//   { paper_id: uuid, host?: "claude" | "codex" | "gemini" }
//
// Response:
//   { token, handoff_url, paper_id }
//
// Security: same threat model as /api/mcp-handoff — a leaked token lets
// an attacker (a) download the paper for 15 minutes and (b) write a
// review to exactly one reviews row for 60 minutes.

import { createClient } from "@supabase/supabase-js";
import { NextRequest, NextResponse } from "next/server";
import { checkRateLimit } from "@/lib/rateLimit";

export const maxDuration = 15;

const FINALIZE_TOKEN_TTL_MINUTES = 60;
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

function isValidUuid(v: string): boolean {
  return UUID_RE.test(v);
}

export async function POST(request: NextRequest) {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
  if (!supabaseUrl || !supabaseKey) {
    return NextResponse.json(
      { error: "Server not configured — set NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_KEY" },
      { status: 503 },
    );
  }
  const supabase = createClient(supabaseUrl, supabaseKey);

  const ip = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ?? "unknown";
  const rateLimited = await checkRateLimit(supabase, ip, "cli-handoff");
  if (rateLimited) return rateLimited;

  let paperId = "";
  let host = "";
  try {
    const body = await request.json();
    paperId = (body.paper_id ?? "").trim();
    host = (body.host ?? "").trim();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }
  if (!paperId || !isValidUuid(paperId)) {
    return NextResponse.json({ error: "Invalid paper_id" }, { status: 400 });
  }

  // Step 1: verify the review row exists. Unlike mcp-handoff, we don't
  // require status='extracted' — the CLI will download the raw PDF and
  // extract locally, so the review row just needs to exist (paper was
  // uploaded via /api/presign).
  const { data: reviewRow, error: reviewErr } = await supabase
    .from("reviews")
    .select("id, paper_filename, status")
    .eq("id", paperId)
    .single();
  if (reviewErr || !reviewRow) {
    return NextResponse.json(
      { error: "Review not found — upload the paper first via /api/presign" },
      { status: 404 },
    );
  }

  // Step 2: mint the finalize_token. Reuse the mcp_handoff_tokens table —
  // the finalize semantics are identical (single-use, 60-min TTL, bound
  // to one paper_id, consumed on POST /api/mcp-finalize).
  const expiresAt = new Date(
    Date.now() + FINALIZE_TOKEN_TTL_MINUTES * 60_000,
  ).toISOString();
  const { data: tokenRow, error: tokenErr } = await supabase
    .from("mcp_handoff_tokens")
    .insert({
      paper_id: paperId,
      expires_at: expiresAt,
    })
    .select("token")
    .single();
  if (tokenErr || !tokenRow) {
    return NextResponse.json(
      { error: `Failed to mint finalize token: ${tokenErr?.message ?? "unknown"}` },
      { status: 500 },
    );
  }

  // Opportunistic cleanup (fire-and-forget).
  if (Math.random() < 0.01) {
    try {
      void supabase.rpc("cleanup_mcp_handoff_tokens");
    } catch {
      // ignore
    }
  }

  // Derive the handoff URL the CLI will fetch from. In production this
  // is coarse.vercel.app (always reachable). In local dev it falls back
  // to the request origin (localhost:3000) — which works when the CLI
  // runs on the same machine but breaks if it runs in a remote sandbox
  // (e.g. Codex cloud). For local dev with remote CLIs, set
  // NEXT_PUBLIC_SITE_URL in .env.local to a tunnel URL.
  let siteUrl =
    process.env.NEXT_PUBLIC_SITE_URL ??
    (process.env.NEXT_PUBLIC_VERCEL_URL
      ? `https://${process.env.NEXT_PUBLIC_VERCEL_URL}`
      : new URL(request.url).origin);

  // If the origin is localhost, try to use the machine's LAN IP so
  // local CLI tools (even those spawned by desktop apps that resolve
  // localhost differently) can reach the dev server.
  if (siteUrl.includes("localhost") || siteUrl.includes("127.0.0.1")) {
    const port = new URL(siteUrl).port || "3000";
    // Use the x-forwarded-host header if behind a proxy, otherwise
    // try the LAN address from the request.
    const forwardedHost = request.headers.get("x-forwarded-host");
    if (forwardedHost && !forwardedHost.includes("localhost")) {
      siteUrl = `https://${forwardedHost}`;
    } else {
      // Keep localhost but note it in the response so the UI can warn.
      siteUrl = `http://localhost:${port}`;
    }
  }

  const handoffUrl = `${siteUrl.replace(/\/$/, "")}/h/${tokenRow.token}`;

  return NextResponse.json({
    token: tokenRow.token,
    paper_id: paperId,
    handoff_url: handoffUrl,
    host: host || null,
    finalize_token_ttl_minutes: FINALIZE_TOKEN_TTL_MINUTES,
    warning: siteUrl.includes("localhost")
      ? "Handoff URL uses localhost — the CLI must run on this same machine. For remote CLIs, set NEXT_PUBLIC_SITE_URL to a public URL."
      : undefined,
  });
}
