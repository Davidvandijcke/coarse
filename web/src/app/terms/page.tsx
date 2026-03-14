import type { Metadata } from "next";
import { CharcoalRule } from "@/components/charcoal";

export const metadata: Metadata = {
  title: "\u2018coarse \u2014 Terms of Service",
  description: "Terms governing use of the coarse AI paper review service.",
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
            fontSize: "0.95rem",
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
  fontSize: "0.9375rem",
  lineHeight: 1.7,
  color: "var(--chalk)",
  margin: "0 0 0.75rem",
};

export default function TermsPage() {
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
            Terms of Service
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
            <h2 style={h2Style}>The service</h2>
            <p style={pStyle}>
              coarse is a free, open-source AI paper review tool. It uses
              multi-agent AI systems to generate referee-style feedback on
              academic papers. The service is provided as-is, without
              warranties of any kind.
            </p>
          </div>

          <div style={sectionStyle}>
            <h2 style={h2Style}>Your papers</h2>
            <p style={pStyle}>
              You retain full ownership and copyright of any papers you upload.
              Uploaded papers are processed to generate a review and then
              deleted from our storage. Generated reviews are stored for 90
              days so you can retrieve them via your review key.
            </p>
          </div>

          <div style={sectionStyle}>
            <h2 style={h2Style}>API keys and costs</h2>
            <p style={pStyle}>
              You provide your own OpenRouter API key. All LLM inference costs
              are charged directly to your OpenRouter account. You are solely
              responsible for these costs. We recommend setting a per-key
              spending limit on OpenRouter to cap your exposure.
            </p>
            <p style={pStyle}>
              Your API key is used once during processing and never stored.
            </p>
          </div>

          <div style={sectionStyle}>
            <h2 style={h2Style}>No warranty</h2>
            <p style={pStyle}>
              The service is provided &ldquo;as is&rdquo; and &ldquo;as
              available&rdquo; without any representations or warranties,
              express or implied. AI-generated reviews may contain errors,
              hallucinations, or inaccuracies. Reviews are not a substitute for
              human peer review.
            </p>
          </div>

          <div style={sectionStyle}>
            <h2 style={h2Style}>Limitation of liability</h2>
            <p style={pStyle}>
              To the fullest extent permitted by law, we are not liable for any
              direct, indirect, incidental, or consequential damages arising
              from your use of the service, including but not limited to API
              costs incurred, decisions made based on review content, or
              temporary unavailability of the service.
            </p>
          </div>

          <div style={sectionStyle}>
            <h2 style={h2Style}>Acceptable use</h2>
            <p style={pStyle}>
              You agree to use the service for legitimate academic and research
              purposes. You agree not to abuse the service by submitting
              excessive requests, attempting to extract or reverse-engineer the
              system, or using it in any way that violates applicable laws.
            </p>
          </div>

          <div style={sectionStyle}>
            <h2 style={h2Style}>Open source</h2>
            <p style={pStyle}>
              coarse is released under the MIT License. You are free to run,
              modify, and distribute the software. See the{" "}
              <a
                href="https://github.com/Davidvandijcke/coarse"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "var(--blue-chalk)", textDecoration: "underline", textUnderlineOffset: "2px" }}
              >
                GitHub repository
              </a>{" "}
              for the full source code.
            </p>
          </div>

          <div style={sectionStyle}>
            <h2 style={h2Style}>Changes to these terms</h2>
            <p style={pStyle}>
              We may update these terms from time to time. Continued use of the
              service after changes constitutes acceptance of the updated
              terms.
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
