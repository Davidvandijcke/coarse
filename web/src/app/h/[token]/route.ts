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
//       signed_pdf_url,         // 3-hour TTL, fresh on every fetch
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

import { buildHandoffLandingCommands } from "@/lib/mcpHandoff";
import {
  DEFAULT_SUBMISSIONS_PAUSED_MESSAGE,
  getSubmissionPauseState,
} from "@/lib/systemStatus";
import {
  appendPreviewBypassQuery,
  getSiteOriginForRequest,
} from "@/lib/siteOrigin";

export const maxDuration = 15;

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const PDF_SIGNED_URL_TTL_SECONDS = 3 * 60 * 60;

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
  const pauseState = await getSubmissionPauseState(supabase);
  if (!pauseState.accepting) {
    const message =
      pauseState.message ?? DEFAULT_SUBMISSIONS_PAUSED_MESSAGE;
    const accept = request.headers.get("accept") ?? "";
    if (accept.includes("application/json") && !accept.includes("text/html")) {
      return NextResponse.json({ error: message }, { status: 503 });
    }
    return new NextResponse(renderPausedLandingPage(message), {
      status: 503,
      headers: { "Content-Type": "text/html; charset=utf-8" },
    });
  }

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
  // tells us the storage path (<uuid>.<ext>). Also pull `domain` and
  // `taxonomy` so the handoff bundle surfaces whatever metadata was
  // recorded at presign time — `taxonomy` was added to the reviews
  // table by `migrate_mcp_handoff.sql` and is written by `mcp-finalize`
  // when a handoff review completes, so returning it here keeps the
  // column wired end-to-end instead of half-wired (write-only on one
  // side of the handoff, hardcoded empty on the other).
  const { data: reviewRow, error: reviewErr } = await supabase
    .from("reviews")
    .select("id, paper_filename, domain, taxonomy")
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

