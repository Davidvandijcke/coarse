"use client";

import { useState } from "react";

import { CharcoalRule } from "@/components/charcoal";

type SetupTab = "openrouter" | "subscription";

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
            fontSize: "1.1rem",
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
            fontSize: "1.1rem",
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
        fontSize: "1.05rem",
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
        fontSize: "1.1rem",
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
        fontSize: "1.05rem",
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

/* ── Tab switcher ────────────────────────────────────────── */
function TabSwitcher({
  active,
  onChange,
}: {
  active: SetupTab;
  onChange: (tab: SetupTab) => void;
}) {
  const tabStyle = (isActive: boolean): React.CSSProperties => ({
    padding: "0.625rem 1.25rem",
    fontFamily: "var(--font-chalk)",
    fontSize: "1.1rem",
    color: isActive ? "var(--yellow-chalk)" : "var(--dust)",
    background: isActive ? "rgba(212, 168, 67, 0.08)" : "transparent",
    border: isActive
      ? "1.5px solid var(--yellow-chalk)"
      : "1px solid var(--tray)",
    borderRadius: "2px",
    cursor: "pointer",
    transition: "color 0.2s, background 0.2s, border-color 0.2s",
  });
  return (
    <div
      role="tablist"
      aria-label="Setup path"
      style={{
        display: "flex",
        gap: "0.75rem",
        flexWrap: "wrap",
        marginTop: "3rem",
        marginBottom: "0.5rem",
      }}
    >
      <button
        role="tab"
        aria-selected={active === "openrouter"}
        type="button"
        onClick={() => onChange("openrouter")}
        style={tabStyle(active === "openrouter")}
      >
        OpenRouter key
      </button>
      <button
        role="tab"
        aria-selected={active === "subscription"}
        type="button"
        onClick={() => onChange("subscription")}
        style={tabStyle(active === "subscription")}
      >
        Use my subscription
      </button>
    </div>
  );
}

