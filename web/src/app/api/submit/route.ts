import { createClient } from "@supabase/supabase-js";
import { NextRequest, NextResponse } from "next/server";
import nodemailer from "nodemailer";

export const maxDuration = 30;

const SUPPORTED_EXTENSIONS = new Set([
  ".pdf", ".txt", ".md", ".tex", ".latex",
  ".html", ".htm", ".docx", ".epub",
]);

const MIME_MAP: Record<string, string> = {
  ".pdf": "application/pdf",
  ".txt": "text/plain",
  ".md": "text/markdown",
  ".tex": "text/x-tex",
  ".latex": "text/x-tex",
  ".html": "text/html",
  ".htm": "text/html",
  ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  ".epub": "application/epub+zip",
};

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

function getExtension(filename: string): string {
  const dot = filename.lastIndexOf(".");
  return dot >= 0 ? filename.slice(dot).toLowerCase() : "";
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
  const mailer = getMailer();

  // Parse multipart form
  let pdf: File | null = null;
  let email = "";
  let apiKey = "";
  let model = "";

  try {
    const form = await request.formData();
    pdf = form.get("pdf") as File | null;
    email = ((form.get("email") as string | null) ?? "").trim();
    apiKey = ((form.get("api_key") as string | null) ?? "").trim();
    model = ((form.get("model") as string | null) ?? "").trim();
  } catch {
    return NextResponse.json({ error: "Invalid form data" }, { status: 400 });
  }

  if (!pdf || pdf.size === 0) {
    return NextResponse.json({ error: "No file provided" }, { status: 400 });
  }
  const ext = getExtension(pdf.name);
  if (!SUPPORTED_EXTENSIONS.has(ext)) {
    return NextResponse.json(
      { error: `Unsupported format. Supported: ${[...SUPPORTED_EXTENSIONS].join(", ")}` },
      { status: 400 },
    );
  }
  if (pdf.size > 50 * 1024 * 1024) {
    return NextResponse.json({ error: "File too large (max 50 MB)" }, { status: 400 });
  }
  if (!email || !email.includes("@")) {
    return NextResponse.json({ error: "Invalid email address" }, { status: 400 });
  }
  if (!apiKey) {
    return NextResponse.json({ error: "OpenRouter API key required" }, { status: 400 });
  }

  // Create review record to get the UUID
  const { data: reviewRow, error: insertError } = await supabaseAdmin
    .from("reviews")
    .insert({ paper_filename: pdf.name, status: "queued", model: model || null })
    .select("id")
    .single();

  if (insertError || !reviewRow) {
    return NextResponse.json({ error: "Failed to create review record" }, { status: 500 });
  }

  const id: string = reviewRow.id;

  // Store email in separate table (not readable by anon key)
  const { error: emailError } = await supabaseAdmin
    .from("review_emails")
    .insert({ review_id: id, email });
  if (emailError) {
    await supabaseAdmin.from("reviews").delete().eq("id", id);
    return NextResponse.json({ error: "Failed to save contact info" }, { status: 500 });
  }
  const storagePath = `${id}${ext}`;

  // Upload file to Supabase Storage
  const fileBytes = await pdf.arrayBuffer();
  const { error: uploadError } = await supabaseAdmin.storage
    .from("papers")
    .upload(storagePath, fileBytes, { contentType: MIME_MAP[ext] ?? "application/octet-stream" });

  if (uploadError) {
    await supabaseAdmin.from("reviews").delete().eq("id", id);
    return NextResponse.json({ error: "Failed to upload file" }, { status: 500 });
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
    }).catch(async () => {
      // Worker failed to start — mark as failed in background
      await supabaseAdmin
        .from("reviews")
        .update({ status: "failed", error_message: "Failed to start review worker" })
        .eq("id", id);
    });
  }

  // Send confirmation email
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "https://coarse.vercel.app";
  if (mailer) {
    await mailer.sendMail({
      from: `coarse <${process.env.GMAIL_USER}>`,
      to: email,
      subject: `Your paper "${escapeHtml(pdf.name)}" is being reviewed`,
      html: [
        `<p>Hi,</p>`,
        `<p>Your paper <strong>${escapeHtml(pdf.name)}</strong> is being reviewed. We'll email you when it's done (usually 30–60 minutes).</p>`,
        `<p>Track progress: <a href="${siteUrl}/status/${id}">${siteUrl}/status/${id}</a></p>`,
        `<p><strong>Save your review key:</strong> <code>${id}</code></p>`,
        `<p>— coarse</p>`,
      ].join(""),
    });
  }

  return NextResponse.json({ id });
}
