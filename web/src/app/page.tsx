"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { useDropzone } from "react-dropzone";
import { useRouter } from "next/navigation";
import { CharcoalRule, HeroMarks } from "@/components/charcoal";
import ModelPicker from "@/components/ModelPicker";
import OpenRouterLoginButton from "@/components/OpenRouterLoginButton";
import { estimateTokensFromPdf, estimateTokensFromText, estimateTokensFromDocx, estimateTokensFromEpub, getModelPricing, estimateReviewCost } from "@/lib/estimateCost";
import { beginLogin, completeLogin, loadStoredKey, saveStoredKey, clearStoredKey } from "@/lib/openrouterAuth";
import {
  type ChatHost,
  type CliHandoffBundle,
  type EffortLevel,
  HOST_LABELS,
  HOST_GLYPHS,
  HOST_CLI_NAME,
  HOST_DEFAULT_MODELS,
  HOST_INSTALL_URL,
  HOST_LAUNCH_LABEL,
  HOST_LAUNCH_HINT,
  buildLaunchUrl,
  EFFORT_LEVELS,
  mintCliHandoff,
  buildCliCommands,
  buildAgentPrompt,
} from "@/lib/mcpHandoff";
import { buildReviewPath, parseReviewLocator } from "@/lib/reviewAccess";
import { getVisibleSiteHost } from "@/lib/siteOrigin";

/* ── Desktop-app platform detection ─────────────────────────
 * The handoff modal's "Open {Host}" buttons dispatch custom URL
 * schemes (claude://, codex://new?prompt=...). Those only work when
 * the *desktop* app is installed and has registered the protocol
 * handler. Linux users with CLI-only installs, mobile visitors, and
 * anyone in a headless browser hit silent failures — the button just
 * does nothing with no feedback. Render the button conditionally: mac
 * and windows only.
 */
function isDesktopAppPlatform(): boolean {
  if (typeof navigator === "undefined") return false;
  const ua = navigator.userAgent || "";
  if (/Android|iPhone|iPad|iPod|Mobile/i.test(ua)) return false;
  return /Macintosh|Mac OS X|Windows/i.test(ua);
}

/* ── Turnstile window API type + helper ───────────────────── */
type TurnstileApi = {
  render: (
    el: HTMLElement,
    opts: {
      sitekey: string;
      callback: (token: string) => void;
      "error-callback"?: () => void;
      "expired-callback"?: () => void;
      theme?: "light" | "dark" | "auto";
    },
  ) => string;
  reset: (widgetId?: string) => void;
  remove: (widgetId?: string) => void;
};
function getTurnstileApi(): TurnstileApi | undefined {
  if (typeof window === "undefined") return undefined;
  return (window as unknown as { turnstile?: TurnstileApi }).turnstile;
}

/* ── Split-flap AI name display ────────────────────────────── */
const AI_NAMES = ["Claude,", "Gemini,", "Qwen,", "ChatGPT,", "DeepSeek,", "Kimi,", "Grok,", "MiniMax,", "Mistral,", "Llama,"];
const CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

function SplitFlap() {
  const [index, setIndex] = useState(0);
  const [display, setDisplay] = useState(AI_NAMES[0]);

  useEffect(() => {
    const cycle = setInterval(() => {
      setIndex((i) => (i + 1) % AI_NAMES.length);
    }, 2600);
    return () => clearInterval(cycle);
  }, []);

  useEffect(() => {
    const target = AI_NAMES[index];
    const maxLen = Math.max(...AI_NAMES.map((w) => w.length));
    let tick = 0;
    const steps = 14;
    const scramble = setInterval(() => {
      tick++;
      setDisplay(
        target
          .padEnd(maxLen)
          .split("")
          .map((ch, i) => {
            const settled = tick > steps - (maxLen - i) * 1.1;
            if (settled || ch === " ") return ch;
            return CHARSET[Math.floor(Math.random() * CHARSET.length)];
          })
          .join("")
      );
      if (tick >= steps) clearInterval(scramble);
    }, 45);
    return () => clearInterval(scramble);
  }, [index]);

  return (
    <span
      style={{
        fontFamily: "var(--font-space-mono), monospace",
        display: "inline-block",
        minWidth: "8ch",
        color: "var(--yellow-chalk)",
        letterSpacing: "0.05em",
      }}
    >
      {display}
    </span>
  );
}

/* ── Copy-to-clipboard code block ────────────────────────── */
function CodeBlock({ text, maxHeight }: { text: string; maxHeight?: string }) {
  const [copied, setCopied] = useState(false);
  // Wrap the scroll area in a relative container so the copy button
  // can be absolutely positioned over the top-right and stay visible
  // regardless of scroll position.
  return (
    <div style={{ position: "relative" }}>
      <button
        type="button"
        onClick={() => {
          navigator.clipboard.writeText(text).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 1500);
          }).catch(() => {});
        }}
        style={{
          position: "absolute",
          top: "0.4rem",
          right: "0.4rem",
          zIndex: 2,
          background: copied ? "var(--yellow-chalk)" : "var(--tray)",
          color: copied ? "var(--board)" : "var(--chalk-bright)",
          border: "none",
          borderRadius: "2px",
          padding: "0.2rem 0.55rem",
          fontSize: "0.92rem",
          fontFamily: "var(--font-chalk)",
          cursor: "pointer",
          transition: "background 0.15s, color 0.15s",
        }}
      >
        {copied ? "copied ✓" : "copy"}
      </button>
      <div
        style={{
          background: "var(--board)",
          border: "1px solid var(--tray)",
          borderLeft: "2px solid var(--yellow-chalk)",
          borderRadius: "2px",
          padding: "0.65rem 0.85rem",
          paddingRight: "4.5rem",
          fontFamily: "var(--font-space-mono), monospace",
          fontSize: "0.9rem",
          color: "var(--chalk-bright)",
          lineHeight: 1.5,
          maxHeight: maxHeight ?? undefined,
          overflowY: maxHeight ? "auto" : undefined,
          overflowX: "auto",
          whiteSpace: "pre-wrap",
          wordBreak: "break-word",
        }}
      >
        {text}
      </div>
    </div>
  );
}

/* ── Header ───────────────────────────────────────────────── */
function Header() {
  return (
    <header
      style={{
        padding: "1rem 2.5rem",
        display: "flex",
        alignItems: "baseline",
        justifyContent: "space-between",
        background: "var(--board)",
      }}
    >
      <div style={{ display: "flex", alignItems: "baseline", gap: "1.25rem" }}>
        <span
          style={{
            fontFamily: "var(--font-serif)",
            fontSize: "1.25rem",
            fontWeight: 400,
            letterSpacing: "-0.01em",
            color: "var(--chalk-bright)",
          }}
        >
          &lsquo;coarse
        </span>
        <span
          style={{
            fontFamily: "var(--font-chalk)",
            fontSize: "1.1rem",
            color: "var(--dust)",
          }}
        >
          peer review is a public good.
        </span>
      </div>
      <div style={{ display: "flex", alignItems: "baseline", gap: "1.5rem" }}>
        <a
          href="/setup"
          style={{
            fontFamily: "var(--font-chalk)",
            fontSize: "1.05rem",
            color: "var(--dust)",
            textDecoration: "none",
            transition: "color 0.2s",
          }}
        >
          setup
        </a>
        <a
          href="/compare"
          style={{
            fontFamily: "var(--font-chalk)",
            fontSize: "1.05rem",
            color: "var(--dust)",
            textDecoration: "none",
            transition: "color 0.2s",
          }}
        >
          side-by-side
        </a>
        <a
          href="https://github.com/Davidvandijcke/coarse"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            fontFamily: "var(--font-chalk)",
            fontSize: "1.05rem",
            color: "var(--dust)",
            textDecoration: "none",
            transition: "color 0.2s",
          }}
        >
          github ↗
        </a>
      </div>
    </header>
  );
}

