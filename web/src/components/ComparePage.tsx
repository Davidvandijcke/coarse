"use client";

import React, { useState, useRef, useMemo, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import type { PaperId, ModelId, ComparisonId, PaperData } from "@/data/compare-types";
import { MODEL_LABELS, COMPARISON_LABELS } from "@/data/compare-types";
import type { Components } from "react-markdown";

const katexOptions = { strict: false, throwOnError: false };

class PanelErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: "2rem", color: "var(--dust)", fontFamily: "var(--font-chalk)", fontSize: "1.1rem" }}>
          Couldn&apos;t render this one. Try another model or comparison.
        </div>
      );
    }
    return this.props.children;
  }
}

const PAPER_LABELS: Record<PaperId, string> = {
  coset_codes: "Coset Codes",
  targeting_interventions: "Targeting Interventions",
};

function textContent(node: React.ReactNode): string {
  if (typeof node === "string") return node;
  if (typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(textContent).join("");
  if (node && typeof node === "object" && "props" in node) return textContent((node as { props: { children?: React.ReactNode } }).props.children);
  return "";
}

function makeHeadingComponents(prefix: string): Partial<Components> {
  return {
    h2: ({ children, node, ...props }) => {
      const text = textContent(children);
      const label = text.replace(/\s*\(\d+\)\s*$/, "").trim();
      const id = `${prefix}-${label.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/-+$/, "")}`;
      return <h2 id={id} {...props}>{children}</h2>;
    },
    h3: ({ children, node, ...props }) => {
      const text = textContent(children);
      const id = `${prefix}-${text.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/-+$/, "")}`;
      return <h3 id={id} {...props}>{children}</h3>;
    },
  };
}

/* ── Vertical chalk divider ────────────────────────────────── */
function ChalkDivider() {
  return (
    <svg
      aria-hidden="true"
      style={{
        width: "1px",
        height: "100%",
        flexShrink: 0,
      }}
    >
      <line
        x1="0.5"
        y1="0"
        x2="0.5"
        y2="100%"
        stroke="var(--chalk)"
        strokeWidth="0.5"
        opacity="0.2"
        filter="url(#ink-rough)"
      />
    </svg>
  );
}

/* ── Main component ─────────────────────────────────────────── */
export function ComparePage({ papers }: { papers: Record<PaperId, PaperData> }) {
  const [paperId, setPaperId] = useState<PaperId>("targeting_interventions");
  const [modelId, setModelId] = useState<ModelId>("claude");
  const [comparisonId, setComparisonId] = useState<ComparisonId>("refine");
  const leftPanelRef = useRef<HTMLDivElement>(null);
  const rightPanelRef = useRef<HTMLDivElement>(null);

  const paper = papers[paperId];
  const modelEntry = paper.models[modelId];
  const comparison = paper.comparisons[comparisonId];

  const effectiveModelId = modelEntry ? modelId : "claude";
  const effectiveModel = paper.models[effectiveModelId]!;

  const leftComponents = useMemo(() => makeHeadingComponents("left"), []);
  const rightComponents = useMemo(() => makeHeadingComponents("right"), []);

  const scrollBothTo = useCallback((section: string) => {
    const slug = section.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/-+$/, "");
    const left = document.getElementById(`left-${slug}`);
    const right = document.getElementById(`right-${slug}`);
    left?.scrollIntoView({ behavior: "smooth", block: "start" });
    right?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);

  return (
    <div
      className="compare-root"
      style={{
        background: "var(--board)",
        height: "100vh",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* Header — minimal, no border */}
      <header
        style={{
          padding: "1rem 2.5rem",
          display: "flex",
          alignItems: "baseline",
          justifyContent: "space-between",
          background: "var(--board)",
          flexShrink: 0,
        }}
      >
        <a
          href="/"
          style={{
            fontFamily: "var(--font-serif)",
            fontSize: "1.25rem",
            fontWeight: 400,
            letterSpacing: "-0.01em",
            textDecoration: "none",
            color: "var(--chalk-bright)",
          }}
        >
          &lsquo;coarse
        </a>
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
          <span
            style={{
              fontFamily: "var(--font-chalk)",
              fontSize: "1.05rem",
              color: "var(--chalk)",
            }}
          >
            side-by-side
          </span>
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

      {/* Top controls */}
      <section style={{ padding: "0.5rem 2.5rem 0" }}>
        {/* Paper selector — chalk tabs */}
        <div style={{ display: "flex", gap: "1.5rem", alignItems: "baseline" }}>
          {(Object.keys(papers) as PaperId[]).map((pid) => (
            <button
              key={pid}
              className="chalk-tab"
              data-active={paperId === pid}
              onClick={() => {
                setPaperId(pid);
                if (!papers[pid].models[modelId]) setModelId("claude");
              }}
            >
              {PAPER_LABELS[pid]}
            </button>
          ))}
        </div>

        {/* Quality score + paper title */}
        <div
          style={{
            display: "flex",
            alignItems: "baseline",
            gap: "2rem",
            marginTop: "1.25rem",
            flexWrap: "wrap",
          }}
        >
          {/* Scrawled grade */}
          <div style={{ transform: "rotate(-1.5deg)", transformOrigin: "center" }}>
            <p
              style={{
                fontFamily: "var(--font-chalk)",
                fontSize: "0.85rem",
                color: "var(--dust)",
                margin: "0 0 0.125rem",
              }}
            >
              {MODEL_LABELS[effectiveModelId]}
            </p>
            <span
              style={{
                fontFamily: "var(--font-chalk)",
                fontSize: "3rem",
                fontWeight: 700,
                color: "var(--yellow-chalk)",
                lineHeight: 1,
              }}
            >
              {effectiveModel.scores.overall.replace(/\/[\d.]+$/, "")}
              <span style={{ fontSize: "1.25rem", fontWeight: 400, color: "var(--dust)" }}>/6</span>
            </span>
          </div>

          {/* Paper title + metrics */}
          <div style={{ flex: 1, minWidth: "200px" }}>
            <p
              style={{
                fontFamily: "var(--font-serif)",
                fontSize: "1.125rem",
                fontWeight: 400,
                margin: "0 0 0.5rem",
                color: "var(--chalk-bright)",
              }}
            >
              {paper.title}
            </p>
            <div style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap" }}>
              {([
                ["Coverage", effectiveModel.scores.coverage],
                ["Specificity", effectiveModel.scores.specificity],
                ["Depth", effectiveModel.scores.depth],
              ] as const).map(([label, val]) => (
                <span key={label} style={{ fontSize: "0.85rem" }}>
                  <span style={{ fontFamily: "var(--font-chalk)", color: "var(--dust)" }}>
                    {label}
                  </span>{" "}
                  <span style={{ fontFamily: "var(--font-chalk)", color: "var(--chalk-bright)", fontWeight: 600 }}>
                    {val}
                  </span>
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Section jump */}
      <div
        style={{
          display: "flex",
          gap: "1.25rem",
          padding: "0.375rem 2.5rem",
          flexShrink: 0,
          alignItems: "baseline",
        }}
      >
        <span style={{ fontFamily: "var(--font-chalk)", fontSize: "0.85rem", color: "var(--dust)" }}>Jump to</span>
        {["Overall Feedback", "Detailed Comments"].map((section) => (
          <button
            key={section}
            className="chalk-tab"
            style={{ fontSize: "0.9rem" }}
            onClick={() => scrollBothTo(section)}
          >
            {section}
          </button>
        ))}
      </div>

      {/* Split panels */}
      <div
        style={{
          display: "flex",
          flex: 1,
          minHeight: 0,
        }}
        className="compare-panels"
      >
        {/* Left panel */}
        <div
          style={{
            flex: "0 0 50%",
            display: "flex",
            flexDirection: "column",
            minHeight: 0,
          }}
          className="compare-panel-left"
        >
          {/* Model selector */}
          <div style={{ display: "flex", gap: "1.25rem", padding: "0.5rem 1.5rem", flexShrink: 0, alignItems: "baseline" }}>
            <span style={{ fontFamily: "var(--font-serif)", fontSize: "0.8rem", color: "var(--dust)", letterSpacing: "0.02em" }}>&lsquo;coarse</span>
            {(["claude", "kimi", "qwen"] as const).map((mid) => {
              const available = !!paper.models[mid];
              return (
                <button
                  key={mid}
                  className="chalk-tab"
                  data-active={effectiveModelId === mid}
                  disabled={!available}
                  onClick={() => available && setModelId(mid)}
                >
                  {MODEL_LABELS[mid]}
                </button>
              );
            })}
          </div>
          <div
            ref={leftPanelRef}
            className="review-content compare-scroll"
            style={{
              flex: 1,
              overflowY: "auto",
              padding: "0.75rem 1.5rem 2rem",
              minHeight: 0,
            }}
          >
            <PanelErrorBoundary>
              <ReactMarkdown
                remarkPlugins={[remarkGfm, remarkMath]}
                rehypePlugins={[[rehypeKatex, katexOptions]]}
                components={leftComponents}
              >
                {effectiveModel.review}
              </ReactMarkdown>
            </PanelErrorBoundary>
          </div>
        </div>

        {/* Chalk divider */}
        <ChalkDivider />

        {/* Right panel */}
        <div
          style={{
            flex: "0 0 50%",
            display: "flex",
            flexDirection: "column",
            minHeight: 0,
          }}
          className="compare-panel-right"
        >
          {/* Comparison selector */}
          <div style={{ display: "flex", gap: "1.25rem", padding: "0.5rem 1.5rem", flexShrink: 0 }}>
            {(["refine", "stanford", "reviewer3"] as const).map((cid) => (
              <button
                key={cid}
                className="chalk-tab"
                data-active={comparisonId === cid}
                onClick={() => setComparisonId(cid)}
              >
                {COMPARISON_LABELS[cid]}
              </button>
            ))}
          </div>

          {/* Content */}
          {comparison.content ? (
            <div
              ref={rightPanelRef}
              className="review-content compare-scroll"
              style={{
                flex: 1,
                overflowY: "auto",
                padding: "0.75rem 1.5rem 2rem",
                minHeight: 0,
              }}
            >
              <PanelErrorBoundary>
                <ReactMarkdown
                  remarkPlugins={[remarkGfm, remarkMath]}
                  rehypePlugins={[[rehypeKatex, katexOptions]]}
                  components={rightComponents}
                >
                  {comparison.content}
                </ReactMarkdown>
              </PanelErrorBoundary>
            </div>
          ) : comparison.pdfPath ? (
            <div style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0, padding: "0.75rem 1.5rem" }}>
              <iframe
                src={comparison.pdfPath}
                title={`${COMPARISON_LABELS[comparisonId]} review`}
                style={{
                  flex: 1,
                  width: "100%",
                  border: "1px solid var(--tray)",
                  minHeight: "400px",
                  borderRadius: "2px",
                }}
              />
              <a
                href={comparison.pdfPath}
                download
                style={{
                  fontFamily: "var(--font-chalk)",
                  fontSize: "0.9rem",
                  color: "var(--dust)",
                  marginTop: "0.5rem",
                  textDecoration: "underline",
                  textUnderlineOffset: "2px",
                }}
              >
                Download PDF if iframe doesn&apos;t render ↓
              </a>
            </div>
          ) : null}
        </div>
      </div>

      <style jsx global>{`
        .compare-scroll::-webkit-scrollbar {
          width: 4px;
        }
        .compare-scroll::-webkit-scrollbar-track {
          background: transparent;
        }
        .compare-scroll::-webkit-scrollbar-thumb {
          background: var(--dust);
          border-radius: 3px;
          opacity: 0.5;
        }
        .compare-scroll::-webkit-scrollbar-thumb:hover {
          background: var(--chalk);
        }

        @media (max-width: 768px) {
          .compare-panels {
            flex-direction: column !important;
          }
          .compare-panel-left,
          .compare-panel-right {
            flex: 1 1 auto !important;
          }
          .compare-panel-right {
            border-top: 1px solid var(--tray);
          }
          .compare-scroll {
            max-height: 60vh;
          }
        }
      `}</style>
    </div>
  );
}
