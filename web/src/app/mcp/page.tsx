"use client";

import { CharcoalRule } from "@/components/charcoal";
import { MCP_SERVER_URL } from "@/lib/mcpHandoff";

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
        <span
          style={{
            fontFamily: "var(--font-chalk)",
            fontSize: "1.05rem",
            color: "var(--chalk)",
          }}
        >
          mcp
        </span>
        <a
          href="/compare"
          style={{
            fontFamily: "var(--font-chalk)",
            fontSize: "1.05rem",
            color: "var(--dust)",
            textDecoration: "none",
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
          }}
        >
          github ↗
        </a>
      </div>
    </header>
  );
}

type Host = {
  id: string;
  title: string;
  blurb: string;
  steps: { label: string; code?: string; note?: string }[];
};

const HOSTS: Host[] = [
  {
    id: "claude-web",
    title: "Claude.ai (Pro / Max / Team / Enterprise)",
    blurb:
      "Claude's web app (claude.ai) supports custom MCP connectors on all paid plans. One-time install; every review runs on your Claude subscription.",
    steps: [
      {
        label: "Open Claude.ai → Settings → Connectors → Add custom connector",
      },
      {
        label: "Name",
        code: "coarse",
      },
      {
        label: "Server URL",
        code: MCP_SERVER_URL,
      },
      {
        label: "Save, then refresh the Claude.ai tab so it picks up the new connector",
      },
    ],
  },
  {
    id: "chatgpt-web",
    title: "ChatGPT (Plus / Pro / Business)",
    blurb:
      "ChatGPT's Apps SDK exposes custom MCP connectors under Developer Mode. Works on Plus, Pro, and Business. Public-directory submission is a separate process — Developer Mode lets you use it immediately.",
    steps: [
      {
        label: "Settings → Connectors → toggle on Developer Mode",
      },
      {
        label: "Add custom server → paste the URL below",
        code: MCP_SERVER_URL,
      },
      {
        label: "Approve the tool list, then start a new chat",
      },
    ],
  },
  {
    id: "claude-code",
    title: "Claude Code (Max subscription)",
    blurb:
      "If you use Claude Code in your terminal, add coarse as a remote MCP server and every /mcp call goes through your Max subscription with no per-review cost beyond extraction.",
    steps: [
      {
        label: "From any project directory, run",
        code: `claude mcp add --transport http coarse ${MCP_SERVER_URL}`,
      },
      {
        label: "Verify with /mcp (you should see the 8 coarse tools listed)",
      },
    ],
  },
  {
    id: "gemini-cli",
    title: "Gemini CLI (personal Google account — AI Pro / AI Ultra)",
    blurb:
      "Gemini CLI signs in with your Google account and counts each review against your AI Pro / AI Ultra free-tier quota. No API billing.",
    steps: [
      {
        label: "Add to ~/.gemini/settings.json",
        code:
          '{\n  "mcpServers": {\n    "coarse": {\n      "httpUrl": "' +
          MCP_SERVER_URL +
          '"\n    }\n  }\n}',
      },
      {
        label: "Restart Gemini CLI and run a review",
      },
    ],
  },
];

function CodeBlock({ children }: { children: React.ReactNode }) {
  return (
    <pre
      style={{
        fontFamily: "var(--font-space-mono), monospace",
        fontSize: "0.95rem",
        color: "var(--chalk-bright)",
        background: "var(--tray)",
        padding: "0.85rem 1rem",
        margin: "0.5rem 0 0",
        borderLeft: "2px solid var(--yellow-chalk)",
        whiteSpace: "pre-wrap",
        wordBreak: "break-all",
        borderRadius: "2px",
      }}
    >
      {children}
    </pre>
  );
}

