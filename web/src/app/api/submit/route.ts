import { createClient } from "@supabase/supabase-js";
import { NextRequest, NextResponse } from "next/server";
import nodemailer from "nodemailer";
import { checkRateLimit } from "@/lib/rateLimit";

export const maxDuration = 30;
const MAX_CONCURRENT_REVIEWS = 20;

function escapeHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
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
        error: statusRow.banner_message || "Submissions are temporarily paused. Please try again later or use the CLI: pip install coarse",
      },
      { status: 503 },
    );
  }

  // Count only truly submitted jobs (rows with a matching review_emails record),
  // not presign placeholders that never completed submission.
  const { count: activeReviews, error: activeReviewsError } = await supabaseAdmin
    .from("reviews")
    .select("id, review_emails!inner(review_id)", { count: "exact", head: true })
    .in("status", ["queued", "running"]);

  if (activeReviewsError) {
    return NextResponse.json(
      {
        error: "Unable to verify current system load. Please try again in a few minutes.",
      },
      { status: 503 },
    );
  }

  if ((activeReviews ?? 0) >= MAX_CONCURRENT_REVIEWS) {
    return NextResponse.json(
      {
        error: "We're seeing high traffic right now. Please try again in a few minutes.",
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

  try {
    const body = await request.json();
    id = (body.id ?? "").trim();
    email = (body.email ?? "").trim();
    apiKey = (body.api_key ?? "").trim();
    model = (body.model ?? "").trim();
    storagePath = (body.storage_path ?? "").trim();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (!id || !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id)) {
    return NextResponse.json({ error: "Invalid review ID" }, { status: 400 });
  }
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return NextResponse.json({ error: "Invalid email address" }, { status: 400 });
  }
  if (email.length > 254) {
    return NextResponse.json({ error: "Email too long" }, { status: 400 });
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

  // Store email in separate table (not readable by anon key)
  const { error: emailError } = await supabaseAdmin
    .from("review_emails")
    .insert({ review_id: id, email });
  if (emailError) {
    await supabaseAdmin.from("reviews").delete().eq("id", id);
    return NextResponse.json({ error: "Failed to save contact info" }, { status: 500 });
  }

  // Trigger Modal worker (fire-and-forget — the worker updates Supabase directly)
  const modalUrl = process.env.MODAL_FUNCTION_URL;
  if (modalUrl) {
    fetch(modalUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${process.env.MODAL_WEBHOOK_SECRET ?? ""}`,
      },
      body: JSON.stringify({
        job_id: id,
        pdf_storage_path: storagePath,
        user_api_key: apiKey,
        email,
        model: model || undefined,
      }),
    })
      .then(async (res) => {
        if (!res.ok) {
          await supabaseAdmin
            .from("reviews")
            .update({
              status: "failed",
              error_message:
                "We are seeing high traffic right now. Please try again later or use the command line version.",
            })
            .eq("id", id);
        }
      })
      .catch(async () => {
        await supabaseAdmin
          .from("reviews")
          .update({ status: "failed", error_message: "Failed to start review worker" })
          .eq("id", id);
      });
  }

  // Send confirmation email
  const paperFilename = reviewRow.paper_filename ?? "your paper";
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "https://coarse.vercel.app";
  if (mailer) {
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
