// POST /api/mcp-extract
//
// Fires the extract-only Modal function (deploy/modal_worker.py →
// do_extract via run_extract) for a paper the user already uploaded
// via /api/presign. This runs the Mistral OCR + structure parsing
// server-side, writes a JSON state blob to papers/<uuid>.mcp.json,
// and flips reviews.status to "extracted" when done.
//
// The browser calls this *only* when the user clicks "Review with my
// subscription" — that click is the explicit signal that the user
// wants the MCP handoff path and is OK spending ~$0.05-0.15 of their
// OpenRouter key on extraction. We deliberately do NOT auto-extract
// on upload because (a) it would charge users who only wanted the
// OpenRouter path, and (b) we want extraction to be user-initiated
// so the button click is the cost-commitment signal.
//
// Request body:
//   { id: uuid, storage_path: "<uuid>.<ext>", api_key: string }
//
// Returns 202 immediately (extraction runs async on Modal); the
// browser watches reviews.status via Supabase realtime to learn when
// the state blob is ready.
//
// Mirrors the auth pattern of /api/submit: same rate limit bucket,
// same Bearer-secret forward to Modal.

import { createClient } from "@supabase/supabase-js";
import { NextRequest, NextResponse } from "next/server";
import {
  buildModalWebhookHostSuffix,
  getModalWebhookConfig,
  type ModalWebhookConfig,
} from "@/lib/modalWebhook";
import { checkRateLimit } from "@/lib/rateLimit";
import { requireReviewHandoffSecret } from "@/lib/routeHandoffAuth";
import { getSubmissionPauseResponse } from "@/lib/systemStatus";

export const maxDuration = 30;

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const STORAGE_PATH_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.(pdf|txt|md|tex|latex|html|htm|docx|epub)$/i;
const MODAL_EXTRACT_HOST_SUFFIXES = [
  buildModalWebhookHostSuffix("coarse-mcp", "run-extract"),
];

