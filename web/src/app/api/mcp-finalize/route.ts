// POST /api/mcp-finalize
//
// Final step of the web→MCP handoff: the MCP server POSTs the rendered
// review markdown + metadata here, authenticated by a single-use
// `finalize_token` minted earlier by /api/mcp-handoff. This route is
// the one place the reviews table gets written to for MCP-driven
// reviews — the MCP server itself never holds a Supabase service key.
//
// Request body:
//   {
//     token: uuid,             // the finalize_token from /api/mcp-handoff
//     paper_id: uuid,          // must match mcp_handoff_tokens.paper_id
//     paper_title: string,     // from the MCP server's extraction
//     domain?: string,         // classified domain
//     taxonomy?: string,       // classified taxonomy
//     markdown: string,        // the rendered review markdown (render_review)
//     paper_markdown?: string, // full paper markdown (for side-by-side view)
//     model?: string,          // model label to attribute the review to
//   }
//
// Contract:
//   - Validates token exists, not expired, not consumed, and its
//     paper_id matches the body's paper_id.
//   - Upserts the reviews row at id = paper_id with the rendered
//     markdown + metadata, flipping status to "done".
//   - Marks the token consumed so it can't be replayed.
//   - Returns { review_url } — the shareable URL the chat host prints.
//
// Security:
//   - Service key stays on the Next.js side. MCP server never sees it.
//   - Token is single-use (consumed_at set before upsert so a concurrent
//     replay sees the row as already consumed).
//   - Expiry enforced at SELECT time (expires_at > now()).
//   - If anything fails after the token is marked consumed, we DO NOT
//     un-consume it — the user has to re-run from the web form to mint
//     a fresh token. That's the safe default: replay is worse than
//     asking the user to retry.
//
// See deploy/migrate_mcp_handoff.sql for the schema.

import { createClient } from "@supabase/supabase-js";
import { NextRequest, NextResponse } from "next/server";
import { checkRateLimit } from "@/lib/rateLimit";

export const maxDuration = 30;

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

function isValidUuid(v: string): boolean {
  return UUID_RE.test(v);
}

// Dangerous HTML tags to strip from the markdown before persisting, in case
// the host LLM wrote a <script> into a comment body. Matches
// src/coarse/synthesis.py._sanitize_html but applied once more here as a
// defense-in-depth measure — the MCP server's synthesis step already does
// the same thing, but we don't want to trust the bytes crossing the
// capability boundary.
const DANGEROUS_HTML = /<\s*\/?\s*(?:script|iframe|object|embed|style|link|form|input|button|textarea|select|meta|base|applet|svg|math)\b[^>]*>/gi;
const EVENT_HANDLER_ATTR = /\bon\w+\s*=/gi;

function scrubMarkdown(md: string): string {
  return md.replace(DANGEROUS_HTML, "").replace(EVENT_HANDLER_ATTR, "");
}

