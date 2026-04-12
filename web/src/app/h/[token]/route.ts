// GET /h/<token>
//
// Serves the CLI handoff bundle to whoever fetches this URL. The URL is
// the one shown to the user in the web form's "Review with Claude Code /
// Codex / Gemini CLI" modal — they paste it into
// `coarse-review --handoff <url>` on their local machine and the
// standalone CLI takes over from there.
//
// Content negotiation:
//
//   - ``Accept: application/json`` (what the CLI sends) → returns the
//     full bundle as JSON:
//     {
//       paper_id,
//       signed_pdf_url,         // 15-min TTL, fresh on every fetch
//       finalize_token,         // same as the URL token
//       callback_url,           // /api/mcp-finalize on this site
//       paper_title,            // from reviews.paper_filename
//     }
//
//   - Anything else (browser) → redirect to the landing page at
//     /h/<token>/page which renders a friendly "paste this command in
//     your terminal" view.
//
// Expired/consumed tokens return 404 to match the existing mcp-finalize
// behavior.

import { createClient } from "@supabase/supabase-js";
import { NextRequest, NextResponse } from "next/server";

export const maxDuration = 15;

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const PDF_SIGNED_URL_TTL_SECONDS = 15 * 60;

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ token: string }> },
) {
  const { token } = await context.params;

  if (!token || !UUID_RE.test(token)) {
    return NextResponse.json({ error: "Invalid token format" }, { status: 400 });
  }

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
  if (!supabaseUrl || !supabaseKey) {
    return NextResponse.json(
      { error: "Server not configured" },
      { status: 503 },
    );
  }
  const supabase = createClient(supabaseUrl, supabaseKey);

  // Step 1: look up the token — it must exist, not be expired, not be consumed.
  const { data: tokenRow, error: tokenErr } = await supabase
    .from("mcp_handoff_tokens")
    .select("token, paper_id, expires_at, consumed_at")
    .eq("token", token)
    .single();

  if (tokenErr || !tokenRow) {
    return NextResponse.json({ error: "Token not found" }, { status: 404 });
  }
  if (tokenRow.consumed_at) {
    return NextResponse.json(
      { error: "Token already consumed — re-trigger the handoff from the web form" },
      { status: 410 },
    );
  }
  if (new Date(tokenRow.expires_at) < new Date()) {
    return NextResponse.json(
      { error: "Token expired — re-trigger the handoff from the web form" },
      { status: 410 },
    );
  }

  // Step 2: look up the review row to get the stored filename, which
  // tells us the storage path (<uuid>.<ext>).
  const { data: reviewRow, error: reviewErr } = await supabase
    .from("reviews")
    .select("id, paper_filename, domain")
    .eq("id", tokenRow.paper_id)
    .single();
  if (reviewErr || !reviewRow) {
    console.error("[/h/token] reviews lookup failed:", {
      paper_id: tokenRow.paper_id,
      reviewErr: reviewErr?.message,
      reviewRow,
    });
    return NextResponse.json(
      { error: "Paper row not found — the upload may have been deleted" },
      { status: 404 },
    );
  }

  const ext = getExtension(reviewRow.paper_filename ?? "");
  if (!ext) {
    return NextResponse.json(
      { error: "Could not derive storage extension from paper_filename" },
      { status: 500 },
    );
  }
  const storagePath = `${tokenRow.paper_id}${ext}`;

  // Step 3: mint a fresh signed download URL for the raw PDF. 15-min TTL.
  const { data: signed, error: signedErr } = await supabase.storage
    .from("papers")
    .createSignedUrl(storagePath, PDF_SIGNED_URL_TTL_SECONDS);
  if (signedErr || !signed?.signedUrl) {
    return NextResponse.json(
      { error: `Failed to sign PDF URL: ${signedErr?.message ?? "unknown"}` },
      { status: 500 },
    );
  }

  const siteUrl =
    process.env.NEXT_PUBLIC_SITE_URL ??
    (process.env.NEXT_PUBLIC_VERCEL_URL
      ? `https://${process.env.NEXT_PUBLIC_VERCEL_URL}`
      : new URL(request.url).origin);
  const callbackUrl = `${siteUrl.replace(/\/$/, "")}/api/mcp-finalize`;

  const bundle = {
    paper_id: tokenRow.paper_id,
    signed_pdf_url: signed.signedUrl,
    finalize_token: tokenRow.token,
    callback_url: callbackUrl,
    paper_title: reviewRow.paper_filename ?? "",
    domain: reviewRow.domain ?? "",
    taxonomy: "",
  };

  // Content negotiation.
  const accept = request.headers.get("accept") ?? "";
  if (accept.includes("application/json") && !accept.includes("text/html")) {
    return NextResponse.json(bundle);
  }

  // Browsers: render an inline landing page with the copy-paste command.
  // No React component — this route can't coexist with a page.tsx in the
  // same directory, so we emit HTML directly.
  const handoffUrl = `${siteUrl.replace(/\/$/, "")}/h/${token}`;
  const html = renderLandingPage({
    handoffUrl,
    paperTitle: reviewRow.paper_filename ?? "your paper",
  });
  return new NextResponse(html, {
    status: 200,
    headers: { "Content-Type": "text/html; charset=utf-8" },
  });
}


