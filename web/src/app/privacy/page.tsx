import type { Metadata } from "next";
import { CharcoalRule } from "@/components/charcoal";

export const metadata: Metadata = {
  title: "\u2018coarse \u2014 Privacy Policy",
  description: "How coarse handles your data: papers, emails, and API keys.",
};

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
        <a
          href="/setup"
          style={{
            fontFamily: "var(--font-chalk)",
            fontSize: "1.05rem",
            color: "var(--dust)",
            textDecoration: "none",
          }}
        >
          setup
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
          }}
        >
          github &uarr;
        </a>
      </div>
    </header>
  );
}

const sectionStyle = { marginBottom: "2rem" };
const h2Style = {
  fontFamily: "var(--font-serif)",
  fontSize: "1.25rem",
  fontWeight: 400 as const,
  color: "var(--chalk-bright)",
  margin: "0 0 0.75rem",
};
const pStyle = {
  fontFamily: "Georgia, serif",
  fontSize: "1.1rem",
  lineHeight: 1.7,
  color: "var(--chalk)",
  margin: "0 0 0.75rem",
};

export default function PrivacyPage() {
  return (
    <div style={{ background: "var(--board)", minHeight: "100vh" }}>
      <Header />
      <main style={{ maxWidth: "720px", margin: "0 auto", padding: "0 2.5rem 6rem" }}>
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
            Privacy Policy
          </h1>
          <p
            style={{
              marginTop: "1rem",
              fontFamily: "var(--font-chalk)",
              fontSize: "1.05rem",
              color: "var(--dust)",
            }}
          >
            Last updated: March 13, 2026
          </p>
        </section>

        <CharcoalRule />

        <div style={{ paddingTop: "2.5rem" }}>
          <div style={sectionStyle}>
            <h2 style={h2Style}>What we collect</h2>
            <p style={pStyle}>
              When you submit a paper for review, we collect:
            </p>
            <ul style={{ ...pStyle, paddingLeft: "1.5rem" }}>
              <li>Your email address (to notify you when the review is done)</li>
              <li>Your uploaded paper (processed and then deleted)</li>
              <li>The generated review (stored for 90 days)</li>
              <li>Standard web analytics via Google Analytics (GA4)</li>
            </ul>
          </div>

          <div style={sectionStyle}>
            <h2 style={h2Style}>What we do not store</h2>
            <p style={pStyle}>
              Your OpenRouter API key is used once to run the review and then
              discarded. It is never written to a database or logged. You can
              verify this in our{" "}
              <a
                href="https://github.com/Davidvandijcke/coarse"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "var(--blue-chalk)", textDecoration: "underline", textUnderlineOffset: "2px" }}
              >
                open-source code
              </a>
              .
            </p>
          </div>

          <div style={sectionStyle}>
            <h2 style={h2Style}>How we use your data</h2>
            <p style={pStyle}>
              Your email is used only to send you a confirmation and a
              notification when your review is complete. We do not send
              marketing emails or share your email with third parties.
            </p>
            <p style={pStyle}>
              Your paper is uploaded to secure storage, processed by AI agents
              to generate a review, and then deleted. The review result is
              stored so you can retrieve it.
            </p>
          </div>

          <div style={sectionStyle}>
            <h2 style={h2Style}>Data retention</h2>
            <ul style={{ ...pStyle, paddingLeft: "1.5rem" }}>
              <li>Uploaded papers: deleted after processing</li>
              <li>Reviews: stored for 90 days, then deleted</li>
              <li>Email addresses: stored alongside the review record</li>
            </ul>
          </div>

          <div style={sectionStyle}>
            <h2 style={h2Style}>Analytics</h2>
            <p style={pStyle}>
              We use Google Analytics 4 to understand how people use the site
              (page views, traffic sources). No personally identifiable
              information is sent to Google Analytics.
            </p>
          </div>

          <div style={sectionStyle}>
            <h2 style={h2Style}>Third-party services</h2>
            <ul style={{ ...pStyle, paddingLeft: "1.5rem" }}>
              <li><strong style={{ color: "var(--chalk-bright)" }}>Supabase</strong> &mdash; database and file storage (EU/US)</li>
              <li><strong style={{ color: "var(--chalk-bright)" }}>OpenRouter</strong> &mdash; LLM API (your own key, your own account)</li>
              <li><strong style={{ color: "var(--chalk-bright)" }}>Vercel</strong> &mdash; website hosting</li>
              <li><strong style={{ color: "var(--chalk-bright)" }}>Google Analytics</strong> &mdash; web analytics</li>
            </ul>
          </div>

          <div style={sectionStyle}>
            <h2 style={h2Style}>Your rights</h2>
            <p style={pStyle}>
              You can request deletion of your review and associated data by
              emailing us. Since the project is open-source (MIT license), you
              can also run it yourself and keep all data on your own
              infrastructure.
            </p>
          </div>

          <div style={sectionStyle}>
            <h2 style={h2Style}>Contact</h2>
            <p style={pStyle}>
              David Van Dijcke &mdash;{" "}
              <a
                href="https://github.com/Davidvandijcke/coarse/issues"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "var(--blue-chalk)", textDecoration: "underline", textUnderlineOffset: "2px" }}
              >
                GitHub Issues
              </a>
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
