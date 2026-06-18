"use client";

import { useState } from "react";

import { CharcoalRule } from "@/components/charcoal";
import { SiteLanguageProvider, useSiteLanguageContext } from "@/lib/i18n";

type SetupTab = "openrouter" | "subscription";

/* ── Header (matching landing page) ──────────────────────── */
function Header() {
  const { t } = useSiteLanguageContext();
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
          {t("headerTagline")}
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
          {t("navSetup")}
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
          {t("navSideBySide")}
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
          {t("navGithub")}
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
  const { t } = useSiteLanguageContext();
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
      aria-label={t("setupTablistAriaLabel")}
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
        {t("setupTabOpenRouter")}
      </button>
      <button
        role="tab"
        aria-selected={active === "subscription"}
        type="button"
        onClick={() => onChange("subscription")}
        style={tabStyle(active === "subscription")}
      >
        {t("setupTabSubscription")}
      </button>
    </div>
  );
}

/* ── OpenRouter tab (direct key flow) ────────────────────── */
function OpenRouterTab() {
  const { t } = useSiteLanguageContext();
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
          {t("setupOrHeading")}
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
          {t("setupOrIntro")}
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
              <strong style={{ color: "var(--chalk-bright)" }}>{t("setupOrFasterLabel")}</strong>
              {t("setupOrFasterMid1")}
              <strong style={{ color: "var(--chalk-bright)" }}>{t("setupOrFasterLogIn")}</strong>
              {t("setupOrFasterSuffix")}
            </p>
          </div>
        </section>

        <CharcoalRule />

        <div style={{ paddingTop: "2.5rem" }}>
          {/* Step 1 */}
          <Step number={1} title={t("setupOrStep1Title")}>
            <p
              style={{
                fontFamily: "Georgia, serif",
                fontSize: "1.1rem",
                lineHeight: 1.7,
                color: "var(--chalk)",
                margin: "0 0 0.75rem",
              }}
            >
              {t("setupOrStep1BodyPrefix")}
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
              </a>
              {t("setupOrStep1BodySuffix")}
            </p>

            <ChalkSketch annotation={t("setupOrStep1Annotation")}>
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
                <MockButton highlight>{t("setupOrStep1MockButton")}</MockButton>
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
                {t("setupOrStep1MockTagline")}
              </div>
            </ChalkSketch>
          </Step>

          {/* Step 2 */}
          <Step number={2} title={t("setupOrStep2Title")}>
            <p
              style={{
                fontFamily: "Georgia, serif",
                fontSize: "1.1rem",
                lineHeight: 1.7,
                color: "var(--chalk)",
                margin: "0 0 0.75rem",
              }}
            >
              {t("setupOrStep2BodyPrefix")}
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
                {t("setupOrStep2BodyLink")}
              </a>
              {t("setupOrStep2BodySuffix")}
            </p>

            <ChalkSketch annotation={t("setupOrStep2Annotation")}>
              <MockLabel>{t("setupOrStep2MockSettings")}</MockLabel>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "1rem",
                  marginTop: "0.75rem",
                }}
              >
                <div style={{ flex: 1 }}>
                  <MockLabel>{t("setupOrStep2MockAmount")}</MockLabel>
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
                <MockButton highlight>{t("setupOrStep2MockButton")}</MockButton>
              </div>
              <div
                style={{
                  marginTop: "0.75rem",
                  fontFamily: "var(--font-chalk)",
                  fontSize: "1.1rem",
                  color: "var(--dust)",
                }}
              >
                {t("setupOrStep2MockBalance")}
              </div>
            </ChalkSketch>
          </Step>

          {/* Step 3 */}
          <Step number={3} title={t("setupOrStep3Title")}>
            <p
              style={{
                fontFamily: "Georgia, serif",
                fontSize: "1.1rem",
                lineHeight: 1.7,
                color: "var(--chalk)",
                margin: "0 0 0.75rem",
              }}
            >
              {t("setupOrStep3BodyPrefix")}
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
                {t("setupOrStep3BodyLink")}
              </a>
              {t("setupOrStep3BodyMid")}
              <span
                style={{
                  fontFamily: "var(--font-space-mono), monospace",
                  fontSize: "1.05rem",
                  color: "var(--chalk-bright)",
                }}
              >
                coarse
              </span>
              {t("setupOrStep3BodySuffix")}
            </p>

            <p
              style={{
                fontFamily: "Georgia, serif",
                fontSize: "1.05rem",
                lineHeight: 1.6,
                color: "var(--dust)",
                margin: "0 0 0.75rem",
              }}
            >
              {t("setupOrStep3Provisioning")}
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
              {t("setupOrStep3CopyWarning")}
            </p>

            <ChalkSketch annotation={t("setupOrStep3Annotation")}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <MockLabel>{t("setupOrStep3MockSettings")}</MockLabel>
                <MockButton highlight>{t("setupOrStep3MockButton")}</MockButton>
              </div>
              <div style={{ marginTop: "1rem" }}>
                <MockLabel>{t("setupOrStep3MockKeyName")}</MockLabel>
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
                <MockLabel>{t("setupOrStep3MockYourKey")}</MockLabel>
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
          <Step number={4} title={t("setupOrStep4Title")}>
            <p
              style={{
                fontFamily: "Georgia, serif",
                fontSize: "1.1rem",
                lineHeight: 1.7,
                color: "var(--chalk)",
                margin: "0 0 0.75rem",
              }}
            >
              {t("setupOrStep4BodyPrefix")}
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
                {t("setupOrStep4BodyLink")}
              </a>
              {t("setupOrStep4BodyMid1")}
              <strong style={{ color: "var(--chalk-bright)" }}>&#8942;</strong>
              {t("setupOrStep4BodyMid2")}
              <strong style={{ color: "var(--chalk-bright)" }}>
                {t("setupOrStep4BodyAtLeast")}
              </strong>
              {t("setupOrStep4BodySuffix")}
            </p>

            <ChalkSketch annotation={t("setupOrStep4Annotation")}>
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
                      {t("setupOrStep4MockEdit")}
                    </div>
                  </div>
                </div>
              </div>
              <div style={{ marginTop: "1rem" }}>
                <MockLabel>{t("setupOrStep4MockLimitLabel")}</MockLabel>
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
                  <MockButton highlight>{t("setupOrStep4MockButton")}</MockButton>
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
                  {t("setupOrStep4WhyLabel")}
                </strong>
                {t("setupOrStep4WhyMid1")}
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
                  {t("setupOrStep4WhyLink")}
                </a>
                {t("setupOrStep4WhySuffix")}
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
                  {t("setupOrStep4CostLabel")}
                </strong>
                {t("setupOrStep4CostBody")}
              </p>
            </div>
          </Step>

          {/* Step 5 */}
          <Step number={5} title={t("setupOrStep5Title")}>
            <p
              style={{
                fontFamily: "Georgia, serif",
                fontSize: "1.1rem",
                lineHeight: 1.7,
                color: "var(--chalk)",
                margin: "0 0 0.75rem",
              }}
            >
              {t("setupOrStep5Body")}
            </p>

            <ChalkSketch annotation={t("setupOrStep5Annotation")}>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "1.25rem",
                }}
              >
                <div>
                  <MockLabel>{t("setupOrStep5MockEmail")}</MockLabel>
                  <MockInput placeholder="you@university.edu" />
                </div>
                <div>
                  <MockLabel>{t("setupOrStep5MockKey")}</MockLabel>
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
                <MockButton highlight>{t("setupOrStep5MockButton")}</MockButton>
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
          {t("setupReadyCta")}
        </a>
      </section>
    </>
  );
}

