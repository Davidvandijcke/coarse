import { createClient, type PostgrestError } from "@supabase/supabase-js";
import { NextRequest, NextResponse } from "next/server";
import nodemailer from "nodemailer";
import { checkRateLimit } from "@/lib/rateLimit";
import { isEmailCapacityReached } from "@/lib/emailCapacity";

export const maxDuration = 30;
const MODAL_TRIGGER_TIMEOUT_MS = 10_000;
const MODAL_WEBHOOK_HOST_SUFFIX = "--coarse-review-run-review.modal.run";

function escapeHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function isLocalhost(hostname: string): boolean {
  return hostname === "localhost" || hostname === "127.0.0.1" || hostname === "::1" || hostname === "[::1]";
}

function getModalWebhookConfig(): { url: string; secret: string } | null {
  const rawUrl = process.env.MODAL_FUNCTION_URL?.trim();
  if (!rawUrl) return null;

  let parsed: URL;
  try {
    parsed = new URL(rawUrl);
  } catch {
    throw new Error("MODAL_FUNCTION_URL must be a valid absolute URL");
  }

  const secret = process.env.MODAL_WEBHOOK_SECRET?.trim() ?? "";
  if (!secret) {
    throw new Error("MODAL_WEBHOOK_SECRET must be set when MODAL_FUNCTION_URL is configured");
  }

  if (parsed.protocol === "https:") {
    if (!parsed.hostname.endsWith(MODAL_WEBHOOK_HOST_SUFFIX)) {
      throw new Error(`MODAL_FUNCTION_URL must target *${MODAL_WEBHOOK_HOST_SUFFIX}`);
    }
    return { url: parsed.toString(), secret };
  }

  if (parsed.protocol === "http:" && process.env.NODE_ENV !== "production" && isLocalhost(parsed.hostname)) {
    return { url: parsed.toString(), secret };
  }

  throw new Error("MODAL_FUNCTION_URL must use https (except http://localhost in development)");
}

function getMailer() {
  const user = process.env.GMAIL_USER;
  const pass = process.env.GMAIL_APP_PASSWORD;
  if (!user || !pass) return null;
  return nodemailer.createTransport({
    service: "gmail",
    auth: { user, pass },
  });
}

