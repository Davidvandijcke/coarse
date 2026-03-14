"use client";

import { CharcoalRule } from "@/components/charcoal";

/* ── Header (matching landing page) ──────────────────────── */
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
        <a
          href="/"
          style={{
            fontFamily: "var(--font-serif)",
            fontSize: "1.25rem",
            fontWeight: 400,
            letterSpacing: "-0.01em",
            color: "var(--chalk-bright)",
            textDecoration: "none",
          }}
        >
          &lsquo;coarse
        </a>
        <span
          style={{
            fontFamily: "var(--font-chalk)",
            fontSize: "0.95rem",
            color: "var(--dust)",
          }}
        >
          peer review is a public good.
        </span>
      </div>
      <div style={{ display: "flex", alignItems: "baseline", gap: "1.5rem" }}>
        <span
          style={{
            fontFamily: "var(--font-chalk)",
            fontSize: "1.05rem",
            color: "var(--chalk)",
          }}
        >
          setup
        </span>
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

/* ── Chalk-sketch mock ───────────────────────────────────── */
function ChalkSketch({
  children,
  annotation,
}: {
  children: React.ReactNode;
  annotation?: string;
}) {
  return (
    <div style={{ position: "relative", margin: "1.25rem 0 0.5rem" }}>
      <div
        style={{
          background: "var(--board-surface)",
          border: "1px dashed var(--tray)",
          borderRadius: "2px",
          padding: "1.25rem 1.5rem",
        }}
      >
        {children}
      </div>
      {annotation && (
        <span
          style={{
            position: "absolute",
            right: "-0.5rem",
            top: "-0.75rem",
            fontFamily: "var(--font-chalk)",
            fontSize: "0.95rem",
            color: "var(--yellow-chalk)",
            transform: "rotate(-3deg)",
          }}
        >
          ← {annotation}
        </span>
      )}
    </div>
  );
}

/* ── Mock UI elements ────────────────────────────────────── */
function MockButton({
  children,
  highlight,
}: {
  children: React.ReactNode;
  highlight?: boolean;
}) {
  return (
    <span
      style={{
        display: "inline-block",
        padding: "0.375rem 1rem",
        border: highlight
          ? "1.5px solid var(--yellow-chalk)"
          : "1px solid var(--tray)",
        borderRadius: "2px",
        fontFamily: "var(--font-chalk)",
        fontSize: "0.9rem",
        color: highlight ? "var(--yellow-chalk)" : "var(--dust)",
        background: highlight ? "rgba(212, 168, 67, 0.08)" : "transparent",
      }}
    >
      {children}
    </span>
  );
}

function MockInput({ placeholder }: { placeholder: string }) {
  return (
    <span
      style={{
        display: "block",
        borderBottom: "1px solid var(--tray)",
        padding: "0.375rem 0",
        fontFamily: "var(--font-space-mono), monospace",
        fontSize: "0.95rem",
        color: "var(--tray)",
      }}
    >
      {placeholder}
    </span>
  );
}

function MockLabel({ children }: { children: React.ReactNode }) {
  return (
    <span
      style={{
        fontFamily: "var(--font-chalk)",
        fontSize: "0.9rem",
        color: "var(--dust)",
        display: "block",
        marginBottom: "0.25rem",
      }}
    >
      {children}
    </span>
  );
}

/* ── Step component ──────────────────────────────────────── */
function Step({
  number,
  title,
  children,
}: {
  number: number;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section style={{ marginBottom: "2.75rem" }}>
      <div
        style={{
          display: "flex",
          alignItems: "baseline",
          gap: "0.75rem",
          marginBottom: "0.75rem",
        }}
      >
        <span
          style={{
            fontFamily: "var(--font-chalk)",
            fontSize: "1.5rem",
            fontWeight: 700,
            color: "var(--yellow-chalk)",
            lineHeight: 1,
          }}
        >
          {number}.
        </span>
        <h2
          style={{
            fontFamily: "var(--font-serif)",
            fontSize: "1.25rem",
            fontWeight: 400,
            color: "var(--chalk-bright)",
            margin: 0,
          }}
        >
          {title}
        </h2>
      </div>
      {children}
    </section>
  );
}