/* ── Subscription tab (Claude Code / Codex / Gemini CLI) ─── */
function SubscriptionTab() {
  const { t } = useSiteLanguageContext();
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
          {t("setupSubHeading")}
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
          {t("setupSubIntro1")}
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
          {t("setupSubIntro2")}
        </p>
      </section>

      <CharcoalRule />

      <div style={{ paddingTop: "2.5rem" }}>
        {/* Step 1 */}
        <Step number={1} title={t("setupSubStep1Title")}>
          <p
            style={{
              fontFamily: "Georgia, serif",
              fontSize: "1.1rem",
              lineHeight: 1.7,
              color: "var(--chalk)",
              margin: "0 0 0.75rem",
            }}
          >
            {t("setupSubStep1Body")}
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
              price={t("setupSubStep1ClaudePrice")}
              installHref="https://docs.claude.com/en/docs/claude-code/setup"
              installLabel={t("setupSubStep1InstallLabel")}
              loginCmd="claude login"
              testCmd="claude -p 'say hi'"
            />
            <AgentCard
              name="Codex"
              price={t("setupSubStep1CodexPrice")}
              installHref="https://developers.openai.com/codex/cli"
              installLabel={t("setupSubStep1InstallLabel")}
              loginCmd="codex login"
              testCmd="codex exec 'say hi'"
            />
            <AgentCard
              name="Gemini CLI"
              price={t("setupSubStep1GeminiPrice")}
              installHref="https://github.com/google-gemini/gemini-cli#quickstart"
              installLabel={t("setupSubStep1InstallLabel")}
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
            {t("setupSubStep1Verify")}
          </p>
        </Step>

        {/* Step 2 */}
        <Step number={2} title={t("setupSubStep2Title")}>
          <p
            style={{
              fontFamily: "Georgia, serif",
              fontSize: "1.1rem",
              lineHeight: 1.7,
              color: "var(--chalk)",
              margin: "0 0 0.75rem",
            }}
          >
            {t("setupSubStep2BodyPrefix")}
            <strong style={{ color: "var(--chalk-bright)" }}>
              {t("setupSubStep2BodyTab")}
            </strong>
            {t("setupSubStep2BodySuffix")}
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
            {t("setupSubStep2KeyPrefix")}
            <code
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.95rem",
                color: "var(--chalk-bright)",
              }}
            >
              export OPENROUTER_API_KEY=sk-or-v1-...
            </code>
            {t("setupSubStep2KeyMid1")}
            <code
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.95rem",
                color: "var(--chalk-bright)",
              }}
            >
              .env
            </code>
            {t("setupSubStep2KeyMid2")}
            <code
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.95rem",
                color: "var(--chalk-bright)",
              }}
            >
              ~/.coarse/config.toml
            </code>
            {t("setupSubStep2KeySuffix")}
          </p>
        </Step>

        {/* Step 3 */}
        <Step number={3} title={t("setupSubStep3Title")}>
          <p
            style={{
              fontFamily: "Georgia, serif",
              fontSize: "1.1rem",
              lineHeight: 1.7,
              color: "var(--chalk)",
              margin: 0,
            }}
          >
            {t("setupSubStep3BodyPrefix")}
            <a
              href="/"
              style={{
                color: "var(--blue-chalk)",
                textDecoration: "underline",
                textUnderlineOffset: "2px",
              }}
            >
              {t("setupSubStep3BodyLink")}
            </a>
            {t("setupSubStep3BodyMid")}
            <strong style={{ color: "var(--chalk-bright)" }}>
              {t("setupSubStep3BodyButton")}
            </strong>
            {t("setupSubStep3BodySuffix")}
          </p>
        </Step>

        {/* Step 4 */}
        <Step number={4} title={t("setupSubStep4Title")}>
          <p
            style={{
              fontFamily: "Georgia, serif",
              fontSize: "1.1rem",
              lineHeight: 1.7,
              color: "var(--chalk)",
              margin: "0 0 0.75rem",
            }}
          >
            {t("setupSubStep4BodyPrefix")}
            <code
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.95rem",
                color: "var(--chalk-bright)",
              }}
            >
              claude -p
            </code>
            {t("setupSubStep4BodyMid1")}
            <code
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.95rem",
                color: "var(--chalk-bright)",
              }}
            >
              codex exec
            </code>
            {t("setupSubStep4BodyMid2")}
            <code
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.95rem",
                color: "var(--chalk-bright)",
              }}
            >
              gemini -p
            </code>
            {t("setupSubStep4BodyMid3")}
            <code
              style={{
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "0.95rem",
                color: "var(--chalk-bright)",
              }}
            >
              view:
            </code>
            {t("setupSubStep4BodySuffix")}
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
                {t("setupSubStep4TimeoutLabel")}
              </strong>
              {t("setupSubStep4TimeoutSuffix")}
            </p>
          </div>
        </Step>

        {/* Step 5 — Troubleshooting */}
        <Step number={5} title={t("setupSubStep5Title")}>
          <Trouble
            symptom={t("setupSubTrouble1Symptom")}
            fix={t("setupSubTrouble1Fix")}
          />
          <Trouble
            symptom={t("setupSubTrouble2Symptom")}
            fix={
              <>
                {t("setupSubTrouble2FixPrefix")}
                <code
                  style={{
                    fontFamily: "var(--font-space-mono), monospace",
                    fontSize: "0.95rem",
                    color: "var(--chalk-bright)",
                  }}
                >
                  uvx --from
                </code>
                {t("setupSubTrouble2FixSuffix")}
              </>
            }
          />
          <Trouble
            symptom={t("setupSubTrouble3Symptom")}
            fix={
              <>
                {t("setupSubTrouble3FixPrefix")}
                <code
                  style={{
                    fontFamily: "var(--font-space-mono), monospace",
                    fontSize: "0.95rem",
                    color: "var(--chalk-bright)",
                  }}
                >
                  ANTHROPIC_API_KEY
                </code>
                {t("setupSubTrouble3FixMid1")}
                <code
                  style={{
                    fontFamily: "var(--font-space-mono), monospace",
                    fontSize: "0.95rem",
                    color: "var(--chalk-bright)",
                  }}
                >
                  OPENAI_API_KEY
                </code>
                {t("setupSubTrouble3FixMid2")}
                <code
                  style={{
                    fontFamily: "var(--font-space-mono), monospace",
                    fontSize: "0.95rem",
                    color: "var(--chalk-bright)",
                  }}
                >
                  GOOGLE_API_KEY
                </code>
                {t("setupSubTrouble3FixSuffix")}
              </>
            }
          />
          <Trouble
            symptom={t("setupSubTrouble4Symptom")}
            fix={
              <>
                {t("setupSubTrouble4FixPrefix")}
                <code
                  style={{
                    fontFamily: "var(--font-space-mono), monospace",
                    fontSize: "0.95rem",
                    color: "var(--chalk-bright)",
                  }}
                >
                  --effort max
                </code>
                {t("setupSubTrouble4FixSuffix")}
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
          {t("setupReadyCta")}
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
  const { t } = useSiteLanguageContext();
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
          <span style={{ color: "var(--dust)" }}>{t("setupSubStep1CardLogin")}</span>
          {loginCmd}
        </div>
        <div>
          <span style={{ color: "var(--dust)" }}>{t("setupSubStep1CardTest")}</span>
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
  // The site-language context must sit ABOVE every consumer, so the provider
  // wraps the body here and the page content lives in SetupBody, whose
  // descendants read the context (mirrors status/[id]/page.tsx's pattern).
  return (
    <SiteLanguageProvider>
      <SetupBody />
    </SiteLanguageProvider>
  );
}

function SetupBody() {
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