/* ── OpenRouter tab (direct key flow) ────────────────────── */
function OpenRouterTab() {
  return (
    <>
      <section style={{ padding: "1.5rem 0 2.5rem" }}>
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
          credits to get started &mdash; you&apos;ll top up to $20 in step 2.
        </p>
          <div
            style={{
              marginTop: "1.25rem",
              padding: "0.75rem 1rem",
              background: "rgba(224, 201, 112, 0.06)",
              borderLeft: "3px solid var(--yellow-chalk)",
              borderRadius: "0 2px 2px 0",
            }}
          >
            <p
              style={{
                fontFamily: "Georgia, serif",
                fontSize: "1rem",
                lineHeight: 1.6,
                color: "var(--chalk)",
                margin: 0,
              }}
            >
              <strong style={{ color: "var(--chalk-bright)" }}>Faster option:</strong>{" "}
              on the main form you can click{" "}
              <strong style={{ color: "var(--chalk-bright)" }}>&ldquo;Log in with OpenRouter&rdquo;</strong>{" "}
              to authorize coarse and skip manual key creation. You still need an
              OpenRouter account with credits (steps 1 and 2 below), and we still
              recommend setting a per-key spend limit (step 4).
            </p>
          </div>
        </section>

        <CharcoalRule />

        <div style={{ paddingTop: "2.5rem" }}>
          {/* Step 1 */}
          <Step number={1} title="Create an account">
            <p
              style={{
                fontFamily: "Georgia, serif",
                fontSize: "1.1rem",
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
                  fontSize: "1.05rem",
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
                fontSize: "1.1rem",
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
              . Add at least $20. Cheap open-source models cost
              ~$0.25 per review; SOTA models like Claude Opus or GPT-5 can
              run $5&ndash;$10 on a long paper. The cost estimate shown
              before submission is a ballpark, not a ceiling. Leave headroom
              or the review can exhaust the key halfway and fail. Unused
              credits don&apos;t expire.
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
                      fontSize: "1.05rem",
                      color: "var(--chalk)",
                    }}
                  >
                    $20.00
                  </div>
                </div>
                <MockButton highlight>Add credits</MockButton>
              </div>
              <div
                style={{
                  marginTop: "0.75rem",
                  fontFamily: "var(--font-chalk)",
                  fontSize: "1.1rem",
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
                fontSize: "1.1rem",
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
                  fontSize: "1.05rem",
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
                fontSize: "1.1rem",
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
                    fontSize: "1.1rem",
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
                fontSize: "1.1rem",
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
              {" "}menu next to your new key, choose &ldquo;Edit&rdquo;, and
              set the credit limit to{" "}
              <strong style={{ color: "var(--chalk-bright)" }}>
                at least $20
              </strong>
              . The key stops working once the limit is hit, so surprise
              charges are impossible. But set it too tight and a single
              expensive review can exhaust it mid-run.
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
                      fontSize: "1rem",
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
                        fontSize: "1.05rem",
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
                      fontSize: "1.05rem",
                      color: "var(--yellow-chalk)",
                      width: "80px",
                    }}
                  >
                    $20.00
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
                  fontSize: "1rem",
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

            <div
              style={{
                marginTop: "0.75rem",
                padding: "0.75rem 1rem",
                background: "rgba(224, 201, 112, 0.06)",
                borderLeft: "3px solid var(--yellow-chalk)",
                borderRadius: "0 2px 2px 0",
              }}
            >
              <p
                style={{
                  fontFamily: "Georgia, serif",
                  fontSize: "1rem",
                  lineHeight: 1.6,
                  color: "var(--chalk)",
                  margin: 0,
                }}
              >
                <strong style={{ color: "var(--chalk-bright)" }}>
                  A note on cost estimates:
                </strong>{" "}
                the estimate shown before submission is a heuristic with a
                ~15% buffer, not a hard ceiling. Actual cost on SOTA models
                with long papers can run up to ~2&times; the estimate once
                proof-verification and critique rewrites kick in. If the
                per-key cap sits right at the estimate, one tough review can
                drain it and fail mid-run. Always leave headroom.
              </p>
            </div>
          </Step>

          {/* Step 5 */}
          <Step number={5} title="Paste into coarse">
            <p
              style={{
                fontFamily: "Georgia, serif",
                fontSize: "1.1rem",
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
                      fontSize: "1.1rem",
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
    </>
  );
}

/* ── Subscription tab (Claude Code / Codex / Gemini CLI) ─── */
function SubscriptionTab() {
  return (
    <>
      <section style={{ padding: "1.5rem 0 2.5rem" }}>
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
          Use your coding-agent subscription
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
          For users already paying for Claude Code, Codex, or Gemini CLI.
          The review runs on your subscription and bills there. You only
          pay OpenRouter ~$0.15 for the OCR pass.
        </p>
        <p
          style={{
            marginTop: "1rem",
            fontFamily: "var(--font-chalk)",
            fontSize: "0.95rem",
            color: "var(--dust)",
            lineHeight: 1.55,
            maxWidth: "620px",
          }}
        >
          Runs locally on your machine using your own Claude Code, Codex,
          or Gemini CLI account. coarse.ink does not receive or store your
          provider login. Your provider&apos;s terms and usage limits still
          apply. coarse.ink is not affiliated with Anthropic, OpenAI, or
          Google.
        </p>
      </section>

      <CharcoalRule />

      <div style={{ paddingTop: "2.5rem" }}>
        {/* Step 1 */}
        <Step number={1} title="Install a coding agent">
          <p
            style={{
              fontFamily: "Georgia, serif",
              fontSize: "1.1rem",
              lineHeight: 1.7,
              color: "var(--chalk)",
              margin: "0 0 0.75rem",
            }}
          >
            Pick whichever one you pay for. Gemini CLI has a free tier if
            you don&apos;t. Install it from the vendor&apos;s own page &mdash;
            their docs stay up to date.
          </p>

          <div
            style={{
              display: "grid",
              gap: "0.75rem",
              marginTop: "1rem",
            }}
          >
            <AgentCard
              name="Claude Code"
              price="Anthropic Pro or Max"
              installHref="https://docs.claude.com/en/docs/claude-code/setup"
              installLabel="Install instructions ↗"
              loginCmd="claude login"
              testCmd="claude -p 'say hi'"
            />
            <AgentCard
              name="Codex"
              price="ChatGPT Plus, Pro, or Business"
              installHref="https://developers.openai.com/codex/cli"
              installLabel="Install instructions ↗"
              loginCmd="codex login"
              testCmd="codex exec 'say hi'"
            />
            <AgentCard
              name="Gemini CLI"
              price="Free tier works for most papers"
              installHref="https://github.com/google-gemini/gemini-cli#quickstart"
              installLabel="Install instructions ↗"
              loginCmd="gemini"
              testCmd="gemini -p 'say hi'"
            />
          </div>

          <p
            style={{
              marginTop: "1.25rem",
              fontFamily: "Georgia, serif",
              fontSize: "1.05rem",
              lineHeight: 1.7,
              color: "var(--chalk)",
            }}
          >
            Run the test command to verify install + login. If it prints a
            response, you&apos;re set.
          </p>
        </Step>

        {/* Step 2 */}
        <Step number={2} title="Put an OpenRouter key on your machine">
          <p
            style={{
              fontFamily: "Georgia, serif",
              fontSize: "1.1rem",
              lineHeight: 1.7,
              color: "var(--chalk)",
              margin: "0 0 0.75rem",
            }}
          >
            coarse still needs OpenRouter for the OCR step (~$0.10 per
            paper). Follow the{" "}
            <strong style={{ color: "var(--chalk-bright)" }}>
              OpenRouter key
            </strong>{" "}
            tab to create an account, add $1 of credit, and set a $2
            per-key limit. The $20 buffer from the OpenRouter-only path
            isn&apos;t needed here because the review itself runs on
            your coding-agent subscription.
          </p>
          <p
            style={{
              fontFamily: "Georgia, serif",
              fontSize: "1.1rem",
              lineHeight: 1.7,
              color: "var(--chalk)",
              margin: 0,
            }}
          >
            Then put the key on your own machine: run{" "}
            <code
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.95rem",
                color: "var(--chalk-bright)",
              }}
            >
              export OPENROUTER_API_KEY=sk-or-v1-...
            </code>
            , drop it in a{" "}
            <code
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.95rem",
                color: "var(--chalk-bright)",
              }}
            >
              .env
            </code>
            , or save it to{" "}
            <code
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.95rem",
                color: "var(--chalk-bright)",
              }}
            >
              ~/.coarse/config.toml
            </code>
            . Your CLI reads it locally when it runs the extraction;
            coarse.ink never sees it.
          </p>
        </Step>

        {/* Step 3 */}
        <Step number={3} title="Upload your paper and pick a CLI">
          <p
            style={{
              fontFamily: "Georgia, serif",
              fontSize: "1.1rem",
              lineHeight: 1.7,
              color: "var(--chalk)",
              margin: 0,
            }}
          >
            On the{" "}
            <a
              href="/"
              style={{
                color: "var(--blue-chalk)",
                textDecoration: "underline",
                textUnderlineOffset: "2px",
              }}
            >
              main page
            </a>
            , drop your PDF onto the form, then click the{" "}
            <strong style={{ color: "var(--chalk-bright)" }}>
              Review with my subscription ▾
            </strong>{" "}
            dropdown and pick your CLI. coarse uploads the file, mints a
            handoff token, and shows the prompt you&apos;ll paste in the
            next step. You don&apos;t paste your OpenRouter key on the
            form here; the CLI reads it from your machine (step 2).
          </p>
        </Step>

        {/* Step 4 */}
        <Step number={4} title="Paste the prompt into your CLI">
          <p
            style={{
              fontFamily: "Georgia, serif",
              fontSize: "1.1rem",
              lineHeight: 1.7,
              color: "var(--chalk)",
              margin: "0 0 0.75rem",
            }}
          >
            coarse gives you one natural-language prompt. Copy it from
            the panel, paste it into your{" "}
            <code
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.95rem",
                color: "var(--chalk-bright)",
              }}
            >
              claude -p
            </code>
            ,{" "}
            <code
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.95rem",
                color: "var(--chalk-bright)",
              }}
            >
              codex exec
            </code>
            , or{" "}
            <code
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.95rem",
                color: "var(--chalk-bright)",
              }}
            >
              gemini -p
            </code>{" "}
            session, and hit send. The agent refreshes its skill bundle,
            runs the full coarse pipeline on its own subprocess calls,
            and prints a{" "}
            <code
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.95rem",
                color: "var(--chalk-bright)",
              }}
            >
              view:
            </code>{" "}
            URL when it&apos;s done. 10&ndash;25 minutes. Click the URL
            to open the finished review on coarse.ink.
          </p>

          <div
            style={{
              marginTop: "1rem",
              padding: "0.75rem 1rem",
              background: "rgba(224, 201, 112, 0.06)",
              borderLeft: "3px solid var(--yellow-chalk)",
              borderRadius: "0 2px 2px 0",
            }}
          >
            <p
              style={{
                fontFamily: "Georgia, serif",
                fontSize: "1rem",
                lineHeight: 1.6,
                color: "var(--chalk)",
                margin: 0,
              }}
            >
              <strong style={{ color: "var(--chalk-bright)" }}>
                If you&apos;re pasting into a coding agent
              </strong>{" "}
              (not a plain terminal), bump its bash-tool timeout to at
              least 45 min before you send the prompt. Default agent
              timeouts can be as low as 2 min, way under the 10&ndash;25
              min review runtime.
            </p>
          </div>
        </Step>

        {/* Step 5 — Troubleshooting */}
        <Step number={5} title="If something goes wrong">
          <Trouble
            symptom="The &ldquo;Try opening Claude Code / Codex&rdquo; button does nothing."
            fix={
              <>
                The button only works if you have the desktop app
                installed. With a CLI-only install, the browser
                can&apos;t launch a terminal for you. Copy the prompt
                from the panel and paste it into your CLI manually.
              </>
            }
          />
          <Trouble
            symptom="&ldquo;No such command &lsquo;install-skills&rsquo;&rdquo; inside the agent run."
            fix={
              <>
                Safe to ignore. The skill bundle still loads directly
                through{" "}
                <code
                  style={{
                    fontFamily: "var(--font-space-mono), monospace",
                    fontSize: "0.95rem",
                    color: "var(--chalk-bright)",
                  }}
                >
                  uvx --from
                </code>
                ; the agent will continue to the review step.
              </>
            }
          />
          <Trouble
            symptom="My Anthropic / OpenAI / Google bill went up after a review."
            fix={
              <>
                Check for{" "}
                <code
                  style={{
                    fontFamily: "var(--font-space-mono), monospace",
                    fontSize: "0.95rem",
                    color: "var(--chalk-bright)",
                  }}
                >
                  ANTHROPIC_API_KEY
                </code>
                ,{" "}
                <code
                  style={{
                    fontFamily: "var(--font-space-mono), monospace",
                    fontSize: "0.95rem",
                    color: "var(--chalk-bright)",
                  }}
                >
                  OPENAI_API_KEY
                </code>
                , or{" "}
                <code
                  style={{
                    fontFamily: "var(--font-space-mono), monospace",
                    fontSize: "0.95rem",
                    color: "var(--chalk-bright)",
                  }}
                >
                  GOOGLE_API_KEY
                </code>{" "}
                in your shell environment. If set, the host CLI bills the
                API account instead of your subscription. v1.3.0+ strips
                these automatically, but older versions didn&apos;t.
              </>
            }
          />
          <Trouble
            symptom="Fewer comments than usual (~10 instead of 15&ndash;25)."
            fix={
              <>
                A section hit the 30-min timeout and got dropped. Rare on
                default effort, more common with{" "}
                <code
                  style={{
                    fontFamily: "var(--font-space-mono), monospace",
                    fontSize: "0.95rem",
                    color: "var(--chalk-bright)",
                  }}
                >
                  --effort max
                </code>{" "}
                on long papers. Re-run; drop effort one notch if it
                happens twice.
              </>
            }
          />
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
    </>
  );
}