function renderLandingPage(args: {
  handoffUrl: string;
  paperTitle: string;
}): string {
  const { handoffUrl, paperTitle } = args;
  const safe = (s: string) =>
    s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

  const setupCmd = `uvx --from 'coarse-ink[mcp] @ git+https://github.com/Davidvandijcke/coarse@feat/mcp-server' coarse install-skills --all --force`;
  const runCmd = `coarse-review --handoff ${handoffUrl}`;

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>coarse — review handoff</title>
  <style>
    :root {
      --board: #0f1115;
      --board-surface: #1a1d24;
      --tray: #2a2f3a;
      --chalk: #d6d3c8;
      --chalk-bright: #f4f0e1;
      --dust: #85847a;
      --yellow-chalk: #d4a843;
      --blue-chalk: #6ea9d4;
    }
    html, body { margin: 0; padding: 0; background: var(--board); color: var(--chalk); font-family: Georgia, serif; }
    main { max-width: 720px; margin: 4rem auto; padding: 0 1.5rem; }
    h1 { font-family: Georgia, serif; font-size: 2rem; color: var(--chalk-bright); margin-bottom: 0.5rem; }
    .subtitle { color: var(--dust); margin-bottom: 2.5rem; }
    .step { margin-bottom: 2rem; }
    .step h2 { font-size: 1.15rem; color: var(--yellow-chalk); margin-bottom: 0.5rem; font-weight: 400; font-family: system-ui, sans-serif; letter-spacing: 0.02em; }
    pre.cmd { background: var(--board-surface); border-left: 3px solid var(--yellow-chalk); padding: 1rem 1.25rem; font-family: 'SF Mono', Menlo, monospace; font-size: 0.9rem; color: var(--chalk-bright); overflow-x: auto; white-space: pre-wrap; word-break: break-all; border-radius: 2px; position: relative; }
    .copy { position: absolute; top: 0.5rem; right: 0.5rem; background: var(--tray); color: var(--chalk-bright); border: 1px solid var(--tray); padding: 0.25rem 0.6rem; font-size: 0.8rem; cursor: pointer; border-radius: 2px; font-family: system-ui, sans-serif; }
    .copy:hover { background: var(--yellow-chalk); color: var(--board); border-color: var(--yellow-chalk); }
    .note { color: var(--dust); font-size: 0.95rem; margin-top: 0.5rem; line-height: 1.5; }
    .note a { color: var(--blue-chalk); text-decoration: none; }
    .note a:hover { text-decoration: underline; }
    footer { margin-top: 4rem; padding-top: 1.5rem; border-top: 1px solid var(--tray); color: var(--dust); font-size: 0.85rem; }
  </style>
</head>
<body>
<main>
  <h1>Review with your subscription</h1>
  <p class="subtitle">Paper: <code>${safe(paperTitle)}</code></p>

  <div class="step">
    <h2>1. One-time setup</h2>
    <pre class="cmd" id="setup"><button class="copy" onclick="copy('setup')">copy</button>${safe(setupCmd)}</pre>
    <p class="note">Installs coarse-ink, prompts for your OpenRouter key (for local OCR extraction — ~$0.10 per paper), and drops the coarse-review skill into your Claude Code / Codex / Gemini CLI skill folders.</p>
  </div>

  <div class="step">
    <h2>2. Run the review</h2>
    <pre class="cmd" id="run"><button class="copy" onclick="copy('run')">copy</button>${safe(runCmd)}</pre>
    <p class="note">This downloads your paper, runs the full coarse pipeline locally using your chosen CLI, and posts the finished review back here. Takes 10–25 minutes. The review will appear at <a href="/" >coarse.vercel.app/review/…</a> when it's done.</p>
    <p class="note"><strong>Options:</strong> add <code>--host claude|codex|gemini</code> (default: first CLI found on PATH), <code>--model &lt;id&gt;</code>, and <code>--effort low|medium|high|max</code>.</p>
  </div>

  <footer>
    Token valid for 60 minutes. Don't have one of the CLIs yet? Install
    <a href="https://claude.ai/download">Claude Code</a>,
    <a href="https://developers.openai.com/codex">Codex</a>, or
    <a href="https://github.com/google-gemini/gemini-cli">Gemini CLI</a>.
  </footer>
</main>

<script>
function copy(id) {
  const pre = document.getElementById(id);
  const text = pre.textContent.replace('copy', '').trim();
  navigator.clipboard.writeText(text).then(() => {
    const btn = pre.querySelector('.copy');
    const orig = btn.textContent;
    btn.textContent = 'copied ✓';
    setTimeout(() => { btn.textContent = orig; }, 1500);
  });
}
</script>
</body>
</html>`;
}

function getExtension(filename: string): string {
  const dot = filename.lastIndexOf(".");
  return dot >= 0 ? filename.slice(dot).toLowerCase() : "";
}