/* ── Page ──────────────────────────────────────────────────── */
export default function SetupPage() {
  return (
    <div style={{ background: "var(--board)", minHeight: "100vh" }}>
      <Header />

      <main
        style={{
          maxWidth: "720px",
          margin: "0 auto",
          padding: "0 2.5rem 6rem",
        }}
      >
        <section style={{ padding: "3.5rem 0 2.5rem" }}>
          <h1
            style={{
              fontFamily: "var(--font-serif)",
              fontSize: "clamp(2rem, 5vw, 2.75rem)",
              fontWeight: 400,
              lineHeight: 1.15,
              letterSpacing: "-0.02em",
              margin: 0,
              color: "var(--chalk-bright)",
            }}
          >
            Get your OpenRouter key
          </h1>
          <p
            style={{
              marginTop: "1rem",
              lineHeight: 1.6,
              color: "var(--dust)",
              fontFamily: "var(--font-chalk)",
              fontSize: "1.05rem",
            }}
          >
            Takes about 2 minutes. You&apos;ll need a credit card for ~$1 in
            credits.
          </p>
        </section>

        <CharcoalRule />

        <div style={{ paddingTop: "2.5rem" }}>
          {/* Step 1 */}
          <Step number={1} title="Create an account">
            <p
              style={{
                fontFamily: "Georgia, serif",
                fontSize: "0.9375rem",
                lineHeight: 1.7,
                color: "var(--chalk)",
                margin: "0 0 0.75rem",
              }}
            >
              Go to{" "}
              <a
                href="https://openrouter.ai"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  color: "var(--blue-chalk)",
                  textDecoration: "underline",
                  textUnderlineOffset: "2px",
                }}
              >
                openrouter.ai
              </a>{" "}
              and click &ldquo;Get API Key&rdquo; or sign up with Google / GitHub.
            </p>

            <ChalkSketch annotation="homepage">
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <span
                  style={{
                    fontFamily: "var(--font-chalk)",
                    fontSize: "1.1rem",
                    color: "var(--chalk)",
                  }}
                >
                  openrouter.ai
                </span>
                <MockButton highlight>Get API Key</MockButton>
              </div>
              <div
                style={{
                  marginTop: "1rem",
                  fontFamily: "Georgia, serif",
                  fontSize: "0.9rem",
                  color: "var(--dust)",
                  lineHeight: 1.6,
                }}
              >
                A unified API for LLMs — one key, many models.
              </div>
            </ChalkSketch>
          </Step>

          {/* Step 2 */}
          <Step number={2} title="Add credits">
            <p
              style={{
                fontFamily: "Georgia, serif",
                fontSize: "0.9375rem",
                lineHeight: 1.7,
                color: "var(--chalk)",
                margin: "0 0 0.75rem",
              }}
            >
              Navigate to{" "}
              <a
                href="https://openrouter.ai/settings/credits"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  color: "var(--blue-chalk)",
                  textDecoration: "underline",
                  textUnderlineOffset: "2px",
                }}
              >
                Settings → Credits
              </a>
              . Add $5 — enough for 4-5 reviews with an open-source model or 1 review with Claude. Unused credits don&apos;t
              expire.
            </p>

            <ChalkSketch annotation="credits page">
              <MockLabel>Settings → Credits</MockLabel>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "1rem",
                  marginTop: "0.75rem",
                }}
              >
                <div style={{ flex: 1 }}>
                  <MockLabel>Amount</MockLabel>
                  <div
                    style={{
                      borderBottom: "1px solid var(--tray)",
                      padding: "0.375rem 0",
                      fontFamily: "var(--font-space-mono), monospace",
                      fontSize: "0.9rem",
                      color: "var(--chalk)",
                    }}
                  >
                    $5.00
                  </div>
                </div>
                <MockButton highlight>Add credits</MockButton>
              </div>
              <div
                style={{
                  marginTop: "0.75rem",
                  fontFamily: "var(--font-chalk)",
                  fontSize: "0.95rem",
                  color: "var(--dust)",
                }}
              >
                Balance: $0.00
              </div>
            </ChalkSketch>
          </Step>

          {/* Step 3 */}
          <Step number={3} title="Create an API key">
            <p
              style={{
                fontFamily: "Georgia, serif",
                fontSize: "0.9375rem",
                lineHeight: 1.7,
                color: "var(--chalk)",
                margin: "0 0 0.75rem",
              }}
            >
              Go to{" "}
              <a
                href="https://openrouter.ai/settings/keys"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  color: "var(--blue-chalk)",
                  textDecoration: "underline",
                  textUnderlineOffset: "2px",
                }}
              >
                Settings → Keys
              </a>
              , click &ldquo;Create Key&rdquo;, and name it{" "}
              <span
                style={{
                  fontFamily: "var(--font-space-mono), monospace",
                  fontSize: "0.9rem",
                  color: "var(--chalk-bright)",
                }}
              >
                coarse
              </span>
              .
            </p>

            <p
              style={{
                fontFamily: "Georgia, serif",
                fontSize: "0.9375rem",
                lineHeight: 1.7,
                color: "var(--red-chalk)",
                fontStyle: "italic",
                margin: "0 0 0.75rem",
              }}
            >
              Copy the key now — you won&apos;t see it again.
            </p>

            <ChalkSketch annotation="keys page">
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <MockLabel>Settings → Keys</MockLabel>
                <MockButton highlight>Create Key</MockButton>
              </div>
              <div style={{ marginTop: "1rem" }}>
                <MockLabel>Key name</MockLabel>
                <MockInput placeholder="coarse" />
              </div>
              <div
                style={{
                  marginTop: "1rem",
                  padding: "0.5rem 0.75rem",
                  background: "rgba(212, 168, 67, 0.06)",
                  borderRadius: "2px",
                }}
              >
                <MockLabel>Your key</MockLabel>
                <span
                  style={{
                    fontFamily: "var(--font-space-mono), monospace",
                    fontSize: "0.95rem",
                    color: "var(--yellow-chalk)",
                    wordBreak: "break-all",
                  }}
                >
                  sk-or-v1-abc123...def456
                </span>
              </div>
            </ChalkSketch>
          </Step>

          {/* Step 4 — Per-key spend limit */}
          <Step number={4} title="Set a spending limit on the key">
            <p
              style={{
                fontFamily: "Georgia, serif",
                fontSize: "0.9375rem",
                lineHeight: 1.7,
                color: "var(--chalk)",
                margin: "0 0 0.75rem",
              }}
            >
              On the{" "}
              <a
                href="https://openrouter.ai/settings/keys"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  color: "var(--blue-chalk)",
                  textDecoration: "underline",
                  textUnderlineOffset: "2px",
                }}
              >
                Keys page
              </a>
              , click the{" "}
              <strong style={{ color: "var(--chalk-bright)" }}>&#8942;</strong>
              {" "}menu next to your new key and choose &ldquo;Edit&rdquo;. Set a
              credit limit (e.g. $5). The key stops working once the limit is
              hit — zero risk of surprise charges.
            </p>

            <ChalkSketch annotation="key menu">
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div>
                  <MockLabel>coarse</MockLabel>
                  <span
                    style={{
                      fontFamily: "var(--font-space-mono), monospace",
                      fontSize: "0.85rem",
                      color: "var(--dust)",
                    }}
                  >
                    sk-or-v1-abc...def
                  </span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                  <span
                    style={{
                      fontFamily: "var(--font-chalk)",
                      fontSize: "1.25rem",
                      color: "var(--chalk)",
                      cursor: "pointer",
                      letterSpacing: "0.05em",
                    }}
                  >
                    &#8942;
                  </span>
                  <div
                    style={{
                      background: "var(--board-surface)",
                      border: "1px solid var(--tray)",
                      borderRadius: "2px",
                      padding: "0.25rem 0",
                    }}
                  >
                    <div
                      style={{
                        padding: "0.35rem 0.75rem",
                        fontFamily: "var(--font-chalk)",
                        fontSize: "0.9rem",
                        color: "var(--yellow-chalk)",
                      }}
                    >
                      Edit
                    </div>
                  </div>
                </div>
              </div>
              <div style={{ marginTop: "1rem" }}>
                <MockLabel>Credit limit for this key</MockLabel>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "1rem",
                    marginTop: "0.25rem",
                  }}
                >
                  <div
                    style={{
                      borderBottom: "1px solid var(--yellow-chalk)",
                      padding: "0.375rem 0",
                      fontFamily: "var(--font-space-mono), monospace",
                      fontSize: "0.9rem",
                      color: "var(--yellow-chalk)",
                      width: "80px",
                    }}
                  >
                    $5.00
                  </div>
                  <MockButton highlight>Save</MockButton>
                </div>
              </div>
            </ChalkSketch>

            <div
              style={{
                marginTop: "1rem",
                padding: "0.75rem 1rem",
                background: "rgba(123, 167, 188, 0.06)",
                borderLeft: "3px solid var(--blue-chalk)",
                borderRadius: "0 2px 2px 0",
              }}
            >
              <p
                style={{
                  fontFamily: "Georgia, serif",
                  fontSize: "0.875rem",
                  lineHeight: 1.6,
                  color: "var(--chalk)",
                  margin: 0,
                }}
              >
                <strong style={{ color: "var(--chalk-bright)" }}>
                  Why this matters:
                </strong>{" "}
                coarse is open-source — you can{" "}
                <a
                  href="https://github.com/Davidvandijcke/coarse"
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    color: "var(--blue-chalk)",
                    textDecoration: "underline",
                    textUnderlineOffset: "2px",
                  }}
                >
                  read every line of code
                </a>
                . Your key is sent directly to OpenRouter to run the review, then
                discarded — it is never stored. But you don&apos;t have to trust
                us: the per-key limit guarantees it can never spend more than you
                allow, even in the worst case.
              </p>
            </div>
          </Step>

          {/* Step 5 */}
          <Step number={5} title="Paste into coarse">
            <p
              style={{
                fontFamily: "Georgia, serif",
                fontSize: "0.9375rem",
                lineHeight: 1.7,
                color: "var(--chalk)",
                margin: "0 0 0.75rem",
              }}
            >
              Come back here, paste your key into the form, and upload your PDF.
            </p>

            <ChalkSketch annotation="coarse form">
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "1.25rem",
                }}
              >
                <div>
                  <MockLabel>Email</MockLabel>
                  <MockInput placeholder="you@university.edu" />
                </div>
                <div>
                  <MockLabel>OpenRouter key</MockLabel>
                  <div
                    style={{
                      borderBottom: "1px solid var(--yellow-chalk)",
                      padding: "0.375rem 0",
                      fontFamily: "var(--font-space-mono), monospace",
                      fontSize: "0.95rem",
                      color: "var(--yellow-chalk)",
                    }}
                  >
                    sk-or-v1-...
                  </div>
                </div>
              </div>
              <div style={{ marginTop: "1rem" }}>
                <MockButton highlight>Review my paper</MockButton>
              </div>
            </ChalkSketch>
          </Step>
        </div>

        <CharcoalRule />

        <section style={{ padding: "2.5rem 0 0", textAlign: "center" }}>
          <a
            href="/"
            style={{
              fontFamily: "var(--font-chalk)",
              fontSize: "1.2rem",
              color: "var(--yellow-chalk)",
              textDecoration: "none",
            }}
          >
            Ready? Review your paper →
          </a>
        </section>
      </main>
    </div>
  );
}
