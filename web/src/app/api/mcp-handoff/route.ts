// POST /api/mcp-handoff
//
// Mints a *pair of short-lived capabilities* for handing an already-
// extracted paper off to the user's chat host (Claude.ai, ChatGPT,
// Claude Code, Gemini CLI) via the coarse MCP connector:
//
//   1. A 15-minute Supabase Storage signed URL for the *state blob*
//      (papers/<uuid>.mcp.json), which contains the extracted paper
//      markdown + parsed structure. The host's first MCP tool call
//      is `load_paper_state(signed_state_url, paper_id)`, which
//      downloads and parses this JSON in <1s. No OCR in the host's
//      critical path; no OpenRouter key in the host's context.
//
//   2. A 60-minute single-use `finalize_token` (row in
//      mcp_handoff_tokens) that the MCP server's `finalize_review`
//      tool presents back to /api/mcp-finalize when it's ready to
//      persist the rendered review. Single-write capability scoped
//      to exactly one reviews row.
//
// Precondition: the caller must have already triggered /api/mcp-extract
// for this paper_id. This route refuses to mint capabilities until
// reviews.status has transitioned to 'extracted' (or 'done', for the
// page-reload / re-handoff case after a full round-trip).
//
// The MCP server itself holds zero Supabase credentials in this flow.
// That's the whole point of the capability-based design: the server has
// no ambient authority — it only ever touches state it was explicitly
// handed a capability for.
//
// Threat model: if the clipboard prompt leaks, the attacker can
// download ONE already-extracted state blob for 15 minutes and write
// ONE review into ONE row for 60 minutes. No OpenRouter key exposure,
// no cross-user data, no schema writes. See
// `deploy/migrate_mcp_handoff.sql` for the matching SQL.

import { createClient } from "@supabase/supabase-js";
import { NextRequest, NextResponse } from "next/server";
import { checkRateLimit } from "@/lib/rateLimit";

export const maxDuration = 15;

const STATE_TTL_SECONDS = 15 * 60; // 15 minutes
const FINALIZE_TOKEN_TTL_MINUTES = 60;

function isValidUuid(v: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(v);
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
  const rateLimited = await checkRateLimit(supabase, ip, "mcp-handoff");
  if (rateLimited) return rateLimited;

  let paperId = "";
  try {
    const body = await request.json();
    paperId = (body.paper_id ?? "").trim();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }
  if (!paperId || !isValidUuid(paperId)) {
    return NextResponse.json({ error: "Invalid paper_id" }, { status: 400 });
  }

  // Step 1: verify the review row exists and extraction has completed.
  // 'extracted' is the expected state; 'done' covers the re-handoff case
  // (user clicked "Review with subscription" on an already-completed
  // review — the state blob is still there, mint a fresh capability).
  const { data: reviewRow, error: reviewErr } = await supabase
    .from("reviews")
    .select("id, status, error_message")
    .eq("id", paperId)
    .single();
  if (reviewErr || !reviewRow) {
    return NextResponse.json(
      { error: "Review not found — upload the paper first via /api/presign" },
      { status: 404 },
    );
  }

  if (reviewRow.status === "failed") {
    return NextResponse.json(
      {
        error:
          "Extraction failed for this paper. Upload a new file and try again.",
        details: reviewRow.error_message ?? undefined,
      },
      { status: 409 },
    );
  }
  if (reviewRow.status !== "extracted" && reviewRow.status !== "done") {
    // Client is racing — extraction is still running. Return 409 so the
    // browser knows to keep waiting rather than treat this as a hard
    // failure. The realtime subscription will fire when status flips.
    return NextResponse.json(
      {
        error:
          "Paper is not yet extracted. Trigger /api/mcp-extract first and wait for reviews.status to become 'extracted'.",
        current_status: reviewRow.status,
      },
      { status: 409 },
    );
  }

  // Step 2: mint the signed URL for the extracted state blob. The
  // storage path is `<paper_id>.mcp.json` — written by deploy/modal_worker.py
  // do_extract() when extraction finished. Valid for STATE_TTL_SECONDS.
  const statePath = `${paperId}.mcp.json`;
  const { data: signed, error: signedErr } = await supabase.storage
    .from("papers")
    .createSignedUrl(statePath, STATE_TTL_SECONDS);
  if (signedErr || !signed?.signedUrl) {
    return NextResponse.json(
      {
        error: `Failed to sign state blob URL: ${signedErr?.message ?? "unknown"}. The state blob may not have been written yet — retry in a few seconds.`,
      },
      { status: 500 },
    );
  }

  // Step 3: mint the finalize_token. Single-use, 60-minute expiry.
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

  // Opportunistic cleanup (fire-and-forget) — sweep expired tokens so the
  // table never grows without bound. Runs <1% of calls to keep the
  // handoff route fast; a cron job is an acceptable alternative.
  if (Math.random() < 0.01) {
    void supabase.rpc("cleanup_mcp_handoff_tokens").then(() => {}).catch(() => {});
  }

  // Derive the absolute callback URL the MCP server will POST the rendered
  // review to. NEXT_PUBLIC_SITE_URL → NEXT_PUBLIC_VERCEL_URL → request origin,
  // in that order, so dev (localhost:3000) and prod (coarse.vercel.app) both
  // return a URL the MCP server can reach over the public internet.
  const siteUrl =
    process.env.NEXT_PUBLIC_SITE_URL ??
    (process.env.NEXT_PUBLIC_VERCEL_URL
      ? `https://${process.env.NEXT_PUBLIC_VERCEL_URL}`
      : new URL(request.url).origin);
  const callbackUrl = `${siteUrl.replace(/\/$/, "")}/api/mcp-finalize`;

  return NextResponse.json({
    paper_id: paperId,
    signed_state_url: signed.signedUrl,
    state_ttl_seconds: STATE_TTL_SECONDS,
    finalize_token: tokenRow.token,
    finalize_token_ttl_minutes: FINALIZE_TOKEN_TTL_MINUTES,
    callback_url: callbackUrl,
  });
}