/* ── Helpers for the subscription tab ────────────────────── */
function AgentCard({
  name,
  price,
  installHref,
  installLabel,
  loginCmd,
  testCmd,
}: {
  name: string;
  price: string;
  installHref: string;
  installLabel: string;
  loginCmd: string;
  testCmd: string;
}) {
  return (
    <div
      style={{
        background: "var(--board-surface)",
        border: "1px dashed var(--tray)",
        borderRadius: "2px",
        padding: "1rem 1.25rem",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "baseline",
          justifyContent: "space-between",
          gap: "1rem",
          flexWrap: "wrap",
        }}
      >
        <div>
          <div
            style={{
              fontFamily: "var(--font-serif)",
              fontSize: "1.2rem",
              color: "var(--chalk-bright)",
            }}
          >
            {name}
          </div>
          <div
            style={{
              fontFamily: "var(--font-chalk)",
              fontSize: "1rem",
              color: "var(--dust)",
              marginTop: "0.2rem",
            }}
          >
            {price}
          </div>
        </div>
        <a
          href={installHref}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            fontFamily: "var(--font-chalk)",
            fontSize: "1rem",
            color: "var(--blue-chalk)",
            textDecoration: "none",
            border: "1px solid var(--tray)",
            borderRadius: "2px",
            padding: "0.25rem 0.6rem",
          }}
        >
          {installLabel}
        </a>
      </div>
      <div
        style={{
          marginTop: "0.75rem",
          display: "flex",
          gap: "1.5rem",
          flexWrap: "wrap",
          fontFamily: "var(--font-space-mono), monospace",
          fontSize: "0.95rem",
          color: "var(--chalk)",
        }}
      >
        <div>
          <span style={{ color: "var(--dust)" }}>login: </span>
          {loginCmd}
        </div>
        <div>
          <span style={{ color: "var(--dust)" }}>test: </span>
          {testCmd}
        </div>
      </div>
    </div>
  );
}

function Trouble({
  symptom,
  fix,
}: {
  symptom: string;
  fix: React.ReactNode;
}) {
  return (
    <div
      style={{
        marginTop: "0.9rem",
        padding: "0.75rem 1rem",
        background: "var(--board-surface)",
        border: "1px dashed var(--tray)",
        borderRadius: "2px",
      }}
    >
      <div
        style={{
          fontFamily: "var(--font-chalk)",
          fontSize: "1.05rem",
          color: "var(--red-chalk)",
          marginBottom: "0.35rem",
        }}
      >
        {symptom}
      </div>
      <div
        style={{
          fontFamily: "Georgia, serif",
          fontSize: "1rem",
          lineHeight: 1.6,
          color: "var(--chalk)",
        }}
      >
        {fix}
      </div>
    </div>
  );
}

/* ── Page ──────────────────────────────────────────────────── */
export default function SetupPage() {
  const [tab, setTab] = useState<SetupTab>("openrouter");
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
        <TabSwitcher active={tab} onChange={setTab} />
        {tab === "openrouter" ? <OpenRouterTab /> : <SubscriptionTab />}
      </main>
    </div>
  );
}
