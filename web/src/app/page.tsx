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
} from "@/lib/mcpHandoff";

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
function CodeBlock({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <div
      style={{
        position: "relative",
        background: "var(--board)",
        border: "1px solid var(--tray)",
        borderLeft: "2px solid var(--yellow-chalk)",
        borderRadius: "2px",
        padding: "0.65rem 0.85rem",
        paddingRight: "4.5rem",
        fontFamily: "var(--font-space-mono), monospace",
        fontSize: "0.82rem",
        color: "var(--chalk-bright)",
        lineHeight: 1.5,
        overflowX: "auto",
        whiteSpace: "pre-wrap",
        wordBreak: "break-all",
      }}
    >
      {text}
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
          background: copied ? "var(--yellow-chalk)" : "var(--tray)",
          color: copied ? "var(--board)" : "var(--chalk-bright)",
          border: "none",
          borderRadius: "2px",
          padding: "0.2rem 0.55rem",
          fontSize: "0.75rem",
          fontFamily: "var(--font-chalk)",
          cursor: "pointer",
          transition: "background 0.15s, color 0.15s",
        }}
      >
        {copied ? "copied ✓" : "copy"}
      </button>
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
          href="/mcp"
          style={{
            fontFamily: "var(--font-chalk)",
            fontSize: "1.05rem",
            color: "var(--dust)",
            textDecoration: "none",
            transition: "color 0.2s",
          }}
        >
          mcp
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
  const [file, setFile] = useState<File | null>(null);
  const [email, setEmail] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [model, setModel] = useState("anthropic/claude-opus-4.6");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lookupKey, setLookupKey] = useState("");
  const [costEstimate, setCostEstimate] = useState<number | null>(null);
  const [costLoading, setCostLoading] = useState(false);
  const tokenCacheRef = useRef<{ name: string; size: number; tokens: number } | null>(null);
  const oauthConsumedRef = useRef(false);
  const [systemStatus, setSystemStatus] = useState<{
    accepting: boolean; banner: string | null; activeReviews: number; capacity: number;
  } | null>(null);

  // MCP handoff state machine:
  //
  //   idle → extracting → ready → handed-off
  //           │
  //           └─► failed
  //
  //  - idle: user hasn't clicked the subscription button yet
  //  - extracting: /api/mcp-extract fired, waiting for status='extracted'
  //  - ready: /api/mcp-handoff succeeded, clipboard copied, tab opened
  //  - failed: extraction or handoff errored; show error in form
  //
  // The extraction stage is user-initiated (click-gated) so we never
  // charge the user's OpenRouter key for a paper they uploaded but
  // never wanted to route through their subscription.
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
  const [showManualCommands, setShowManualCommands] = useState<boolean>(false);
  const [launchStatus, setLaunchStatus] = useState<string>("");

  // Fetch system capacity status on mount
  useEffect(() => {
    fetch("/api/status").then(r => r.json()).then(setSystemStatus).catch(() => {});
  }, []);

  // Hydrate OpenRouter key from localStorage and handle OAuth callback (?code=...)
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    const stored = loadStoredKey();

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
        try {
          saveStoredKey(key);
        } catch {
          setError(
            "Logged in, but couldn't save the key to your browser. You'll need to log in again next visit.",
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

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (handoffPhase !== "idle") return;
    if (!file || !email || !apiKey) return;
    setSubmitting(true);
    setError(null);
    try {
      // Step 1: Get a presigned upload URL (small JSON request — no file)
      const presignResp = await fetch("/api/presign", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: file.name }),
      });
      if (!presignResp.ok) {
        const data = await presignResp.json();
        throw new Error(data.error || "Failed to prepare upload");
      }
      const { id, storagePath, signedUrl, token } = await presignResp.json();

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
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id,
          email,
          api_key: apiKey,
          model,
          storage_path: storagePath,
        }),
      });
      if (!submitResp.ok) {
        const data = await submitResp.json();
        throw new Error(data.error || "Submission failed");
      }
      router.push(`/status/${id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Submission failed");
      setSubmitting(false);
    }
  }

  /**
   * Route this review to one of the user's chat hosts via the coarse MCP
   * connector, using the capability-handoff flow with click-gated extraction.
   *
   * State machine:
   *   1. phase='extracting': upload + POST /api/mcp-extract (spawns Modal
   *      do_extract). UI shows a status line "Extracting paper text via OCR…".
   *   2. Subscribe to reviews row via Supabase realtime; wait for
   *      status='extracted'. (Falls back to 1-second polling if realtime
   *      fails.) Extraction typically finishes in 30-90s.
   *   3. phase='ready': POST /api/mcp-handoff to mint the signed state URL
   *      and finalize token. Copy the prompt to clipboard. Open the chat
   *      host in a new tab. Show the "prompt copied" panel.
   *
   * The OpenRouter key never leaves the Next.js → Modal path — it's used
   * once by Modal's do_extract to pay for Mistral OCR + structure parsing,
   * then discarded. The host LLM's clipboard prompt carries only
   * capability tokens, never the raw key.
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
      const presignResp = await fetch("/api/presign", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: file.name }),
      });
      if (!presignResp.ok) {
        const data = await presignResp.json();
        throw new Error(data.error || "Failed to prepare upload");
      }
      const { id, signedUrl } = await presignResp.json();

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
      const bundle = await mintCliHandoff(id, host);

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
    const { setupCmd, runCmd } = buildCliCommands({
      handoffUrl: handoffBundle.handoff_url,
      host,
      model: selectedModel,
      effort: selectedEffort,
    });

    // Copy the full prompt to clipboard (fallback for hosts that can't
    // receive prompts via URL scheme — currently Claude Code and Gemini).
    const fullPrompt =
      `Please review an academic paper for me using the coarse-review skill. ` +
      `If coarse-ink is not installed yet, first run:\n\n${setupCmd}\n\n` +
      `Then run the review:\n\n${runCmd}\n\n` +
      `Run both commands in the terminal. The review takes 10-25 minutes. ` +
      `When it finishes, show me the review URL and a summary.`;
    try {
      await navigator.clipboard.writeText(fullPrompt);
    } catch (err) {
      console.error("clipboard write failed", err);
    }

    // Open the host's app. Codex gets a codex://new?prompt=<text> deep
    // link that pre-fills the prompt. Claude Code and Gemini just open
    // the app (no prompt param support yet) and rely on clipboard paste.
    const launchUrl = buildLaunchUrl({ host, runCmd, setupCmd });
    window.location.href = launchUrl;

    if (host === "codex") {
      setLaunchStatus(
        `Codex opened with the review command pre-filled. Just hit send.`,
      );
    } else {
      setLaunchStatus(
        `${HOST_LABELS[host]} opened. Prompt copied — paste it (⌘V) into the chat.`,
      );
    }
  }

  function resetHandoff() {
    setHandoffPhase("idle");
    setHandoffBundle(null);
    setHandoffState(null);
    setHandoffMessage("");
    setLaunchStatus("");
    setShowManualCommands(false);
  }

  const accepting = systemStatus?.accepting !== false;
  const canSubmit = !!file && !!email && !!apiKey && !submitting && accepting && handoffPhase === "idle";
  // CLI handoff does NOT require an OpenRouter key on the web form — the
  // user's local `coarse-review` command reads its own key from
  // ~/.coarse/config.toml or .env. It also does NOT require an email —
  // the review comes back via the /review/<id> URL printed by the CLI
  // at the end.
  const handoffBusy = handoffPhase === "extracting";
  const canHandoff = !!file && !handoffBusy && !submitting && accepting;

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
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@university.edu"
                  aria-label="Email address"
                  className="field-line"
                />
                <p
                  style={{
                    fontFamily: "var(--font-chalk)",
                    fontSize: "1.1rem",
                    color: "var(--dust)",
                    marginTop: "0.4rem",
                  }}
                >
                  We&apos;ll email you when it&apos;s done. Not needed for subscription review.
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
                  Stored on your device only. Never saved on our servers.
                </p>
              </div>
            </div>

            {/* Model picker */}
            <ModelPicker value={model} onChange={setModel} />

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

              {handoffBundle && handoffState && (() => {
                const host = handoffState.host;
                const { setupCmd, runCmd } = buildCliCommands({
                  handoffUrl: handoffBundle.handoff_url,
                  host,
                  model: selectedModel,
                  effort: selectedEffort,
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
                          style={{ marginLeft: "0.25rem", padding: "0.25rem 0.5rem", background: "var(--board)", color: "var(--chalk)", border: "1px solid var(--tray)", borderRadius: "2px", fontFamily: "monospace", fontSize: "0.85rem" }}
                        >
                          {HOST_DEFAULT_MODELS[host].map((m) => (<option key={m} value={m}>{m}</option>))}
                        </select>
                      </label>
                      <label style={{ fontFamily: "var(--font-chalk)", fontSize: "0.95rem", color: "var(--dust)" }}>
                        effort{" "}
                        <select
                          value={selectedEffort}
                          onChange={(e) => setSelectedEffort(e.target.value as EffortLevel)}
                          style={{ marginLeft: "0.25rem", padding: "0.25rem 0.5rem", background: "var(--board)", color: "var(--chalk)", border: "1px solid var(--tray)", borderRadius: "2px", fontFamily: "monospace", fontSize: "0.85rem" }}
                        >
                          {EFFORT_LEVELS.map((e) => (<option key={e} value={e}>{e}</option>))}
                        </select>
                      </label>
                    </div>

                    {/* Primary launch button */}
                    <button
                      type="button"
                      onClick={handleLaunch}
                      style={{
                        display: "block",
                        width: "100%",
                        padding: "0.875rem 1.5rem",
                        background: "var(--yellow-chalk)",
                        color: "var(--board)",
                        border: "none",
                        borderRadius: "2px",
                        fontFamily: "var(--font-chalk)",
                        fontSize: "1.1rem",
                        fontWeight: 600,
                        cursor: "pointer",
                        transition: "opacity 0.15s",
                      }}
                    >
                      {HOST_LAUNCH_LABEL[host]}
                    </button>
                    <p
                      style={{
                        fontFamily: "var(--font-chalk)",
                        fontSize: "0.9rem",
                        color: "var(--dust)",
                        margin: "0.5rem 0 0",
                        lineHeight: 1.5,
                      }}
                    >
                      {launchStatus || HOST_LAUNCH_HINT[host]}
                    </p>

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

                    {/* Collapsible manual commands */}
                    <div style={{ marginTop: "1.25rem" }}>
                      <button
                        type="button"
                        onClick={() => setShowManualCommands(!showManualCommands)}
                        style={{
                          background: "transparent",
                          border: "none",
                          color: "var(--dust)",
                          fontFamily: "var(--font-chalk)",
                          fontSize: "0.9rem",
                          cursor: "pointer",
                          padding: 0,
                          textDecoration: "underline",
                          textUnderlineOffset: "2px",
                        }}
                      >
                        {showManualCommands ? "Hide manual commands ▴" : "Show manual commands ▾"}
                      </button>
                      {showManualCommands && (
                        <div style={{ marginTop: "0.75rem" }}>
                          <div style={{ fontFamily: "var(--font-chalk)", fontSize: "0.9rem", color: "var(--dust)", marginBottom: "0.35rem" }}>
                            one-time setup (skip if you&apos;ve run this before)
                          </div>
                          <CodeBlock text={setupCmd} />
                          <div style={{ fontFamily: "var(--font-chalk)", fontSize: "0.9rem", color: "var(--dust)", marginTop: "0.75rem", marginBottom: "0.35rem" }}>
                            run the review
                          </div>
                          <CodeBlock text={runCmd} />
                        </div>
                      )}
                    </div>

                    <p
                      style={{
                        fontFamily: "var(--font-chalk)",
                        fontSize: "0.85rem",
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
                if (e.key === "Enter" && lookupKey.trim())
                  router.push(`/review/${lookupKey.trim()}`);
              }}
              placeholder="Paste your review key..."
              aria-label="Review key"
              className="field-line-mono"
              style={{ maxWidth: "480px" }}
            />
            <button
              type="button"
              onClick={() => {
                const k = lookupKey.trim();
                if (k) router.push(`/review/${k}`);
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
        </footer>
      </main>
    </div>
  );
}