export async function POST(request: NextRequest) {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_KEY;

  if (!supabaseUrl || !supabaseKey) {
    return NextResponse.json(
      { error: "Server not configured — set NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_KEY in .env.local" },
      { status: 503 }
    );
  }

  let modalWebhookConfig: { url: string; secret: string } | null = null;
  try {
    modalWebhookConfig = getModalWebhookConfig();
  } catch (error) {
    console.error("Invalid Modal webhook configuration", error);
    return NextResponse.json({ error: "Server not configured to start review workers" }, { status: 503 });
  }

  const supabaseAdmin = createClient(supabaseUrl, supabaseKey);

  const ip = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ?? "unknown";
  const rateLimited = await checkRateLimit(supabaseAdmin, ip, "submit");
  if (rateLimited) return rateLimited;

  // Check if submissions are paused (manual kill switch)
  const { data: statusRow } = await supabaseAdmin
    .from("system_status")
    .select("accepting_reviews, banner_message")
    .eq("id", 1)
    .single();

  if (statusRow && !statusRow.accepting_reviews) {
    return NextResponse.json(
      {
        error: statusRow.banner_message || "Submissions are temporarily paused. Please try again later or use the CLI: pip install coarse-ink",
      },
      { status: 503 },
    );
  }

  const mailer = getMailer();

  // Parse JSON body (no file — file was uploaded directly to Supabase via presign)
  let id = "";
  let email = "";
  let apiKey = "";
  let model = "";
  let storagePath = "";
  let authorNotes = "";

  try {
    const body = await request.json();
    id = (body.id ?? "").trim();
    email = (body.email ?? "").trim();
    apiKey = (body.api_key ?? "").trim();
    model = (body.model ?? "").trim();
    storagePath = (body.storage_path ?? "").trim();
    authorNotes = (body.author_notes ?? "").trim();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (!id || !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id)) {
    return NextResponse.json({ error: "Invalid review ID" }, { status: 400 });
  }
  // Email is optional when the daily email-capacity gate is active. Re-check
  // server-side so a client can't bypass the regex by lying about capacity.
  const emailSkipped =
    email.length === 0 && (await isEmailCapacityReached(supabaseAdmin));
  if (!emailSkipped) {
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return NextResponse.json({ error: "Invalid email address" }, { status: 400 });
    }
    if (email.length > 254) {
      return NextResponse.json({ error: "Email too long" }, { status: 400 });
    }
  }
  if (!apiKey) {
    return NextResponse.json({ error: "OpenRouter API key required" }, { status: 400 });
  }
  if (apiKey.length > 256) {
    return NextResponse.json({ error: "API key too long" }, { status: 400 });
  }
  if (model.length > 128) {
    return NextResponse.json({ error: "Model name too long" }, { status: 400 });
  }
  // Author notes are optional. Cap at 2000 chars — long enough for a useful
  // steering paragraph, short enough to not blow up the agent context or
  // provide meaningful room for prompt-injection payloads.
  if (authorNotes.length > 2000) {
    return NextResponse.json({ error: "Author notes too long (max 2000 chars)" }, { status: 400 });
  }
  if (!storagePath) {
    return NextResponse.json({ error: "No storage path provided" }, { status: 400 });
  }
  // Storage path must be UUID.extension (set by presign) — reject anything else
  if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.(pdf|txt|md|tex|latex|html|htm|docx|epub)$/i.test(storagePath)) {
    return NextResponse.json({ error: "Invalid storage path" }, { status: 400 });
  }

  // Verify the review record exists
  const { data: reviewRow, error: fetchError } = await supabaseAdmin
    .from("reviews")
    .select("id, paper_filename, status")
    .eq("id", id)
    .single();

  if (fetchError || !reviewRow) {
    return NextResponse.json({ error: "Review not found — presign first" }, { status: 404 });
  }

  // Update model on the review record
  if (model) {
    await supabaseAdmin.from("reviews").update({ model }).eq("id", id);
  }

  // Mark the reviews row as failed instead of deleting it on mid-submit
  // errors. Previously, the error handlers ran `.delete()`, which created a
  // race: if submit A fails on one of the inserts and rolls back by deleting
  // the reviews row, and submit B (double-click) has already fired its 23505
  // idempotency check and returned 200, the client is redirected to
  // /status/${id} which then 404s because the row is gone. Updating status to
  // 'failed' keeps the row visible so the status page shows the real outcome,
  // and it matches the existing Modal-fetch-failure semantics below.
  const markFailed = async (errorMessage: string) => {
    await supabaseAdmin
      .from("reviews")
      .update({ status: "failed", error_message: errorMessage })
      .eq("id", id);
  };

  // NOTE: ORDER MATTERS. review_emails MUST be inserted before review_secrets.
  // Double-clicks short-circuit on the 23505 unique_violation here, so the
  // review_secrets insert never runs on the duplicate request. If a future
  // refactor reorders these, the double-click protection breaks silently.
  //
  // If this insert raises a Postgres unique_violation (SQLSTATE 23505), the
  // review_id was already submitted — almost always a double-click on the
  // submit button where the browser fires two POSTs with the same presigned
  // id. Treat it as an idempotent success: submit 1 already did all the
  // downstream work (review_secrets insert, Modal fetch, confirmation email),
  // so submit 2 must NOT re-fire the Modal worker (which would race submit 1
  // on the same job_id and leak a second worker). Return 200 with the same id
  // so the client's success handler runs.
  const { error: emailError } = await supabaseAdmin
    .from("review_emails")
    .insert({ review_id: id, email });
  if (emailError) {
    if ((emailError as PostgrestError).code === "23505") {
      return NextResponse.json({ id });
    }
    await markFailed("Failed to save contact info");
    return NextResponse.json({ error: "Failed to save contact info" }, { status: 500 });
  }

  // Store the user's API key in review_secrets (RLS deny-all; only the Modal
  // worker, which uses the service role, can read it). Inserting here — rather
  // than sending the key in the Modal webhook body — keeps the key out of
  // Modal's managed queue payload, which would otherwise persist it until the
  // worker consumed it. The worker reads + deletes the row in one shot via
  // _fetch_and_consume_user_key(); a GitHub Actions cron sweeps any rows older
  // than 3 hours as a safety net.
  const { error: secretError } = await supabaseAdmin
    .from("review_secrets")
    .insert({ review_id: id, user_api_key: apiKey });
  if (secretError) {
    await markFailed("Failed to stage review credentials");
    return NextResponse.json({ error: "Failed to stage review credentials" }, { status: 500 });
  }

  // Trigger Modal worker (fire-and-forget — the worker updates Supabase directly).
  // NOTE: user_api_key is intentionally NOT in the body. The worker resolves it
  // from review_secrets. This keeps the key out of Modal's spawn() payload.
  if (modalWebhookConfig) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), MODAL_TRIGGER_TIMEOUT_MS);
    fetch(modalWebhookConfig.url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${modalWebhookConfig.secret}`,
      },
      signal: controller.signal,
      body: JSON.stringify({
        job_id: id,
        pdf_storage_path: storagePath,
        email,
        model: model || undefined,
        author_notes: authorNotes || undefined,
      }),
    })
      .then(async (res) => {
        if (!res.ok) {
          // Modal never consumed the key — drop it from review_secrets so the
          // orphaned row doesn't sit for up to 3h waiting for the TTL cron.
          try {
            await supabaseAdmin.from("review_secrets").delete().eq("review_id", id);
            await supabaseAdmin
              .from("reviews")
              .update({
                status: "failed",
                error_message:
                  "We are seeing high traffic right now. Please try again later or use the command line version.",
              })
              .eq("id", id);
          } catch (cleanupErr) {
            // Best-effort cleanup — log so stuck rows surface in vercel logs.
            console.error(`[${id}] submit cleanup after !res.ok failed`, cleanupErr);
          }
        }
      })
      .catch(async (fetchErr) => {
        if (fetchErr instanceof Error && fetchErr.name === "AbortError") {
          console.warn(`[${id}] Modal webhook timed out after ${MODAL_TRIGGER_TIMEOUT_MS}ms; delivery status unknown`);
          return;
        }
        // Modal fetch itself rejected — same cleanup as the !res.ok branch.
        try {
          await supabaseAdmin.from("review_secrets").delete().eq("review_id", id);
          await supabaseAdmin
            .from("reviews")
            .update({ status: "failed", error_message: "Failed to start review worker" })
            .eq("id", id);
        } catch (cleanupErr) {
          console.error(`[${id}] submit cleanup after fetch reject failed`, {
            fetchErr,
            cleanupErr,
          });
        }
      })
      .finally(() => {
        clearTimeout(timeoutId);
      });
  }

  // Send confirmation email (only when a real address was provided — the
  // email-capacity gate lets users submit without one).
  const paperFilename = reviewRow.paper_filename ?? "your paper";
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "https://coarse.vercel.app";
  if (mailer && email) {
    await mailer.sendMail({
      from: `coarse <${process.env.GMAIL_USER}>`,
      to: email,
      subject: `Your paper "${escapeHtml(paperFilename)}" is being reviewed`,
      html: [
        `<p>Hi,</p>`,
        `<p>Your paper <strong>${escapeHtml(paperFilename)}</strong> is being reviewed${model ? ` using <strong>${escapeHtml(model)}</strong>` : ""}. We'll email you when it's done (usually 30–60 minutes).</p>`,
        `<p>Track progress: <a href="${siteUrl}/status/${id}">${siteUrl}/status/${id}</a></p>`,
        `<p><strong>Save your review key:</strong> <code>${id}</code></p>`,
        `<p>— coarse</p>`,
      ].join(""),
    });
  }

  return NextResponse.json({ id });
}
