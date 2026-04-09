"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { useDropzone } from "react-dropzone";
import { useRouter } from "next/navigation";
import { CharcoalRule, HeroMarks } from "@/components/charcoal";
import ModelPicker from "@/components/ModelPicker";
import { estimateTokensFromPdf, estimateTokensFromText, estimateTokensFromDocx, estimateTokensFromEpub, getModelPricing, estimateReviewCost } from "@/lib/estimateCost";

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
  const [file, setFile] = useState<File | null>(null);
  const [email, setEmail] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [model, setModel] = useState("anthropic/claude-sonnet-4.6");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lookupKey, setLookupKey] = useState("");
  const [costEstimate, setCostEstimate] = useState<number | null>(null);
  const [costLoading, setCostLoading] = useState(false);
  const tokenCacheRef = useRef<{ name: string; size: number; tokens: number } | null>(null);
  const [systemStatus, setSystemStatus] = useState<{
    accepting: boolean; banner: string | null; activeReviews: number; capacity: number;
  } | null>(null);

  // Fetch system capacity status on mount
  useEffect(() => {
    fetch("/api/status").then(r => r.json()).then(setSystemStatus).catch(() => {});
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
        const cached = tokenCacheRef.current;
        if (cached && cached.name === file.name && cached.size === file.size) {
          tokens = cached.tokens;
        } else {
          const ext = file.name.toLowerCase().split(".").pop();
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
          setCostEstimate(estimateReviewCost(tokens, pricing));
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

  const accepting = systemStatus?.accepting !== false;
  const canSubmit = !!file && !!email && !!apiKey && !submitting && accepting;

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
              pip install coarse
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
                <FieldLabel>Email</FieldLabel>
                <input
                  type="email"
                  required
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
                  We&apos;ll email you when it&apos;s done.
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
                  Used once. Never stored.
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
              <p
                style={{
                  fontFamily: "var(--font-chalk)",
                  fontSize: "1.1rem",
                  color: "var(--dust)",
                  marginTop: "0.9rem",
                }}
              >
                File deleted after processing. No provider trains on it. Review key works for 90 days. Usually under $2.
              </p>
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