// Step 3: mint a fresh signed download URL for the original source file.
// Fresh on every fetch, valid for 3 hours so slow/remote coding-agent
// sessions can still finish after the handoff without racing a short TTL.
  const { data: signed, error: signedErr } = await supabase.storage
    .from("papers")
    .createSignedUrl(storagePath, PDF_SIGNED_URL_TTL_SECONDS);
  if (signedErr || !signed?.signedUrl) {
    return NextResponse.json(
      { error: `Failed to sign PDF URL: ${signedErr?.message ?? "unknown"}` },
      { status: 500 },
    );
  }

  const siteUrl = getSiteOriginForRequest(request.url);
  // The callback URL is POSTed by the CLI / Codex-cloud sandbox
  // from outside any browser session, so it has no Vercel SSO
  // cookie and will be blocked by Vercel's edge Deployment
  // Protection on preview deploys unless we append the same
  // Protection Bypass for Automation query params we already
  // append to the handoff URL in `/api/cli-handoff/route.ts`.
  // `appendPreviewBypassQuery` is a no-op on production (it checks
  // `VERCEL_ENV === "preview"` first), so production callback URLs
  // stay clean. Without this, the review runs end-to-end but the
  // final POST from `cli_review.py::_post_finalize` gets 401'd at
  // the Vercel edge and the review URL never lands in the web UI.
  // See `deploy/PREVIEW_ENVIRONMENTS.md::Step 0.3` for the
  // operator-side dashboard step that enables this.
  const baseCallbackUrl = `${siteUrl.replace(/\/$/, "")}/api/mcp-finalize`;
  const callbackUrl = appendPreviewBypassQuery(baseCallbackUrl);

  const bundle = {
    paper_id: tokenRow.paper_id,
    signed_pdf_url: signed.signedUrl,
    finalize_token: tokenRow.token,
    callback_url: callbackUrl,
    paper_title: reviewRow.paper_filename ?? "",
    domain: reviewRow.domain ?? "",
    taxonomy: reviewRow.taxonomy ?? "",
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
    paperId: tokenRow.paper_id,
    siteUrl,
  });
  return new NextResponse(html, {
    status: 200,
    headers: { "Content-Type": "text/html; charset=utf-8" },
  });
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderPausedLandingPage(message: string): string {
  const safeMessage = escapeHtml(message);
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>coarse - submissions paused</title>
  <style>
    :root {
      --board: #0f1115;
      --board-surface: #1a1d24;
      --tray: #2a2f3a;
      --chalk: #d6d3c8;
      --chalk-bright: #f4f0e1;
      --dust: #85847a;
      --red-chalk: #d46e6e;
    }
    html, body { margin: 0; padding: 0; background: var(--board); color: var(--chalk); font-family: Georgia, serif; }
    main { max-width: 720px; margin: 4rem auto; padding: 0 1.5rem; }
    h1 { font-size: 2rem; color: var(--chalk-bright); margin-bottom: 0.75rem; }
    .notice { border-left: 3px solid var(--red-chalk); padding: 1rem 1.25rem; background: var(--board-surface); line-height: 1.7; }
    .note { color: var(--dust); margin-top: 1rem; line-height: 1.6; }
  </style>
</head>
<body>
<main>
  <h1>Submissions are paused</h1>
  <div class="notice">${safeMessage}</div>
  <p class="note">
    New handoffs are blocked until the maintainer resumes the service. If you already started a review,
    your existing status and review pages will keep working.
  </p>
</main>
</body>
</html>`;
}


function renderLandingPage(args: {
  handoffUrl: string;
  paperTitle: string;
  paperId: string;
  siteUrl: string;
}): string {
  const { handoffUrl, paperTitle, paperId, siteUrl } = args;
  const safe = (s: string) => escapeHtml(s);
  const siteHost = (() => {
    try {
      return new URL(siteUrl).host;
    } catch {
      return "this site";
    }
  })();

  // Shared with the browser handoff flow in web/src/app/page.tsx via
  // `buildHandoffLandingCommands` so the two surfaces can't drift on
  // uvx pin, log-file scheme, or attach-command shape. The landing
  // page shows a host-agnostic run command (no --host/--model/--effort
  // appended) because the user edits the command before running to
  // pick their own host; the browser flow uses `buildCliCommands`
  // which appends the flags selected in the modal.
  const { setupCmd, runCmd, attachCmd, logFile } = buildHandoffLandingCommands({
    handoffUrl,
    paperId,
  });

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
    <p class="note">Refreshes the bundled coarse-review skill in your Claude Code / Codex / Gemini CLI skill folders via an ephemeral <code>uvx</code> environment. No permanent install required. coarse needs Python 3.12+, so this command forces the correct interpreter.</p>
  </div>

  <div class="step">
    <h2>2. Launch the review (detached)</h2>
    <pre class="cmd" id="run"><button class="copy" onclick="copy('run')">copy</button>${safe(runCmd)}</pre>
    <p class="note">Starts a detached local review worker, writes its PID to <code>${safe(logFile)}.pid</code>, streams all output to <code>${safe(logFile)}</code>, and returns within 2 seconds. The review will appear at <code>${safe(siteHost)}/review/${safe(paperId)}?token=…</code> when it's done — the <code>view:</code> line in the log has the full tokened URL.</p>
    <p class="note"><strong>Options:</strong> edit the command before running to add <code>--host claude|codex|gemini</code> (default: first CLI found on PATH), <code>--model &lt;id&gt;</code>, and <code>--effort low|medium|high|max</code>.</p>
  </div>

  <div class="step">
    <h2>3. Wait for it to finish (one blocking command)</h2>
    <pre class="cmd" id="attach"><button class="copy" onclick="copy('attach')">copy</button>${safe(attachCmd)}</pre>
    <p class="note">Blocks until the detached worker exits. Streams the log as it's written and prints a <code>[attach] pid=&lt;N&gt; elapsed=&lt;mm:ss&gt; — waiting…</code> heartbeat every 30 seconds of log idleness. Takes 10–25 minutes — run this inside a terminal that can hold an open command, or paste it into your coding agent with a ≥30-minute tool timeout. Safe to Ctrl+C: the watcher detaches but the review keeps running, and you can re-attach with the same command.</p>
    <p class="note">Exit codes: <code>0</code> complete, <code>1</code> failure marker, <code>2</code> silent crash, <code>3</code> missing pidfile, <code>124</code> attach's own 30-min timeout.</p>
  </div>

  <footer>
    Runs locally on your machine using your own Claude Code, Codex, or Gemini CLI account. coarse.ink does not receive or store your provider login, and your provider&apos;s terms, limits, and policies apply.<br>
    Token valid for 3 hours. Don't have one of the CLIs yet? Install
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