/* ── Label above a field ───────────────────────────────────── */
function FieldLabel({ children }: { children: React.ReactNode }) {
  return (
    <span
      style={{
        display: "block",
        fontFamily: "var(--font-chalk)",
        fontSize: "1.15rem",
        color: "var(--dust)",
        marginBottom: "0.5rem",
      }}
    >
      {children}
    </span>
  );
}

/* ── Page ──────────────────────────────────────────────────── */
export default function Home() {
  const router = useRouter();
  const siteHost = getVisibleSiteHost();
  const [file, setFile] = useState<File | null>(null);
  const [email, setEmail] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [model, setModel] = useState("anthropic/claude-opus-4.6");
  const [authorNotes, setAuthorNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [keyNotice, setKeyNotice] = useState<string | null>(null);
  const [lookupKey, setLookupKey] = useState("");
  const [costEstimate, setCostEstimate] = useState<number | null>(null);
  const [costLoading, setCostLoading] = useState(false);
  const tokenCacheRef = useRef<{ name: string; size: number; tokens: number } | null>(null);
  const oauthConsumedRef = useRef(false);
  const turnstileSiteKey = process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY;
  const turnstileTokenRef = useRef<string>("");
  const turnstileContainerRef = useRef<HTMLDivElement | null>(null);
  const turnstileWidgetIdRef = useRef<string | undefined>(undefined);
  // 'loading' while the Cloudflare script is fetching or the widget
  // hasn't fired its success callback yet. 'ready' once a token has
  // been captured. 'failed' when the script 404s, Cloudflare reports
  // a widget error, or the widget never produces a token within its
  // initial budget — typically because a browser privacy extension
  // (Brave Shields, uBlock Origin with certain lists, Firefox ETP
  // strict) is blocking challenges.cloudflare.com. Drives whether
  // the submit button is enabled and what message we show.
  const [turnstileStatus, setTurnstileStatus] = useState<"loading" | "ready" | "failed">(
    turnstileSiteKey ? "loading" : "ready",
  );
  const [systemStatus, setSystemStatus] = useState<{
    accepting: boolean; banner: string | null; activeReviews: number; capacity: number;
    emailCapacityReached?: boolean;
  } | null>(null);
  const refreshSystemStatus = useCallback(() => {
    fetch("/api/status", { cache: "no-store" })
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        // Shape-guard the response before committing to state. On preview
        // deploys behind the password gate, an unauthenticated 401 from
        // the middleware returns `{error: "Preview is password-protected..."}`
        // — a different shape from the expected `{accepting, message, ...}`
        // body. Without this guard, the banner gate downstream reads
        // `!data.accepting` as `true` (because `undefined !== false`) and
        // renders a bogus "Submissions are temporarily paused" message.
        if (data && typeof data.accepting === "boolean") {
          setSystemStatus(data);
        }
      })
      .catch(() => {});
  }, []);

  // CLI handoff state machine:
  //
  //   idle → extracting → ready
  //           │
  //           └─► failed
  //
  //  - idle: user hasn't clicked the subscription button yet
  //  - extracting: presign + upload + /api/cli-handoff in flight
  //  - ready: clipboard prompt and host launch affordances are ready
  //  - failed: upload or handoff errored; show error in form
  type HandoffPhase = "idle" | "extracting" | "ready" | "failed";
  const [mcpPickerOpen, setMcpPickerOpen] = useState(false);
  const [handoffPhase, setHandoffPhase] = useState<HandoffPhase>("idle");
  const [handoffState, setHandoffState] = useState<{
    paperId: string; host: ChatHost;
  } | null>(null);
  const [handoffMessage, setHandoffMessage] = useState<string>("");
  const [handoffBundle, setHandoffBundle] = useState<CliHandoffBundle | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [selectedEffort, setSelectedEffort] = useState<EffortLevel>("high");
  const [launchStatus, setLaunchStatus] = useState<string>("");

  // Refresh system capacity state on mount and when the tab becomes active.
  useEffect(() => {
    refreshSystemStatus();

    const handleFocus = () => {
      refreshSystemStatus();
    };
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        refreshSystemStatus();
      }
    };
    const intervalId = window.setInterval(refreshSystemStatus, 30000);

    window.addEventListener("focus", handleFocus);
    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      window.clearInterval(intervalId);
      window.removeEventListener("focus", handleFocus);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [refreshSystemStatus]);

  // Render the Cloudflare Turnstile widget once its script has loaded. The
  // <Script strategy="afterInteractive"> tag in layout.tsx pulls the API
  // asynchronously, so window.turnstile may not exist yet on first effect
  // run — retry with a small backoff until it shows up. Bounded at ~7.5s
  // so a failed CDN fetch doesn't poll forever. Also runs a 12s watchdog
  // after the widget renders: if no token callback fires in that window
  // the widget is almost certainly being blocked by a browser privacy
  // extension (Brave Shields, uBlock, ETP strict) — flip to 'failed' so
  // we can show the user a clear explanation + CLI fallback instead of
  // leaving them staring at an empty box. No-op entirely when
  // NEXT_PUBLIC_TURNSTILE_SITE_KEY is unset.
  useEffect(() => {
    if (!turnstileSiteKey) return;
    const container = turnstileContainerRef.current;
    if (!container) return;

    let cancelled = false;
    let retryTimer: number | undefined;
    let watchdogTimer: number | undefined;
    let retries = 0;
    const MAX_RETRIES = 50; // 50 * 150ms = 7.5s

    const markFailed = (reason: string) => {
      if (cancelled) return;
      console.error(`Turnstile: ${reason}`);
      turnstileTokenRef.current = "";
      setTurnstileStatus("failed");
    };

    const tryRender = () => {
      if (cancelled) return;
      const api = getTurnstileApi();
      if (!api) {
        retries += 1;
        if (retries >= MAX_RETRIES) {
          markFailed("api.js failed to load within 7.5s");
          return;
        }
        retryTimer = window.setTimeout(tryRender, 150);
        return;
      }
      if (turnstileWidgetIdRef.current !== undefined) return;
      // Clear the container defensively so a React-strict-mode mount→
      // unmount→mount doesn't stack two widgets if the cleanup path's
      // api.remove(widgetId) fails silently.
      container.innerHTML = "";
      try {
        turnstileWidgetIdRef.current = api.render(container, {
          sitekey: turnstileSiteKey,
          callback: (token: string) => {
            if (cancelled) return;
            turnstileTokenRef.current = token;
            setTurnstileStatus("ready");
            if (watchdogTimer !== undefined) {
              window.clearTimeout(watchdogTimer);
              watchdogTimer = undefined;
            }
          },
          "error-callback": () => {
            markFailed("widget error-callback fired (likely hostname mismatch or blocked iframe)");
          },
          "expired-callback": () => {
            // Token expired — back to loading while Cloudflare auto-
            // refreshes. Don't flip to 'failed'; this is a normal
            // lifecycle event after ~5 minutes of widget idle time.
            if (cancelled) return;
            turnstileTokenRef.current = "";
            setTurnstileStatus("loading");
          },
          theme: "dark",
        });
      } catch (err) {
        markFailed(`render threw: ${err instanceof Error ? err.message : String(err)}`);
        return;
      }
      // Watchdog: if the widget doesn't deliver a token within 12s,
      // treat it as failed. Covers the case where Cloudflare's iframe
      // is blocked from loading but api.render itself didn't throw.
      watchdogTimer = window.setTimeout(() => {
        if (turnstileTokenRef.current === "") {
          markFailed("no token after 12s — widget likely blocked by a browser extension");
        }
      }, 12_000);
    };
    tryRender();

    return () => {
      cancelled = true;
      if (retryTimer !== undefined) window.clearTimeout(retryTimer);
      if (watchdogTimer !== undefined) window.clearTimeout(watchdogTimer);
      const api = getTurnstileApi();
      const widgetId = turnstileWidgetIdRef.current;
      if (api && widgetId !== undefined) {
        try {
          api.remove(widgetId);
        } catch {
          /* best-effort; happens if the script was torn down first */
        }
      }
      turnstileWidgetIdRef.current = undefined;
      turnstileTokenRef.current = "";
    };
  }, [turnstileSiteKey]);

  // Reset the Turnstile widget so the next submission gets a fresh,
  // single-use token. Always called from handleSubmit's finally block —
  // the token is consumed server-side on every presign attempt (success
  // or failure), so a retry always needs a fresh one. Turnstile
  // auto-refreshes the widget after reset in managed mode, so the next
  // token lands in the ref within ~1s. While it's refreshing, flip the
  // status back to 'loading' so the submit button stays disabled until
  // the new token is captured (prevents the user spam-clicking against
  // an empty ref). Preserves 'failed' — resetting a broken widget
  // doesn't make it un-broken. No-op when Turnstile is disabled.
  const resetTurnstile = useCallback(() => {
    turnstileTokenRef.current = "";
    setTurnstileStatus((prev) => (prev === "failed" ? "failed" : "loading"));
    const api = getTurnstileApi();
    if (api) {
      try {
        api.reset(turnstileWidgetIdRef.current);
      } catch {
        /* best-effort */
      }
    }
  }, []);

  // Hydrate a tab-scoped OpenRouter key and handle OAuth callback (?code=...).
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    const { key: stored, migratedFromLocalStorage } = loadStoredKey();

    if (migratedFromLocalStorage) {
      setKeyNotice(
        "Moved your saved OpenRouter key into tab-only storage. It will clear when you close this tab.",
      );
    }

    if (!code) {
      if (stored) setApiKey(stored);
      return;
    }

    if (oauthConsumedRef.current) return;
    oauthConsumedRef.current = true;
    // Strip ?code= immediately so a mid-flight reload won't re-submit a consumed code.
    window.history.replaceState({}, "", window.location.pathname);

    completeLogin(code)
      .then((key) => {
        setApiKey(key);
        setKeyNotice(null);
        try {
          saveStoredKey(key);
        } catch {
          setError(
            "Logged in, but couldn't keep the key in this tab. You'll need to paste it again if this page reloads.",
          );
        }
      })
      .catch((err) => {
        console.error("OpenRouter login failed", err);
        setError("OpenRouter login failed. Please try again or paste a key manually.");
        if (stored) setApiKey(stored);
      });
  }, []);

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted[0]) setFile(accepted[0]);
  }, []);

  // Compute cost estimate when file or model changes
  useEffect(() => {
    if (!file) { setCostEstimate(null); return; }
    let cancelled = false;
    setCostLoading(true);

    (async () => {
      try {
        // Cache token count so model switches don't re-parse the file
        let tokens: number;
        const ext = file.name.toLowerCase().split(".").pop();
        const cached = tokenCacheRef.current;
        if (cached && cached.name === file.name && cached.size === file.size) {
          tokens = cached.tokens;
        } else {
          if (ext === "pdf") {
            tokens = await estimateTokensFromPdf(file);
          } else if (ext === "docx") {
            tokens = await estimateTokensFromDocx(file);
          } else if (ext === "epub") {
            tokens = await estimateTokensFromEpub(file);
          } else {
            tokens = await estimateTokensFromText(file);
          }
          tokenCacheRef.current = { name: file.name, size: file.size, tokens };
        }

        const pricing = await getModelPricing(model);
        if (cancelled) return;

        if (pricing) {
          // Pass modelId for reasoning-model overhead detection and
          // isPdf to gate the extraction_qa stage — matches the Python
          // cost gate's behavior in build_cost_estimate().
          setCostEstimate(estimateReviewCost(tokens, pricing, model, ext === "pdf"));
        } else {
          setCostEstimate(null);
        }
      } catch (err) {
        console.error("Cost estimation failed:", err);
        if (!cancelled) setCostEstimate(null);
      } finally {
        if (!cancelled) setCostLoading(false);
      }
    })();

    return () => { cancelled = true; };
  }, [file, model]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "text/plain": [".txt"],
      "text/markdown": [".md"],
      "text/x-tex": [".tex", ".latex"],
      "text/html": [".html", ".htm"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "application/epub+zip": [".epub"],
    },
    maxSize: 50 * 1024 * 1024,
    maxFiles: 1,
  });

  /**
   * Extract a user-readable error message from a non-2xx Response.
   *
   * Assumes JSON by convention (every /api/* route returns JSON on
   * error) but falls back to text if the body isn't valid JSON. Most
   * importantly, this never throws a SyntaxError on the caller: when
   * a middleware layer returns a plain-text 401 (preview Basic Auth
   * on an unauthenticated fetch, for example) the old code crashed
   * with "Unexpected token A in JSON" and surfaced that cryptic
   * message as the submit error. Now we pick a clean human-readable
   * fallback keyed on the status code.
   */
  async function readApiError(resp: Response, fallback: string): Promise<string> {
    const rawBody = await resp.text().catch(() => "");
    if (rawBody) {
      try {
        const parsed = JSON.parse(rawBody) as { error?: unknown };
        if (parsed && typeof parsed.error === "string" && parsed.error.trim()) {
          return parsed.error;
        }
      } catch {
        // Body wasn't JSON — fall through to the plain-text path.
      }
    }
    if (resp.status === 401 || resp.status === 403) {
      return (
        "Authentication failed. On preview deploys this usually means the " +
        "browser's cached Basic Auth credentials didn't get sent on the " +
        "form submit. Refresh the tab (Cmd/Ctrl+Shift+R), sign in again at " +
        "the password prompt, and retry."
      );
    }
    if (resp.status === 503) {
      // Every app-emitted 503 is JSON with an `error` field and is
      // handled by the earlier branch. This fallback fires only on
      // infra-level 503s (Vercel edge, CDN interstitial), where the
      // body is an HTML error page or a stack trace. We don't want
      // to render raw HTML in an error message, so return a fixed
      // string instead of exposing `rawBody`.
      return "Service temporarily unavailable — please try again in a minute.";
    }
    return `${fallback} (HTTP ${resp.status})`;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (handoffPhase !== "idle") return;
    if (!file || !apiKey) return;
    if (!email && !(systemStatus?.emailCapacityReached === true)) return;
    setSubmitting(true);
    setError(null);
    try {
      // Step 1: Get a presigned upload URL (small JSON request — no file)
      const turnstileToken = turnstileTokenRef.current;
      if (turnstileSiteKey && !turnstileToken) {
        if (turnstileStatus === "failed") {
          throw new Error(
            "Our human-check widget couldn't load — a browser extension " +
              "(Brave Shields, uBlock Origin, Firefox ETP strict) is most " +
              "likely blocking challenges.cloudflare.com. Try disabling it " +
              `for ${siteHost}, or run coarse locally: uvx coarse-ink review paper.pdf`,
          );
        }
        throw new Error(
          "Still waiting for the human check to load — give it a second and try again.",
        );
      }
      const presignResp = await fetch("/api/presign", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: file.name, turnstile_token: turnstileToken }),
      });
      if (!presignResp.ok) {
        throw new Error(await readApiError(presignResp, "Failed to prepare upload"));
      }
      const { id, storagePath, signedUrl, token, handoffSecret, accessToken } = await presignResp.json();

      // Step 2: Upload file directly to Supabase Storage (bypasses Vercel 4.5MB limit)
      const uploadResp = await fetch(signedUrl, {
        method: "PUT",
        headers: {
          "Content-Type": file.type || "application/octet-stream",
          "x-upsert": "true",
        },
        body: file,
      });
      if (!uploadResp.ok) {
        throw new Error("File upload failed — please try again");
      }

      // Step 3: Submit metadata (no file — just JSON)
      const submitResp = await fetch("/api/submit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          id,
          email,
          api_key: apiKey,
          model,
          storage_path: storagePath,
          author_notes: authorNotes || undefined,
          handoff_secret: handoffSecret,
        }),
      });
      if (!submitResp.ok) {
        throw new Error(await readApiError(submitResp, "Submission failed"));
      }
      router.push(buildReviewPath("status", id, accessToken));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Submission failed");
      setSubmitting(false);
    } finally {
      // Turnstile tokens are single-use per siteverify call, so reset
      // after every attempt (success or failure). Placed in finally so
      // it runs exactly once per submit regardless of which step threw.
      resetTurnstile();
    }
  }

  /**
   * Route this review to one of the user's local coding-agent hosts using the
   * CLI handoff flow.
   *
   * The browser uploads the source file, receives a paper-scoped handoff URL,
   * copies the review prompt to the clipboard, and then lets the local
   * `coarse-review --handoff ...` command do extraction and finalization on the
   * user's machine with the user's own OpenRouter key and coding-agent
   * subscription.
   */
  async function handleMcpHandoff(host: ChatHost) {
    if (!file) return;
    if (handoffPhase === "extracting") return;
    // Reset any previous handoff so the user can switch hosts.
    resetHandoff();
    setError(null);
    setMcpPickerOpen(false);
    setHandoffPhase("extracting");
    setHandoffMessage("Uploading paper...");
    setHandoffBundle(null);

    try {
      // Step 1: presign + upload (same path as the OpenRouter flow).
      // `/api/presign` enforces Turnstile server-side and returns 403
      // "Human check failed..." on a missing or invalid token, so the
      // handoff path has to feed through the same widget-ready check +
      // token handoff as `handleSubmit`. This mirrors `handleSubmit`'s
      // Turnstile block verbatim so the two paths stay aligned.
      const turnstileToken = turnstileTokenRef.current;
      if (turnstileSiteKey && !turnstileToken) {
        if (turnstileStatus === "failed") {
          throw new Error(
            "Our human-check widget couldn't load — a browser extension " +
              "(Brave Shields, uBlock Origin, Firefox ETP strict) is most " +
              "likely blocking challenges.cloudflare.com. Try disabling it " +
              `for ${siteHost}, or run coarse locally: uvx coarse-ink review paper.pdf`,
          );
        }
        throw new Error(
          "Still waiting for the human check to load — give it a second and try again.",
        );
      }
      const presignResp = await fetch("/api/presign", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: file.name, turnstile_token: turnstileToken }),
      });
      if (!presignResp.ok) {
        throw new Error(await readApiError(presignResp, "Failed to prepare upload"));
      }
      const { id, signedUrl, handoffSecret } = await presignResp.json();

      const uploadResp = await fetch(signedUrl, {
        method: "PUT",
        headers: {
          "Content-Type": file.type || "application/octet-stream",
          "x-upsert": "true",
        },
        body: file,
      });
      if (!uploadResp.ok) {
        throw new Error("File upload failed — please try again");
      }

      // Step 2: mint CLI handoff token. No server-side extraction — the
      // user's local `coarse-review` command downloads the raw PDF and
      // does Mistral OCR locally with their own OpenRouter key, then
      // POSTs the rendered review back to /api/mcp-finalize.
      setHandoffMessage("Preparing handoff...");
      const bundle = await mintCliHandoff(id, host, handoffSecret);

      // Step 3: defaults for the modal dropdowns.
      setSelectedModel(HOST_DEFAULT_MODELS[host][0]);
      setSelectedEffort("high");

      setHandoffBundle(bundle);
      setHandoffState({ paperId: id, host });
      setHandoffPhase("ready");
      setHandoffMessage("");
    } catch (err) {
      setHandoffPhase("failed");
      const msg = err instanceof Error ? err.message : "Handoff failed";
      setError(msg);
      setHandoffMessage("");
    } finally {
      // Turnstile tokens are single-use per siteverify call — same
      // contract as the OpenRouter submit path — so reset after every
      // attempt so the widget can auto-refresh a fresh token for the
      // next click. Without this the second handoff click would 403
      // with "Human check failed".
      resetTurnstile();
    }
  }

  /**
   * Primary launch action: copy the run command to the clipboard,
   * then open the host's web interface (if it has one) in a new tab.
   *
   * The clipboard write MUST happen synchronously inside the click
   * handler or browsers will block it. The new-tab open then fires
   * after the clipboard write; if it fails (popup blocker, no web
   * equivalent) we fall back silently — the clipboard copy still
   * worked, which is the actually-important part.
   */
  async function handleLaunch() {
    if (!handoffBundle || !handoffState) return;
    const host = handoffState.host;
    const { setupCmd, runCmd, attachCmd, logFile } = buildCliCommands({
      handoffUrl: handoffBundle.handoff_url,
      host,
      model: selectedModel,
      effort: selectedEffort,
      paperId: handoffState.paperId,
    });

    // Copy the full prompt to clipboard (fallback for hosts that can't
    // receive prompts via URL scheme — currently Claude Code and Gemini).
    const fullPrompt = buildAgentPrompt({ setupCmd, runCmd, attachCmd, logFile });
    try {
      await navigator.clipboard.writeText(fullPrompt);
    } catch (err) {
      console.error("clipboard write failed", err);
    }

    // Custom URL schemes (claude://, codex://...) fail silently when the
    // desktop handler isn't registered. The browser gives no feedback and
    // the button appears to do nothing. Detect this with a 2.5s visibility
    // timer: if the OS never switches focus to another app, the scheme
    // didn't resolve and we swap in a "didn't work — paste the commands
    // instead" hint so the user isn't stuck.
    const launchUrl = buildLaunchUrl({ host, runCmd, setupCmd, attachCmd, logFile });
    if (!launchUrl) {
      setLaunchStatus("Command copied to clipboard. Paste it into your terminal.");
      return;
    }

    let becameHidden = false;
    const onVis = () => {
      if (document.visibilityState === "hidden") becameHidden = true;
    };
    document.addEventListener("visibilitychange", onVis);
    window.location.href = launchUrl;
    setLaunchStatus(
      host === "codex"
        ? "Opening Codex desktop app — the composer should pre-fill. Hit send."
        : `Opening ${HOST_LABELS[host]} — paste the prompt from your clipboard (⌘V / Ctrl+V).`,
    );
    setTimeout(() => {
      document.removeEventListener("visibilitychange", onVis);
      if (!becameHidden) {
        setLaunchStatus(
          `${HOST_LABELS[host]} desktop app didn't open. If you only have the CLI ` +
            `version installed, paste the commands above into your terminal instead.`,
        );
      }
    }, 2500);
  }

  function resetHandoff() {
    setHandoffPhase("idle");
    setHandoffBundle(null);
    setHandoffState(null);
    setHandoffMessage("");
    setLaunchStatus("");
  }

  const accepting = systemStatus?.accepting !== false;
  const emailDisabled = systemStatus?.emailCapacityReached === true;
  // When Turnstile is enabled, require a ready widget before we enable
  // submit so the user isn't clicking against a form that's guaranteed
  // to throw. In the 'failed' branch the submit button stays disabled
  // and the widget slot shows a clear explanation + CLI fallback.
  const turnstileReadyForSubmit = !turnstileSiteKey || turnstileStatus === "ready";
  const canSubmit =
    !!file &&
    !!apiKey &&
    !submitting &&
    accepting &&
    handoffPhase === "idle" &&
    (emailDisabled || !!email) &&
    turnstileReadyForSubmit;
  // CLI handoff does NOT require an OpenRouter key on the web form — the
  // user's local `coarse-review` command reads its own key from
  // ~/.coarse/config.toml or .env. It also does NOT require an email —
  // the review comes back via the /review/<id> URL printed by the CLI
  // at the end. Turnstile IS required because `handleMcpHandoff`
  // POSTs to `/api/presign`, which enforces the token server-side.
  const handoffBusy = handoffPhase === "extracting";
  const canHandoff =
    !!file && !handoffBusy && !submitting && accepting && turnstileReadyForSubmit;

  return (
    <div style={{ background: "var(--board)", minHeight: "100vh" }}>
      <Header />

      {/* Capacity banner */}
      {systemStatus && (systemStatus.banner || !systemStatus.accepting || systemStatus.activeReviews >= systemStatus.capacity * 0.8) && (
        <div
          style={{
            maxWidth: "720px",
            margin: "0 auto",
            padding: "1rem 2.5rem",
          }}
        >
          <div
            style={{
              borderLeft: "3px solid var(--red-chalk)",
              paddingLeft: "1rem",
              color: "var(--chalk)",
              fontFamily: "Georgia, serif",
              fontSize: "1.05rem",
              lineHeight: 1.6,
            }}
          >
            {!systemStatus.accepting
              ? (systemStatus.banner || "Submissions are temporarily paused.")
              : systemStatus.banner
                ? systemStatus.banner
                : `The system is busy (${systemStatus.activeReviews}/${systemStatus.capacity} slots in use). Your review may be queued.`}
            {" "}
            For faster results, try the CLI:{" "}
            <code style={{ background: "var(--tray)", padding: "0.15em 0.4em", fontSize: "0.95em" }}>
              pip install coarse-ink
            </code>{" "}
            <a
              href="https://github.com/Davidvandijcke/coarse"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: "var(--red-chalk)", textDecoration: "underline", textUnderlineOffset: "2px" }}
            >
              GitHub
            </a>
          </div>
        </div>
      )}

      <main
        style={{
          maxWidth: "720px",
          margin: "0 auto",
          padding: "0 2.5rem 6rem",
        }}
      >
        {/* ── Hero ──────────────────────────────────────────── */}
        <section style={{ padding: "4.5rem 0 3.5rem", position: "relative" }}>
          <HeroMarks />

          <p
            style={{
              fontFamily: "var(--font-chalk)",
              fontSize: "1.1rem",
              color: "var(--dust)",
              margin: "0 0 1.25rem",
            }}
          >
            Hey <SplitFlap /> can you review this paper?
          </p>

          <h1
            style={{
              fontFamily: "var(--font-serif)",
              fontSize: "clamp(3.5rem, 9vw, 6rem)",
              fontWeight: 400,
              lineHeight: 1.0,
              letterSpacing: "-0.02em",
              margin: 0,
              color: "var(--chalk-bright)",
            }}
          >
            &lsquo;coarse!
          </h1>

          <p
            style={{
              marginTop: "1.75rem",
              fontSize: "1.1rem",
              lineHeight: 1.6,
              color: "var(--chalk)",
              maxWidth: "520px",
            }}
          >
            AI agents review your paper and write a referee report.
            You pay the API cost directly. No account.
          </p>
          <p
            style={{
              marginTop: "0.75rem",
              fontSize: "1rem",
              lineHeight: 1.7,
              color: "var(--dust)",
              fontStyle: "italic",
              maxWidth: "500px",
            }}
          >
            Academic peer review runs on unpaid academic labor.
            Others decided to make a business out of that. We didn&apos;t like that.
          </p>

          {/* Score preview */}
          <div style={{ marginTop: "2.25rem" }}>
            <div style={{ display: "flex", gap: "2.5rem", flexWrap: "wrap", alignItems: "flex-end" }}>
              {/* Big score */}
              <div style={{ transform: "rotate(-1.5deg)" }}>
                <span
                  style={{
                    fontFamily: "var(--font-chalk)",
                    fontSize: "2.75rem",
                    fontWeight: 700,
                    color: "var(--yellow-chalk)",
                    lineHeight: 1,
                  }}
                >
                  5<span style={{ fontSize: "1.5rem", verticalAlign: "super", lineHeight: 0 }}>+</span>
                  <span style={{ fontSize: "1.1rem", fontWeight: 400, color: "var(--dust)" }}> / 5</span>
                </span>
                <span
                  style={{
                    fontFamily: "var(--font-chalk)",
                    fontSize: "1.1rem",
                    color: "var(--dust)",
                    display: "block",
                    marginTop: "0.25rem",
                  }}
                >
                  vs. other AI reviewers
                </span>
              </div>

              {/* Stats */}
              {[
                ["< $2*", "per review", "*typically :)"],
                ["20+", "detailed comments", null],
                ["MIT", "open source", null],
              ].map(([num, label, footnote]) => (
                <div key={label} style={{ position: "relative" }}>
                  <span
                    style={{
                      fontFamily: "var(--font-serif)",
                      fontSize: "1.5rem",
                      fontWeight: 400,
                      display: "block",
                      lineHeight: 1,
                      color: "var(--chalk-bright)",
                    }}
                  >
                    {num}
                  </span>
                  <span
                    style={{
                      fontFamily: "var(--font-chalk)",
                      fontSize: "1.1rem",
                      color: "var(--dust)",
                      display: "block",
                      marginTop: "0.25rem",
                    }}
                  >
                    {label}
                  </span>
                  {footnote && (
                    <span
                      style={{
                        fontFamily: "var(--font-chalk)",
                        fontSize: "1rem",
                        color: "var(--dust)",
                        fontStyle: "italic",
                        display: "block",
                        position: "absolute",
                        top: "100%",
                        left: 0,
                        marginTop: "0.125rem",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {footnote}
                    </span>
                  )}
                </div>
              ))}
            </div>

            {/* Competitive comparison */}
            <p
              style={{
                marginTop: "1.25rem",
                fontFamily: "Georgia, serif",
                fontSize: "1.05rem",
                lineHeight: 1.7,
                color: "var(--chalk)",
                maxWidth: "520px",
              }}
            >
              Blind-evaluated against{" "}
              <span style={{ color: "var(--chalk-bright)" }}>refine.ink</span>,{" "}
              <span style={{ color: "var(--chalk-bright)" }}>Stanford Agentic Reviewer</span>, and{" "}
              <span style={{ color: "var(--chalk-bright)" }}>reviewer3.com</span>.
              Scores higher on coverage, specificity, and depth -- at a fraction of the cost.
            </p>

            <a
              href="/compare"
              style={{
                display: "inline-block",
                marginTop: "0.75rem",
                fontFamily: "var(--font-chalk)",
                fontSize: "1.05rem",
                color: "var(--blue-chalk)",
                textDecoration: "none",
              }}
            >
              See the side-by-side →
            </a>
          </div>
        </section>

        <CharcoalRule />

        {/* ── Form ──────────────────────────────────────────── */}
        <section style={{ padding: "2.5rem 0 3rem" }}>
          <p
            style={{
              fontFamily: "var(--font-chalk)",
              fontSize: "1.1rem",
              color: "var(--dust)",
              marginBottom: "2.25rem",
            }}
          >
            Submit a paper
          </p>

          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
            {/* Drop zone */}
            <div>
              <FieldLabel>Paper</FieldLabel>
              <div
                {...getRootProps()}
                role="button"
                aria-label="Upload your paper — drop a file or click to browse"
                style={{
                  border: `1.5px dashed ${isDragActive ? "var(--yellow-chalk)" : "var(--tray)"}`,
                  padding: "2.25rem 2rem",
                  textAlign: "center",
                  cursor: "pointer",
                  background: isDragActive ? "rgba(212, 168, 67, 0.06)" : "var(--board-surface)",
                  transition: "border-color 0.2s, background 0.2s",
                  borderRadius: "2px",
                }}
              >
                <input {...getInputProps()} aria-label="Choose a file to upload" />
                {file ? (
                  <>
                    <p
                      style={{
                        fontFamily: "var(--font-space-mono), monospace",
                        fontSize: "1rem",
                        fontWeight: 700,
                        margin: 0,
                        color: "var(--chalk-bright)",
                      }}
                    >
                      {file.name}
                    </p>
                    <p
                      style={{
                        fontFamily: "var(--font-chalk)",
                        fontSize: "1.1rem",
                        color: "var(--dust)",
                        margin: "0.375rem 0 0",
                      }}
                    >
                      {(file.size / 1024 / 1024).toFixed(1)} MB — click or drop to replace
                    </p>
                  </>
                ) : (
                  <>
                    <p
                      style={{
                        fontFamily: "Georgia, serif",
                        fontSize: "1.05rem",
                        color: "var(--chalk)",
                        margin: 0,
                      }}
                    >
                      Drop your file here, or{" "}
                      <span style={{ textDecoration: "underline", textUnderlineOffset: "2px" }}>browse</span>
                    </p>
                    <p
                      style={{
                        fontFamily: "var(--font-chalk)",
                        fontSize: "1.1rem",
                        color: "var(--dust)",
                        margin: "0.375rem 0 0",
                      }}
                    >
                      Up to 50 MB
                    </p>
                  </>
                )}
              </div>
            </div>

            {/* Email + API key */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "2rem",
              }}
            >
              <div>
                <FieldLabel>Email <span style={{ color: "var(--dust)", fontWeight: 400 }}>(for web review only)</span></FieldLabel>
                <input
                  type="email"
                  required={!emailDisabled}
                  disabled={emailDisabled}
                  value={emailDisabled ? "" : email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={emailDisabled ? "— unavailable —" : "you@university.edu"}
                  aria-label="Email address"
                  className="field-line"
                  style={emailDisabled ? { opacity: 0.55, cursor: "not-allowed" } : undefined}
                />
                <p
                  style={{
                    fontFamily: "var(--font-chalk)",
                    fontSize: "1.1rem",
                    color: emailDisabled ? "var(--red-chalk)" : "var(--dust)",
                    marginTop: "0.4rem",
                  }}
                >
                  {emailDisabled
                    ? "Email delivery is temporarily down. Save your review key when you submit and check back in about an hour."
                    : <>We&apos;ll email you when it&apos;s done. Check your spam folder if you don&apos;t see it.</>}
                </p>
              </div>

              <div>
                <FieldLabel>
                  OpenRouter key{" "}
                  <a
                    href="/setup"
                    style={{
                      color: "var(--blue-chalk)",
                      textDecoration: "none",
                    }}
                  >
                    get one →
                  </a>
                </FieldLabel>
                <div style={{ marginBottom: "0.9rem" }}>
                  <OpenRouterLoginButton
                    apiKey={apiKey}
                    onLogin={() => {
                      beginLogin(window.location.origin + "/").catch((err) => {
                        setError(
                          `OpenRouter login could not start: ${err instanceof Error ? err.message : String(err)}`,
                        );
                      });
                    }}
                    onLogout={() => {
                      clearStoredKey();
                      setApiKey("");
                      setKeyNotice(null);
                    }}
                  />
                </div>
                {!apiKey && (
                  <p
                    style={{
                      fontFamily: "var(--font-chalk)",
                      fontSize: "1rem",
                      color: "var(--dust)",
                      margin: "0 0 0.4rem",
                    }}
                  >
                    — or paste a key —
                  </p>
                )}
                <input
                  type="password"
                  required
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="sk-or-v1-…"
                  aria-label="OpenRouter API key"
                  className="field-line-mono"
                />
                <p
                  style={{
                    fontFamily: "var(--font-chalk)",
                    fontSize: "1.1rem",
                    color: "var(--dust)",
                    marginTop: "0.4rem",
                  }}
                >
                  OAuth keys stay in this tab only and clear when you close it. Never saved on our servers.
                </p>
                {keyNotice && (
                  <p
                    style={{
                      fontFamily: "var(--font-chalk)",
                      fontSize: "1rem",
                      color: "var(--blue-chalk)",
                      marginTop: "0.35rem",
                    }}
                  >
                    {keyNotice}
                  </p>
                )}
              </div>
            </div>

            {/* Model picker */}
            <ModelPicker value={model} onChange={setModel} />

            {/* Optional author notes — steer the review */}
            <div>
              <FieldLabel>
                Notes for the reviewer{" "}
                <span style={{ color: "var(--dust)", fontSize: "0.85em" }}>(optional)</span>
              </FieldLabel>
              <textarea
                value={authorNotes}
                onChange={(e) => setAuthorNotes(e.target.value.slice(0, 2000))}
                placeholder="e.g. please focus on the identification strategy in §3 — the data section is still a placeholder."
                rows={3}
                maxLength={2000}
                aria-label="Optional notes to steer the reviewer"
                className="field-line-textarea"
              />
              <p
                style={{
                  fontFamily: "var(--font-chalk)",
                  fontSize: "1rem",
                  color: "var(--dust)",
                  marginTop: "0.35rem",
                  display: "flex",
                  justifyContent: "space-between",
                }}
              >
                <span>Steer what the reviewer focuses on. Does not override the rubric.</span>
                <span style={{ fontVariantNumeric: "tabular-nums" }}>{authorNotes.length}/2000</span>
              </p>
            </div>

            {/* Cost estimate */}
            {file && (
              <p
                style={{
                  fontFamily: "var(--font-space-mono), monospace",
                  fontSize: "1.05rem",
                  color: costEstimate !== null ? "var(--yellow-chalk)" : "var(--dust)",
                  margin: "-0.5rem 0 0",
                }}
              >
                {costLoading
                  ? "Estimating cost..."
                  : costEstimate !== null
                    ? `Estimated API cost: $${costEstimate < 0.01 ? costEstimate.toFixed(4) : costEstimate.toFixed(2)}`
                    : "Cost estimate unavailable for this model"}
              </p>
            )}

            {turnstileSiteKey && (
              <div>
                <div
                  ref={turnstileContainerRef}
                  style={{
                    minHeight: "65px",
                    display: turnstileStatus === "failed" ? "none" : "block",
                  }}
                />
                {turnstileStatus === "failed" && (
                  <div
                    style={{
                      borderLeft: "3px solid var(--yellow-chalk)",
                      paddingLeft: "1rem",
                      color: "var(--chalk)",
                      fontFamily: "Georgia, serif",
                      fontSize: "1.05rem",
                      lineHeight: 1.6,
                    }}
                  >
                    <p style={{ margin: "0 0 0.6rem" }}>
                      Our human check couldn&apos;t load. A browser privacy
                      extension or a Turnstile hostname mismatch is most
                      likely blocking{" "}
                      <code style={{ fontFamily: "var(--font-space-mono), monospace" }}>
                        challenges.cloudflare.com
                      </code>{" "}
                      — common with Brave Shields, uBlock Origin on some filter
                      lists, or Firefox ETP strict mode.
                    </p>
                    <p style={{ margin: "0 0 0.6rem" }}>
                      Try disabling the extension for{" "}
                      <code style={{ fontFamily: "var(--font-space-mono), monospace" }}>
                        {siteHost}
                      </code>{" "}
                      and refreshing, or use a different browser. If
                      you&apos;re on a preview URL, the deployment may also need
                      that hostname added to the Cloudflare Turnstile widget
                      allowlist.
                    </p>
                    <p style={{ margin: 0 }}>
                      Or run coarse locally with your own OpenRouter key:{" "}
                      <code style={{ fontFamily: "var(--font-space-mono), monospace" }}>
                        uvx coarse-ink review paper.pdf
                      </code>
                      .
                    </p>
                  </div>
                )}
              </div>
            )}

            {error && (
              <div
                style={{
                  borderLeft: "3px solid var(--red-chalk)",
                  paddingLeft: "1rem",
                  color: "var(--red-chalk)",
                  fontFamily: "Georgia, serif",
                  fontSize: "1.05rem",
                }}
              >
                {error}
              </div>
            )}

            <div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "1rem", alignItems: "center" }}>
                <button
                  type="submit"
                  disabled={!canSubmit}
                  style={{
                    background: canSubmit ? "var(--yellow-chalk)" : "var(--tray)",
                    color: canSubmit ? "var(--board)" : "var(--dust)",
                    border: "none",
                    padding: "0.9375rem 2.5rem",
                    fontFamily: "var(--font-chalk)",
                    fontSize: "1.1rem",
                    fontWeight: 600,
                    cursor: canSubmit ? "pointer" : "not-allowed",
                    transition: "background 0.2s, color 0.2s",
                    borderRadius: "2px",
                  }}
                >
                  {submitting ? "Submitting..." : "Review my paper"}
                </button>

                <span
                  style={{
                    fontFamily: "var(--font-chalk)",
                    fontSize: "1.05rem",
                    color: "var(--dust)",
                  }}
                >
                  or
                </span>

                <div style={{ position: "relative" }}>
                  <button
                    type="button"
                    disabled={!canHandoff}
                    onClick={() => setMcpPickerOpen((v) => !v)}
                    style={{
                      background: "transparent",
                      color: canHandoff ? "var(--chalk-bright)" : "var(--dust)",
                      border: `1.5px solid ${canHandoff ? "var(--yellow-chalk)" : "var(--tray)"}`,
                      padding: "0.875rem 1.75rem",
                      fontFamily: "var(--font-chalk)",
                      fontSize: "1.1rem",
                      fontWeight: 600,
                      cursor: canHandoff ? "pointer" : "not-allowed",
                      transition: "border-color 0.2s, color 0.2s",
                      borderRadius: "2px",
                    }}
                    aria-expanded={mcpPickerOpen}
                    aria-haspopup="listbox"
                  >
                    {handoffBusy ? "Preparing..." : "Review with my subscription ▾"}
                  </button>

                  {handoffBusy && handoffMessage && (
                    <div
                      style={{
                        position: "absolute",
                        top: "calc(100% + 0.6rem)",
                        left: 0,
                        minWidth: "340px",
                        padding: "0.65rem 0.9rem",
                        background: "var(--board-surface)",
                        border: "1px solid var(--tray)",
                        borderLeft: "3px solid var(--yellow-chalk)",
                        borderRadius: "2px",
                        fontFamily: "var(--font-chalk)",
                        fontSize: "1rem",
                        color: "var(--chalk)",
                        lineHeight: 1.4,
                        zIndex: 9,
                      }}
                    >
                      <span style={{ color: "var(--yellow-chalk)" }}>⏳</span>{" "}
                      {handoffMessage}
                    </div>
                  )}

                  {mcpPickerOpen && canHandoff && (
                    <div
                      role="listbox"
                      style={{
                        position: "absolute",
                        top: "calc(100% + 0.4rem)",
                        left: 0,
                        minWidth: "320px",
                        background: "var(--board-surface)",
                        border: "1px solid var(--tray)",
                        borderRadius: "2px",
                        padding: "0.5rem 0",
                        boxShadow: "0 6px 18px rgba(0,0,0,0.35)",
                        zIndex: 10,
                      }}
                    >
                      {(["claude-code", "codex", "gemini-cli"] as ChatHost[]).map((h) => (
                        <button
                          key={h}
                          type="button"
                          onClick={() => handleMcpHandoff(h)}
                          role="option"
                          aria-selected="false"
                          style={{
                            display: "block",
                            width: "100%",
                            textAlign: "left",
                            padding: "0.7rem 1rem",
                            background: "transparent",
                            border: "none",
                            color: "var(--chalk-bright)",
                            fontFamily: "var(--font-chalk)",
                            fontSize: "1.05rem",
                            cursor: "pointer",
                            transition: "background 0.15s",
                            borderRadius: 0,
                          }}
                          onMouseEnter={(e) => {
                            (e.currentTarget as HTMLButtonElement).style.background = "var(--tray)";
                          }}
                          onMouseLeave={(e) => {
                            (e.currentTarget as HTMLButtonElement).style.background = "transparent";
                          }}
                        >
                          <span style={{ color: "var(--yellow-chalk)", marginRight: "0.6rem" }}>
                            {HOST_GLYPHS[h]}
                          </span>
                          {HOST_LABELS[h]}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <p
                style={{
                  fontFamily: "var(--font-chalk)",
                  fontSize: "1.1rem",
                  color: "var(--dust)",
                  marginTop: "0.9rem",
                  maxWidth: "620px",
                  lineHeight: 1.5,
                }}
              >
                <strong style={{ color: "var(--chalk)" }}>Review my paper:</strong>
                {" "}OpenRouter handles everything end-to-end. File deleted after processing. Review key works for 90 days. Usually under $2.
              </p>
              <p
                style={{
                  fontFamily: "var(--font-chalk)",
                  fontSize: "1.1rem",
                  color: "var(--dust)",
                  marginTop: "0.3rem",
                  maxWidth: "620px",
                  lineHeight: 1.5,
                }}
              >
                <strong style={{ color: "var(--chalk)" }}>Review with my subscription:</strong>
                {" "}we hand you a shell command that runs the full coarse pipeline
                locally using <em>your</em>{" "}
                <a href="https://claude.ai/download" target="_blank" rel="noopener noreferrer" style={{ color: "var(--blue-chalk)", textDecoration: "none" }}>Claude Code</a>,{" "}
                <a href="https://github.com/openai/codex" target="_blank" rel="noopener noreferrer" style={{ color: "var(--blue-chalk)", textDecoration: "none" }}>Codex</a>, or{" "}
                <a href="https://github.com/google-gemini/gemini-cli" target="_blank" rel="noopener noreferrer" style={{ color: "var(--blue-chalk)", textDecoration: "none" }}>Gemini CLI</a>{" "}
                subscription for the LLM reasoning. You only pay ~$0.10 for the
                local Mistral OCR step (with your own OpenRouter key). Review
                shows up on this page when done.
              </p>
              <p
                style={{
                  fontFamily: "var(--font-chalk)",
                  fontSize: "0.95rem",
                  color: "var(--dust)",
                  margin: "0.55rem 0 0",
                  maxWidth: "620px",
                  lineHeight: 1.5,
                }}
              >
                Runs locally on your machine using your own Claude Code, Codex,
                or Gemini CLI account. coarse.ink does not receive or store your
                provider login, and your provider&apos;s terms, usage limits, and
                organization policies apply. coarse.ink is not affiliated with
                Anthropic, OpenAI, or Google.
              </p>

              {handoffBundle && handoffState && (() => {
                const host = handoffState.host;
                const { setupCmd, runCmd, attachCmd, logFile } = buildCliCommands({
                  handoffUrl: handoffBundle.handoff_url,
                  host,
                  model: selectedModel,
                  effort: selectedEffort,
                  paperId: handoffState.paperId,
                });
                return (
                  <div
                    style={{
                      marginTop: "1.5rem",
                      padding: "1.25rem 1.5rem",
                      borderLeft: "3px solid var(--yellow-chalk)",
                      background: "var(--board-surface)",
                      borderRadius: "2px",
                    }}
                  >
                    <p
                      style={{
                        fontFamily: "var(--font-chalk)",
                        fontSize: "1.15rem",
                        color: "var(--chalk-bright)",
                        margin: "0 0 0.75rem",
                      }}
                    >
                      <span style={{ color: "var(--yellow-chalk)" }}>
                        {HOST_GLYPHS[host]}
                      </span>{" "}
                      Review with <strong>{HOST_LABELS[host]}</strong>
                    </p>

                    {/* Model + effort dropdowns */}
                    <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "1rem" }}>
                      <label style={{ fontFamily: "var(--font-chalk)", fontSize: "0.95rem", color: "var(--dust)" }}>
                        model{" "}
                        <select
                          value={selectedModel}
                          onChange={(e) => setSelectedModel(e.target.value)}
                          style={{ marginLeft: "0.25rem", padding: "0.25rem 0.5rem", background: "var(--board)", color: "var(--chalk)", border: "1px solid var(--tray)", borderRadius: "2px", fontFamily: "monospace", fontSize: "0.92rem" }}
                        >
                          {HOST_DEFAULT_MODELS[host].map((m) => (<option key={m} value={m}>{m}</option>))}
                        </select>
                      </label>
                      <label style={{ fontFamily: "var(--font-chalk)", fontSize: "0.95rem", color: "var(--dust)" }}>
                        effort{" "}
                        <select
                          value={selectedEffort}
                          onChange={(e) => setSelectedEffort(e.target.value as EffortLevel)}
                          style={{ marginLeft: "0.25rem", padding: "0.25rem 0.5rem", background: "var(--board)", color: "var(--chalk)", border: "1px solid var(--tray)", borderRadius: "2px", fontFamily: "monospace", fontSize: "0.92rem" }}
                        >
                          {EFFORT_LEVELS.map((e) => (<option key={e} value={e}>{e}</option>))}
                        </select>
                      </label>
                    </div>

                    {/* PRIMARY: always-visible prompt. Uniform across
                        all three hosts — no collapsibles, no host-
                        specific reveals. Users paste this into their
                        terminal and it works regardless of whether any
                        desktop-app deep-link fires. */}
                    <div style={{ marginTop: "0.25rem" }}>
                      <div
                        style={{
                          fontFamily: "var(--font-chalk)",
                          fontSize: "0.95rem",
                          color: "var(--yellow-chalk)",
                          marginBottom: "0.5rem",
                        }}
                      >
                        Paste this prompt into your {HOST_LABELS[host]} terminal:
                      </div>
                      <CodeBlock
                        text={buildAgentPrompt({ setupCmd, runCmd, attachCmd, logFile })}
                        maxHeight="160px"
                      />
                      <p
                        style={{
                          fontFamily: "var(--font-chalk)",
                          fontSize: "0.92rem",
                          color: "var(--dust)",
                          margin: "0.5rem 0 0",
                          lineHeight: 1.5,
                        }}
                      >
                        The agent will refresh the coarse-review skill, run
                        the full review locally, and take 10&ndash;25 minutes.
                        Your provider login stays on your machine.
                      </p>
                      <p
                        style={{
                          fontFamily: "var(--font-chalk)",
                          fontSize: "0.92rem",
                          color: "var(--yellow-chalk)",
                          margin: "0.5rem 0 0",
                          lineHeight: 1.5,
                        }}
                      >
                        Your OpenRouter key needs to be on your machine first
                        — export <code style={{ fontFamily: "var(--font-space-mono), monospace", fontSize: "0.88rem" }}>OPENROUTER_API_KEY</code>,
                        or put it in <code style={{ fontFamily: "var(--font-space-mono), monospace", fontSize: "0.88rem" }}>.env</code>{" "}
                        or <code style={{ fontFamily: "var(--font-space-mono), monospace", fontSize: "0.88rem" }}>~/.coarse/config.toml</code>.
                        We don&apos;t pass it through the browser because the
                        handoff URL ends up in your agent&apos;s chat log. If
                        it&apos;s missing, the agent will ask.
                      </p>
                    </div>

                    {/* Review URL */}
                    <p
                      style={{
                        fontFamily: "Georgia, serif",
                        fontSize: "1rem",
                        color: "var(--chalk)",
                        margin: "1rem 0 0",
                        lineHeight: 1.55,
                      }}
                    >
                      When the review finishes, it will appear at:
                    </p>
                    <a
                      href={`/review/${handoffState.paperId}`}
                      style={{
                        display: "inline-block",
                        marginTop: "0.35rem",
                        fontFamily: "var(--font-space-mono), monospace",
                        fontSize: "0.95rem",
                        color: "var(--blue-chalk)",
                        textDecoration: "underline",
                        textUnderlineOffset: "2px",
                        wordBreak: "break-all",
                      }}
                    >
                      /review/{handoffState.paperId}
                    </a>

                    {/* SECONDARY: desktop-app launch button. Hidden on
                        Linux/mobile (no desktop handlers) and for Gemini
                        (no documented URL scheme). When the scheme
                        fires successfully the user gets a nice one-click
                        handoff; when it silently fails the 2.5s timer in
                        handleLaunch swaps the hint to "didn't open".
                        Either way, the commands above are always the
                        guaranteed path. */}
                    {host !== "gemini-cli" && isDesktopAppPlatform() && (
                      <div style={{ marginTop: "1.25rem" }}>
                        <button
                          type="button"
                          onClick={handleLaunch}
                          style={{
                            display: "block",
                            width: "100%",
                            padding: "0.8rem 1.25rem",
                            background: "var(--board-surface)",
                            color: "var(--yellow-chalk)",
                            border: "1.5px solid var(--yellow-chalk)",
                            borderRadius: "2px",
                            fontFamily: "var(--font-chalk)",
                            fontSize: "1.08rem",
                            fontWeight: 600,
                            cursor: "pointer",
                            transition: "background 0.15s",
                          }}
                        >
                          {HOST_LAUNCH_LABEL[host]}
                        </button>
                        <p
                          style={{
                            fontFamily: "var(--font-chalk)",
                            fontSize: "0.88rem",
                            color: "var(--dust)",
                            margin: "0.4rem 0 0",
                            lineHeight: 1.5,
                          }}
                        >
                          {launchStatus || HOST_LAUNCH_HINT[host]}
                        </p>
                      </div>
                    )}

                    <p
                      style={{
                        fontFamily: "var(--font-chalk)",
                        fontSize: "0.92rem",
                        color: "var(--dust)",
                        margin: "1rem 0 0",
                      }}
                    >
                      Don&apos;t have {HOST_LABELS[host]} yet?{" "}
                      <a href={HOST_INSTALL_URL[host]} target="_blank" rel="noopener noreferrer" style={{ color: "var(--blue-chalk)", textDecoration: "none" }}>
                        install it →
                      </a>
                    </p>
                  </div>
                );
              })()}
            </div>
          </form>
        </section>

        <CharcoalRule />

        {/* ── Retrieve ──────────────────────────────────────── */}
        <section style={{ padding: "2.5rem 0 0" }}>
          <p
            style={{
              fontFamily: "var(--font-chalk)",
              fontSize: "1.1rem",
              color: "var(--dust)",
              marginBottom: "1.25rem",
            }}
          >
            Find a review
          </p>

          <div style={{ display: "flex", gap: "0.875rem", alignItems: "flex-end" }}>
            <input
              type="text"
              value={lookupKey}
              onChange={(e) => setLookupKey(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && lookupKey.trim()) {
                  const parsed = parseReviewLocator(lookupKey);
                  if (parsed?.token) {
                    router.push(buildReviewPath("review", parsed.id, parsed.token));
                  } else if (parsed?.id) {
                    router.push(`/review/${parsed.id}`);
                  }
                }
              }}
              placeholder="Paste your review key, full review link, or legacy review ID..."
              aria-label="Review key"
              className="field-line-mono"
              style={{ maxWidth: "480px" }}
            />
            <button
              type="button"
              onClick={() => {
                const parsed = parseReviewLocator(lookupKey);
                if (parsed?.token) {
                  router.push(buildReviewPath("review", parsed.id, parsed.token));
                } else if (parsed?.id) {
                  router.push(`/review/${parsed.id}`);
                }
              }}
              disabled={!lookupKey.trim()}
              style={{
                background: "transparent",
                border: `1px solid ${lookupKey.trim() ? "var(--chalk)" : "var(--tray)"}`,
                color: lookupKey.trim() ? "var(--chalk)" : "var(--dust)",
                padding: "0.5rem 1.25rem",
                fontFamily: "var(--font-chalk)",
                fontSize: "1rem",
                cursor: lookupKey.trim() ? "pointer" : "not-allowed",
                whiteSpace: "nowrap",
                transition: "border-color 0.2s, color 0.2s",
                borderRadius: "2px",
              }}
            >
              Find
            </button>
          </div>
        </section>

        <CharcoalRule />

        <footer
          style={{
            padding: "1.5rem 0 0",
            display: "flex",
            justifyContent: "center",
            gap: "1.5rem",
          }}
        >
          <a
            href="/privacy"
            style={{
              fontFamily: "var(--font-chalk)",
              fontSize: "1.05rem",
              color: "var(--dust)",
              textDecoration: "none",
            }}
          >
            privacy
          </a>
          <a
            href="/terms"
            style={{
              fontFamily: "var(--font-chalk)",
              fontSize: "1.05rem",
              color: "var(--dust)",
              textDecoration: "none",
            }}
          >
            terms
          </a>
          <a
            href="mailto:dvdijcke@umich.edu"
            style={{
              fontFamily: "var(--font-chalk)",
              fontSize: "1.05rem",
              color: "var(--dust)",
              textDecoration: "none",
            }}
          >
            contact
          </a>
        </footer>
      </main>
    </div>
  );
}
