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
              . Add at least $20. A single review costs roughly $0.25&ndash;$2
              depending on the model, so $20 covers multiple reviews and gives
              each one enough headroom to finish. The estimate you see before
              you submit is a ballpark, not a ceiling &mdash; complex papers
              with lots of math can cost closer to 2&times; the estimate.
              If you leave too little headroom on the key, a single review can
              exhaust it and fail halfway. Unused credits don&apos;t expire.
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
              {" "}menu next to your new key and choose &ldquo;Edit&rdquo;.
              Set the credit limit to{" "}
              <strong style={{ color: "var(--chalk-bright)" }}>
                at least $20
              </strong>
              . The key stops working once the limit is hit, so there&apos;s
              zero risk of surprise charges. But set it too tight and you pay
              for that in a different currency: a single review can burn
              through a too-low cap and fail halfway, leaving you with nothing
              to show for the spend. The $20 floor gives any single review
              roughly 10&times; the headroom it needs even on a big paper.
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
                coarse shows an approximate cost before each review (typically
                $0.25&ndash;$2). That&apos;s a heuristic with a ~15% buffer, not
                a hard ceiling. Actual cost can run up to ~2&times; the estimate
                on complex papers depending on how much the model reasons,
                how the critique agent rewrites comments, and whether
                proof-verification kicks in for math-heavy sections. If your
                per-key limit is set right at the estimate, a single review can
                drain it and fail mid-run. Leave headroom.
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
          You pay OpenRouter about $0.15 for the OCR pass. The review itself
          runs on your existing Claude Code, Codex, or Gemini CLI
          subscription, so there are no per-token LLM charges on top.
        </p>
        <div
          style={{
            marginTop: "1.25rem",
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
              When to use this path:
            </strong>{" "}
            you&apos;re already paying Anthropic Pro, ChatGPT Plus, or Google
            for a coding-agent subscription and would rather not pay
            OpenRouter twice. The review runs on your own machine (or your
            Codex cloud sandbox), bills against your existing plan, and lands
            back on coarse.ink when it&apos;s done.
          </p>
        </div>
      </section>

      <CharcoalRule />

      <div style={{ paddingTop: "2.5rem" }}>
        {/* Step 1 */}
        <Step number={1} title="Install one of the coding agents">
          <p
            style={{
              fontFamily: "Georgia, serif",
              fontSize: "1.1rem",
              lineHeight: 1.7,
              color: "var(--chalk)",
              margin: "0 0 0.75rem",
            }}
          >
            Pick whichever one you already pay for. If you don&apos;t pay for
            any of them yet, Gemini CLI has a free tier that works for most
            papers. Install and then log in on the vendor&apos;s own page
            &mdash; those docs update faster than anything we could copy here.
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
              note="If you use the terminal CLI, install it with npm or Homebrew first, then run claude login and follow the browser prompt."
            />
            <AgentCard
              name="Codex"
              price="ChatGPT Plus, Pro, or Business"
              installHref="https://developers.openai.com/codex/cli"
              installLabel="Install instructions ↗"
              loginCmd="codex login"
              testCmd="codex exec 'say hi'"
              note="After install, run codex login and sign in with the same ChatGPT account that has your Plus/Pro subscription. The free ChatGPT tier does not include Codex."
            />
            <AgentCard
              name="Gemini CLI"
              price="Free tier works, Google AI Pro for heavier use"
              installHref="https://github.com/google-gemini/gemini-cli#quickstart"
              installLabel="Install instructions ↗"
              loginCmd="gemini"
              testCmd="gemini -p 'say hi'"
              note="Run gemini once to trigger the login flow. The free tier gives you enough to review several papers a day."
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
            Open a terminal and run the &ldquo;test&rdquo; command above. If
            you see a response, you&apos;re set. If you see
            &ldquo;command not found,&rdquo; the CLI isn&apos;t on your{" "}
            <code
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.95rem",
                color: "var(--chalk-bright)",
              }}
            >
              PATH
            </code>
            {" "}&mdash; follow the install guide&apos;s troubleshooting
            section before continuing.
          </p>
        </Step>

        {/* Step 2 */}
        <Step number={2} title="Add $1 to OpenRouter for extraction">
          <p
            style={{
              fontFamily: "Georgia, serif",
              fontSize: "1.1rem",
              lineHeight: 1.7,
              color: "var(--chalk)",
              margin: "0 0 0.75rem",
            }}
          >
            coarse still needs OpenRouter for the OCR pass that turns your PDF
            into text. That costs about $0.10 per paper, no matter which
            coding agent runs the review itself. Follow the{" "}
            <strong style={{ color: "var(--chalk-bright)" }}>
              OpenRouter key
            </strong>{" "}
            tab on this page to create an account and add credit. $1 is
            plenty &mdash; you won&apos;t need the $20 buffer because
            extraction is cheap and bounded, and the review itself bills
            against your subscription, not OpenRouter.
          </p>
          <p
            style={{
              fontFamily: "Georgia, serif",
              fontSize: "1.05rem",
              lineHeight: 1.7,
              color: "var(--dust)",
              margin: 0,
            }}
          >
            You still want the per-key spend limit from step 4 of the
            OpenRouter tab, just set it to $2 instead of $20.
          </p>
        </Step>

        {/* Step 3 */}
        <Step number={3} title="Upload your paper">
          <p
            style={{
              fontFamily: "Georgia, serif",
              fontSize: "1.1rem",
              lineHeight: 1.7,
              color: "var(--chalk)",
              margin: "0 0 0.75rem",
            }}
          >
            Go to the{" "}
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
            , drop your PDF onto the form, paste your OpenRouter key, and
            click{" "}
            <strong style={{ color: "var(--chalk-bright)" }}>
              Review with my subscription
            </strong>
            . Pick which CLI you want to use in the modal that appears.
          </p>
        </Step>

        {/* Step 4 */}
        <Step number={4} title="Run the commands in your terminal">
          <p
            style={{
              fontFamily: "Georgia, serif",
              fontSize: "1.1rem",
              lineHeight: 1.7,
              color: "var(--chalk)",
              margin: "0 0 0.75rem",
            }}
          >
            The modal shows three commands. They&apos;re already filled in
            with your paper&apos;s handoff URL, so you don&apos;t need to edit
            anything.
          </p>

          <ol
            style={{
              fontFamily: "Georgia, serif",
              fontSize: "1.1rem",
              lineHeight: 1.7,
              color: "var(--chalk)",
              margin: "0 0 0.75rem",
              paddingLeft: "1.25rem",
            }}
          >
            <li style={{ marginBottom: "0.5rem" }}>
              <strong style={{ color: "var(--chalk-bright)" }}>Setup</strong>{" "}
              refreshes the coarse skill bundle in your CLI&apos;s skill
              folder. Takes about 10 seconds and is safe to run every time.
            </li>
            <li style={{ marginBottom: "0.5rem" }}>
              <strong style={{ color: "var(--chalk-bright)" }}>Launch</strong>{" "}
              kicks off the review in the background and returns within 2
              seconds. It prints a log file path and a PID. Keep the terminal
              open.
            </li>
            <li>
              <strong style={{ color: "var(--chalk-bright)" }}>
                Wait
              </strong>{" "}
              blocks until the review finishes. Expect 10&ndash;25 minutes.
              You can Ctrl+C out of this one; the review keeps running and
              you can re-attach with the same command.
            </li>
          </ol>

          <p
            style={{
              fontFamily: "Georgia, serif",
              fontSize: "1.1rem",
              lineHeight: 1.7,
              color: "var(--chalk)",
              margin: "0 0 0.75rem",
            }}
          >
            Open whichever CLI you installed in step 1 and paste each command
            in order. When the third command exits, it prints a{" "}
            <code
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.95rem",
                color: "var(--chalk-bright)",
              }}
            >
              view:
            </code>{" "}
            line with a clickable URL. Click it and your finished review opens
            on coarse.ink.
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
                Tool-timeout tip for coding agents:
              </strong>{" "}
              if you&apos;re pasting the commands into Claude Code, Codex, or
              Gemini CLI itself (instead of a plain terminal), bump the bash
              tool timeout to at least 45 minutes before running the wait
              command. The review takes 10&ndash;25 minutes and agents have
              default timeouts as low as 2 minutes.
            </p>
          </div>
        </Step>

        {/* Step 5 — Troubleshooting */}
        <Step number={5} title="If something goes wrong">
          <Trouble
            symptom="The &ldquo;Open Claude Code&rdquo; button in the modal does nothing."
            fix={
              <>
                That button tries to launch the Claude Code desktop app via a{" "}
                <code
                  style={{
                    fontFamily: "var(--font-space-mono), monospace",
                    fontSize: "0.95rem",
                    color: "var(--chalk-bright)",
                  }}
                >
                  claude://
                </code>{" "}
                protocol URL. It only works if you have the Claude desktop app
                installed. If you installed Claude Code as a CLI tool (the
                most common case), the browser can&apos;t open a terminal for
                you. Copy the three commands from the modal and paste them
                into your terminal manually.
              </>
            }
          />
          <Trouble
            symptom="&ldquo;No such command &lsquo;install-skills&rsquo;&rdquo; during the setup step."
            fix={
              <>
                Safe to ignore. The launch command loads the coarse code
                via{" "}
                <code
                  style={{
                    fontFamily: "var(--font-space-mono), monospace",
                    fontSize: "0.95rem",
                    color: "var(--chalk-bright)",
                  }}
                >
                  uvx --from
                </code>{" "}
                and doesn&apos;t need the skill folder. Move on.
              </>
            }
          />
          <Trouble
            symptom="My Anthropic bill went up right after I ran a review."
            fix={
              <>
                Check whether you have{" "}
                <code
                  style={{
                    fontFamily: "var(--font-space-mono), monospace",
                    fontSize: "0.95rem",
                    color: "var(--chalk-bright)",
                  }}
                >
                  ANTHROPIC_API_KEY
                </code>{" "}
                set in your shell. Claude Code&apos;s documented behavior is:
                if the key is set, it bills the API account instead of your
                subscription. coarse-review strips this variable from the
                child process before running{" "}
                <code
                  style={{
                    fontFamily: "var(--font-space-mono), monospace",
                    fontSize: "0.95rem",
                    color: "var(--chalk-bright)",
                  }}
                >
                  claude -p
                </code>
                , but older versions (before v1.3.0) didn&apos;t. If you
                upgraded partway through, it&apos;s worth double-checking
                your billing dashboard and the env var. Same thing applies
                to{" "}
                <code
                  style={{
                    fontFamily: "var(--font-space-mono), monospace",
                    fontSize: "0.95rem",
                    color: "var(--chalk-bright)",
                  }}
                >
                  OPENAI_API_KEY
                </code>{" "}
                / Codex and{" "}
                <code
                  style={{
                    fontFamily: "var(--font-space-mono), monospace",
                    fontSize: "0.95rem",
                    color: "var(--chalk-bright)",
                  }}
                >
                  GOOGLE_API_KEY
                </code>{" "}
                / Gemini.
              </>
            }
          />
          <Trouble
            symptom="The wait command exits but I only see 10 detailed comments instead of the usual 20."
            fix={
              <>
                One or more section-review calls hit their 30-minute timeout
                and got dropped. This is rare on the default effort level but
                can happen with{" "}
                <code
                  style={{
                    fontFamily: "var(--font-space-mono), monospace",
                    fontSize: "0.95rem",
                    color: "var(--chalk-bright)",
                  }}
                >
                  --effort max
                </code>{" "}
                on a book-length paper. Re-run the review on the same paper
                and you&apos;ll typically get a full comment set the second
                time. If it happens twice in a row, drop the effort one
                notch.
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
  note,
}: {
  name: string;
  price: string;
  installHref: string;
  installLabel: string;
  loginCmd: string;
  testCmd: string;
  note: string;
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
      <p
        style={{
          marginTop: "0.65rem",
          marginBottom: 0,
          fontFamily: "Georgia, serif",
          fontSize: "0.95rem",
          lineHeight: 1.55,
          color: "var(--dust)",
        }}
      >
        {note}
      </p>
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