function HostCard({ host }: { host: Host }) {
  return (
    <div style={{ marginBottom: "2.75rem" }}>
      <h3
        style={{
          fontFamily: "var(--font-serif)",
          fontSize: "1.5rem",
          fontWeight: 400,
          color: "var(--chalk-bright)",
          margin: "0 0 0.5rem",
          letterSpacing: "-0.01em",
        }}
      >
        {host.title}
      </h3>
      <p
        style={{
          fontFamily: "Georgia, serif",
          fontSize: "1.05rem",
          color: "var(--chalk)",
          lineHeight: 1.6,
          margin: "0 0 1rem",
          maxWidth: "620px",
        }}
      >
        {host.blurb}
      </p>
      <ol
        style={{
          paddingLeft: "1.35rem",
          margin: 0,
          color: "var(--chalk)",
          fontFamily: "Georgia, serif",
          fontSize: "1.05rem",
          lineHeight: 1.65,
        }}
      >
        {host.steps.map((step, i) => (
          <li key={i} style={{ marginBottom: "0.85rem" }}>
            {step.label}
            {step.code ? <CodeBlock>{step.code}</CodeBlock> : null}
          </li>
        ))}
      </ol>
    </div>
  );
}

export default function McpPage() {
  return (
    <div style={{ background: "var(--board)", minHeight: "100vh" }}>
      <Header />
      <main
        style={{
          maxWidth: "720px",
          margin: "0 auto",
          padding: "3rem 2.5rem 6rem",
        }}
      >
        <p
          style={{
            fontFamily: "var(--font-chalk)",
            fontSize: "1.1rem",
            color: "var(--dust)",
            margin: "0 0 1rem",
          }}
        >
          Use your subscription
        </p>
        <h1
          style={{
            fontFamily: "var(--font-serif)",
            fontSize: "clamp(2.5rem, 6vw, 4rem)",
            fontWeight: 400,
            lineHeight: 1.05,
            letterSpacing: "-0.02em",
            margin: 0,
            color: "var(--chalk-bright)",
          }}
        >
          Bring your own chat host.
        </h1>
        <p
          style={{
            marginTop: "1.5rem",
            fontSize: "1.1rem",
            lineHeight: 1.7,
            color: "var(--chalk)",
            maxWidth: "620px",
          }}
        >
          coarse runs as an <span style={{ color: "var(--yellow-chalk)" }}>MCP server</span> — so
          Claude.ai, ChatGPT, Claude Code, and Gemini CLI can all drive a full
          review using <em>your existing subscription</em> for the expensive
          model calls. We still need an OpenRouter key for the ~$0.05 PDF
          extraction step, but everything else — overview, section-level
          commentary, crossref, critique — runs inside your chat host on
          whichever subscription you already pay for.
        </p>
        <p
          style={{
            marginTop: "1rem",
            fontSize: "1.05rem",
            lineHeight: 1.7,
            color: "var(--dust)",
            fontStyle: "italic",
            maxWidth: "620px",
          }}
        >
          One-time install per chat host. After that, uploading a paper on
          the main page and clicking &ldquo;Review with [your host]&rdquo; copies a
          ready-to-paste prompt to your clipboard and drops you into a new
          chat there. Your host does the reasoning; coarse ships the
          rendered review back to <code>/review/&lt;id&gt;</code> on this
          site.
        </p>

        <div style={{ margin: "2.5rem 0" }}>
          <CharcoalRule />
        </div>

        {HOSTS.map((host) => (
          <HostCard key={host.id} host={host} />
        ))}

        <CharcoalRule />
        <p
          style={{
            fontFamily: "var(--font-chalk)",
            fontSize: "1.05rem",
            color: "var(--dust)",
            marginTop: "1.5rem",
            lineHeight: 1.6,
          }}
        >
          Can&apos;t see the Connectors settings on Claude.ai or ChatGPT? You
          might be on a free plan. Claude.ai Pro and ChatGPT Plus are both
          required for custom MCP connectors. Or fall back to{" "}
          <a
            href="/"
            style={{
              color: "var(--blue-chalk)",
              textDecoration: "none",
            }}
          >
            the OpenRouter path
          </a>
          {" "}on the main page — no install, pay-as-you-go.
        </p>
      </main>
    </div>
  );
}