function getExtension(filename: string): string {
  const dot = filename.lastIndexOf(".");
  return dot >= 0 ? filename.slice(dot).toLowerCase() : "";
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
  const rateLimited = await checkRateLimit(supabase, ip, "mcp-finalize");
  if (rateLimited) return rateLimited;

  let body: Record<string, unknown>;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const token = String(body.token ?? "").trim();
  const paperId = String(body.paper_id ?? "").trim();
  const paperTitle = String(body.paper_title ?? "").trim().slice(0, 500);
  const domain = String(body.domain ?? "").trim().slice(0, 128);
  const taxonomy = String(body.taxonomy ?? "").trim().slice(0, 128);
  const markdownRaw = String(body.markdown ?? "");
  const paperMarkdownRaw = String(body.paper_markdown ?? "");
  const model = String(body.model ?? "mcp-host").trim().slice(0, 128);

  if (!token || !isValidUuid(token)) {
    return NextResponse.json({ error: "Invalid token" }, { status: 400 });
  }
  if (!paperId || !isValidUuid(paperId)) {
    return NextResponse.json({ error: "Invalid paper_id" }, { status: 400 });
  }
  if (!markdownRaw || markdownRaw.length < 20) {
    return NextResponse.json(
      { error: "markdown is empty or too short" },
      { status: 400 },
    );
  }
  // Reasonable ceiling: rendered reviews usually run 10-30 KB; cap at 1 MB.
  if (markdownRaw.length > 1_000_000) {
    return NextResponse.json(
      { error: "markdown exceeds 1 MB cap" },
      { status: 413 },
    );
  }
  if (paperMarkdownRaw.length > 4_000_000) {
    return NextResponse.json(
      { error: "paper_markdown exceeds 4 MB cap" },
      { status: 413 },
    );
  }

  const markdown = scrubMarkdown(markdownRaw);
  const paperMarkdown = paperMarkdownRaw ? scrubMarkdown(paperMarkdownRaw) : null;

  // We may need the original upload filename after finalize succeeds so we
  // can delete the source object from Storage immediately instead of waiting
  // for the 24h cleanup cron. The rendered review persists the extracted
  // markdown in `reviews.paper_markdown`, so the raw source file is no
  // longer needed once the review is published.
  const { data: reviewMeta, error: reviewMetaErr } = await supabase
    .from("reviews")
    .select("paper_filename")
    .eq("id", paperId)
    .maybeSingle();

  if (reviewMetaErr) {
    return NextResponse.json(
      { error: `Review lookup failed: ${reviewMetaErr.message}` },
      { status: 500 },
    );
  }

  // Step 1: validate the token. Must exist, not expired, not consumed,
  // and paper_id must match the body to prevent cross-paper replay.
  const { data: tokenRow, error: tokenErr } = await supabase
    .from("mcp_handoff_tokens")
    .select("token, paper_id, expires_at, consumed_at")
    .eq("token", token)
    .maybeSingle();

  if (tokenErr) {
    return NextResponse.json(
      { error: `Token lookup failed: ${tokenErr.message}` },
      { status: 500 },
    );
  }
  if (!tokenRow) {
    return NextResponse.json({ error: "Unknown token" }, { status: 401 });
  }
  if (tokenRow.consumed_at) {
    return NextResponse.json(
      { error: "Token already consumed. Start a new handoff from coarse.vercel.app." },
      { status: 401 },
    );
  }
  if (new Date(tokenRow.expires_at).getTime() < Date.now()) {
    return NextResponse.json(
      { error: "Token expired. Start a new handoff from coarse.vercel.app." },
      { status: 401 },
    );
  }
  if (tokenRow.paper_id !== paperId) {
    return NextResponse.json(
      { error: "Token paper_id does not match request paper_id" },
      { status: 403 },
    );
  }

  // Step 2: mark the token consumed BEFORE writing the review, so a
  // concurrent replay (same token fired twice) races on the UPDATE and
  // only one winner actually writes. We use a conditional UPDATE on
  // consumed_at IS NULL so the second caller sees zero rows affected
  // and gets a clean "already consumed" error.
  const { data: claimed, error: claimErr } = await supabase
    .from("mcp_handoff_tokens")
    .update({ consumed_at: new Date().toISOString() })
    .eq("token", token)
    .is("consumed_at", null)
    .select("token")
    .maybeSingle();

  if (claimErr || !claimed) {
    // A racing replay won the claim — or the DB hiccupped. Either way,
    // tell the caller the token is gone. Don't un-consume on DB errors;
    // the user can retry from the web form.
    return NextResponse.json(
      { error: "Token already consumed (race). Start a new handoff." },
      { status: 401 },
    );
  }

  // Step 3: upsert the reviews row at id = paper_id with the rendered
  // review content. The presign route already inserted the row with
  // status="queued"; we flip it to "done" and fill the result fields.
  const { error: upsertErr } = await supabase
    .from("reviews")
    .update({
      paper_title: paperTitle || undefined,
      domain: domain || undefined,
      model: model || "mcp-host",
      status: "done",
      result_markdown: markdown,
      paper_markdown: paperMarkdown ?? undefined,
      completed_at: new Date().toISOString(),
    })
    .eq("id", paperId);

  if (upsertErr) {
    return NextResponse.json(
      { error: `Failed to write review: ${upsertErr.message}` },
      { status: 500 },
    );
  }

  // Best-effort storage cleanup after a successful finalize. Remove both
  // the original upload (`<paper_id>.<ext>`) and any extracted MCP state
  // blob (`<paper_id>.mcp.json`). If deletion fails, the normal 24h cleanup
  // cron can still sweep the stragglers.
  const storageObjects = [`${paperId}.mcp.json`];
  const sourceExt = getExtension(String(reviewMeta?.paper_filename ?? ""));
  if (sourceExt) {
    storageObjects.unshift(`${paperId}${sourceExt}`);
  }
  try {
    await supabase.storage.from("papers").remove(storageObjects);
  } catch (cleanupErr) {
    console.error("[mcp-finalize] storage cleanup failed", {
      paperId,
      storageObjects,
      cleanupErr,
    });
  }

  // Derive the review URL the same way /api/mcp-handoff does so the dev
  // loop (localhost:3000) and prod (coarse.vercel.app) both return URLs
  // the caller can actually click.
  const siteUrl =
    process.env.NEXT_PUBLIC_SITE_URL ??
    (process.env.NEXT_PUBLIC_VERCEL_URL
      ? `https://${process.env.NEXT_PUBLIC_VERCEL_URL}`
      : new URL(request.url).origin);
  const reviewUrl = `${siteUrl.replace(/\/$/, "")}/review/${paperId}`;

  return NextResponse.json({
    review_id: paperId,
    review_url: reviewUrl,
  });
}