export async function POST(request: NextRequest) {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
  if (!supabaseUrl || !supabaseKey) {
    return NextResponse.json(
      { error: "Server not configured — set NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_KEY" },
      { status: 503 },
    );
  }
  const supabaseAdmin = createClient(supabaseUrl, supabaseKey);

  const ip = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ?? "unknown";
  const rateLimited = await checkRateLimit(supabaseAdmin, ip, "mcp-extract");
  if (rateLimited) return rateLimited;
  const paused = await getSubmissionPauseResponse(supabaseAdmin);
  if (paused) return paused;

  let id = "";
  let apiKey = "";
  let storagePath = "";
  let handoffSecret = "";
  try {
    const body = await request.json();
    id = String(body.id ?? "").trim();
    apiKey = String(body.api_key ?? "").trim();
    storagePath = String(body.storage_path ?? "").trim();
    handoffSecret = String(body.handoff_secret ?? "").trim();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (!id || !UUID_RE.test(id)) {
    return NextResponse.json({ error: "Invalid review ID" }, { status: 400 });
  }
  if (!apiKey || apiKey.length > 256) {
    return NextResponse.json(
      { error: "OpenRouter API key required" },
      { status: 400 },
    );
  }
  if (!storagePath || !STORAGE_PATH_RE.test(storagePath)) {
    return NextResponse.json(
      { error: "Invalid storage path" },
      { status: 400 },
    );
  }
  const handoffAuth = await requireReviewHandoffSecret(supabaseAdmin, id, handoffSecret);
  if (!handoffAuth.ok) {
    return NextResponse.json({ error: handoffAuth.error }, { status: handoffAuth.status });
  }

  // Verify the review row exists (and prevent issuing extract for an
  // already-finalized review — the cached state is reusable but we
  // don't want to silently no-op, the browser should know.)
  const { data: reviewRow, error: fetchError } = await supabaseAdmin
    .from("reviews")
    .select("id, status")
    .eq("id", id)
    .single();
  if (fetchError || !reviewRow) {
    return NextResponse.json(
      { error: "Review not found — presign first" },
      { status: 404 },
    );
  }

  // If this paper already has an extracted state blob, short-circuit
  // with a 200 so the browser can proceed straight to /api/mcp-handoff.
  // This is the "user clicked subscription twice" / "page reload"
  // case — no reason to re-run OCR or re-charge the user's key.
  if (reviewRow.status === "extracted" || reviewRow.status === "done") {
    return NextResponse.json({ id, status: reviewRow.status, cached: true });
  }

  let modalWebhookConfig: ModalWebhookConfig | null = null;
  try {
    modalWebhookConfig = getModalWebhookConfig({
      rawUrl: process.env.MODAL_EXTRACT_URL,
      rawSecret: process.env.MODAL_WEBHOOK_SECRET,
      allowedHostSuffixes: MODAL_EXTRACT_HOST_SUFFIXES,
      urlEnvVarName: "MODAL_EXTRACT_URL",
    });
  } catch (error) {
    console.error("Invalid MCP extraction webhook configuration", error);
    return NextResponse.json(
      { error: "Server not configured to start extraction workers" },
      { status: 503 },
    );
  }
  if (!modalWebhookConfig) {
    return NextResponse.json(
      {
        error:
          "MCP extraction worker not configured — set MODAL_EXTRACT_URL to the run_extract endpoint URL from `modal deploy deploy/mcp_server.py` (the coarse-mcp app, separate from coarse-review)",
      },
      { status: 503 },
    );
  }

  // Stage the user's OpenRouter key in `review_secrets` so the Modal
  // worker can read+delete it in one shot without the key ever riding
  // through Modal's spawn() payload. Matches the pattern used by
  // /api/submit for the OpenRouter path. RLS is deny-all on this
  // table; only service_role (what we hold) can insert.
  //
  // Upsert semantics: if a prior attempt already wrote a row for this
  // review_id (e.g. user clicked the button, it failed transiently,
  // they clicked again), overwrite it rather than 23505-failing.
  const { error: secretError } = await supabaseAdmin
    .from("review_secrets")
    .upsert({ review_id: id, user_api_key: apiKey });
  if (secretError) {
    return NextResponse.json(
      { error: "Failed to stage OpenRouter key for extraction" },
      { status: 500 },
    );
  }

  // Fire-and-forget POST to Modal's run_extract endpoint. The body
  // intentionally does NOT include user_api_key — the worker resolves
  // it from review_secrets. This keeps the key out of Modal's
  // managed queue payload, same design as /api/submit.
  fetch(modalWebhookConfig.url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${modalWebhookConfig.secret}`,
    },
    body: JSON.stringify({
      job_id: id,
      pdf_storage_path: storagePath,
    }),
  })
    .then(async (res) => {
      if (!res.ok) {
        // Modal never consumed the staged key — drop the orphaned
        // review_secrets row so the TTL cron doesn't have to sweep it.
        try {
          await supabaseAdmin.from("review_secrets").delete().eq("review_id", id);
        } catch (cleanupErr) {
          console.error(`[${id}] mcp-extract cleanup failed`, cleanupErr);
        }
        await supabaseAdmin
          .from("reviews")
          .update({
            status: "failed",
            error_message:
              "Extraction worker returned non-2xx — check Modal logs.",
          })
          .eq("id", id);
      }
    })
    .catch(async () => {
      try {
        await supabaseAdmin.from("review_secrets").delete().eq("review_id", id);
      } catch (cleanupErr) {
        console.error(`[${id}] mcp-extract catch cleanup failed`, cleanupErr);
      }
      await supabaseAdmin
        .from("reviews")
        .update({
          status: "failed",
          error_message: "Failed to start extraction worker",
        })
        .eq("id", id);
    });

  return NextResponse.json({ id, status: "extracting" }, { status: 202 });
}
