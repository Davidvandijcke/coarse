"use client";

import React, { useState, useRef, useMemo, useCallback, type CSSProperties } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import type { PaperId, ModelId, ComparisonId, PaperData } from "@/data/compare-types";
import { MODEL_LABELS, COMPARISON_LABELS, COMPARISON_URLS } from "@/data/compare-types";
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
  cortical_circuits: "Cortical Circuits",
  coset_codes: "Coset Codes",
  population_genetics: "Population Genetics",
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

/* ── Judge prompt (from quality.py) ────────────────────────── */
const JUDGE_SYSTEM_PROMPT = `You are an expert academic peer review evaluator. You have access to the original paper and two reviews labeled "Review A" and "Review B". One is a human-written reference and one is AI-generated. Your task is to assess Review B's quality primarily against the paper itself, using Review A for calibration.

IMPORTANT — Bias awareness:
- Do NOT favor a review because it is longer. A concise review that identifies real errors is better than a verbose review that pads with generic observations. Evaluate substance per comment, not total word count.
- Do NOT favor a review because it uses more confident or assertive language. A hedged but correct observation is better than a confident but wrong claim.
- Do NOT favor a review because it cites more sources or uses more technical jargon. Evaluate whether the technical content is correct, not whether it sounds impressive.
- USE THE FULL SCORING RANGE. A review with fabricated quotes or incorrect mathematical claims should score 1-2, not 3-4. Reserve scores of 3-4 for reviews that are mediocre but not actively wrong. Do not cluster scores in the middle of the scale.

Score each dimension from 1.0 to 6.0 in half-point increments (1, 1.5, 2, ..., 5, 5.5, 6). Use half-points to distinguish minor issues from major ones — e.g., one truncated quote out of 19 is a 4.5, not a 4.

The scale:
- 1.0-2.0: Major deficiencies — fabricated quotes, incorrect claims, missing the paper's central issues, or largely generic feedback
- 2.5-3.5: Partial quality — some valid points but significant gaps, errors in technical analysis, or mostly surface-level observations
- 4.0-4.5: Good but below reference — identifies real issues with some depth but misses important points or has minor inaccuracies
- 5.0: Matches the reference review in quality
- 5.5: Exceeds the reference — catches valid issues the reference missed, or provides deeper analysis on shared issues
- 6.0: Substantially exceeds the reference — identifies important errors or insights the reference missed entirely, with stronger evidence and reasoning

Award 5+ scores when Review B demonstrably surpasses Review A. This requires concrete evidence (e.g., found a real error the reference overlooked, provided a re-derivation where the reference only noted concern, or identified a cross-section inconsistency the reference missed).

Dimensions:
1. **coverage**: Does Review B identify the paper's most important issues? Evaluate this against the paper itself — what are the real strengths, weaknesses, and gaps? Review A may help calibrate what matters, but it is not the answer key. Credit Review B fully for finding valid issues Review A missed, and do not penalize it for omitting issues that are minor or debatable.
2. **specificity**: Are comments precise, with correct verbatim quotes from the paper and actionable guidance? Verify quotes against the paper text. Score 5 if every comment has an accurate quote and clear fix, 1 if comments are vague or quotes are fabricated. Score 5+ if quotes are more precise and fixes more concrete than Review A.
3. **depth**: Is the analysis substantive and technically rigorous? Does it engage with the paper's methodology, proofs, and assumptions at a deep level, or does it stay surface-level (notation complaints, formatting issues)? A long review full of surface observations scores LOWER than a short review with deep technical engagement. Score 5+ if the analysis provides deeper technical engagement than Review A (e.g., re-derivations, concrete counterexamples, numerical verification).
4. **format**: Does Review B adhere to the standard review structure (header block, Overall Feedback with titled issues, Detailed Comments with numbered entries, each with Quote and Feedback sections)? Score 5 for perfect adherence, 1 for major structural deviation.

For each dimension, provide a brief reasoning string (1-2 sentences).

Also provide 2-3 strengths and 2-3 weaknesses of Review B as brief bullet strings.

Do not compute overall_score — it will be computed externally.`;

const JUDGE_USER_TEMPLATE = `Evaluate Review B below. Use the paper text as the primary source of truth and Review A for calibration (Review A is not an answer key).

## Original Paper
<paper>
{full paper text — ~50-200K tokens}
</paper>

## Review A (for calibration)
<review_a>
{one of the two reviews — assignment alternates to mitigate positional bias}
</review_a>

## Review B (evaluate this)
<review_b>
{the other review}
</review_b>

Score Review B on: coverage, specificity, depth, and format (each 1.0-6.0 in half-point increments, where 5.0 = matches Review A, 5.5-6.0 = exceeds Review A).
Verify quotes against the paper text. Assess coverage and depth against the paper itself — does Review B find the paper's real issues and engage with its actual methodology and assumptions? Credit valid issues Review A missed — if Review B catches real errors Review A overlooked, that warrants a score above 5.0. Provide reasoning for each score, plus 2-3 strengths and 2-3 weaknesses.

NOTE: To mitigate positional bias, the judge runs twice with Review A and Review B swapped. Scores are inverted and averaged across both orderings.`;

/* ── Scores overview table ────────────────────────────────── */
const SCORE_DATA = [
  { paper: "van Vreeswijk & Sompolinsky (1998)", qwen: 5.50, claude: 5.62, kimi: 5.25, refLabel: "Stanford" },
  { paper: "van Vreeswijk & Sompolinsky (1998)", qwen: 5.50, claude: 5.75, kimi: 5.75, refLabel: "Reviewer 3" },
  { paper: "van Vreeswijk & Sompolinsky (1998)", qwen: 3.50, claude: 5.62, kimi: 5.12, refLabel: "refine.ink" },
  { paper: "Forney (1988)", qwen: 4.88, claude: 5.12, kimi: 5.75, refLabel: "Stanford" },
  { paper: "Forney (1988)", qwen: 4.25, claude: 5.25, kimi: 5.75, refLabel: "Reviewer 3" },
  { paper: "Forney (1988)", qwen: 5.50, claude: 5.75, kimi: 5.25, refLabel: "refine.ink" },
  { paper: "Stephens & Donnelly (2000)", qwen: 5.75, claude: 5.25, kimi: 5.00, refLabel: "Stanford" },
  { paper: "Stephens & Donnelly (2000)", qwen: 5.62, claude: 5.00, kimi: 5.25, refLabel: "Reviewer 3" },
  { paper: "Stephens & Donnelly (2000)", qwen: 4.38, claude: 5.50, kimi: 4.62, refLabel: "refine.ink" },
  { paper: "Galeotti, Golub & Goyal (2020)", qwen: 5.75, claude: 5.75, kimi: 5.75, refLabel: "Stanford" },
  { paper: "Galeotti, Golub & Goyal (2020)", qwen: 5.75, claude: 5.75, kimi: 5.75, refLabel: "Reviewer 3" },
  { paper: "Galeotti, Golub & Goyal (2020)", qwen: 5.12, claude: 5.62, kimi: 5.62, refLabel: "refine.ink" },
];

const PAPERS_ORDER = [
  "van Vreeswijk & Sompolinsky (1998)",
  "Forney (1988)",
  "Stephens & Donnelly (2000)",
  "Galeotti, Golub & Goyal (2020)",
];

function ScoresOverviewTable() {
  const [open, setOpen] = useState(false);

  const cellStyle: CSSProperties = {
    padding: "0.375rem 0.625rem",
    fontFamily: "var(--font-space-mono), monospace",
    fontSize: "0.75rem",
    textAlign: "center" as const,
    color: "var(--chalk)",
    borderBottom: "1px solid var(--tray)",
  };
  const headerStyle: CSSProperties = {
    ...cellStyle,
    fontFamily: "var(--font-chalk)",
    fontSize: "0.8rem",
    color: "var(--dust)",
    fontWeight: 400,
  };
  const paperCellStyle: CSSProperties = {
    ...cellStyle,
    fontFamily: "Georgia, serif",
    fontSize: "0.75rem",
    textAlign: "left" as const,
    color: "var(--chalk-bright)",
    whiteSpace: "nowrap" as const,
  };
  const refCellStyle: CSSProperties = {
    ...cellStyle,
    fontFamily: "var(--font-chalk)",
    fontSize: "0.75rem",
    textAlign: "left" as const,
    color: "var(--dust)",
  };

  function scoreColor(score: number): string {
    if (score >= 5.5) return "var(--yellow-chalk)";
    if (score >= 5.0) return "var(--chalk-bright)";
    if (score >= 4.5) return "var(--chalk)";
    return "var(--dust)";
  }

  return (
    <div style={{ padding: "0 2.5rem", flexShrink: 0 }}>
      <button
        onClick={() => setOpen(!open)}
        style={{
          background: "none",
          border: "none",
          cursor: "pointer",
          fontFamily: "var(--font-chalk)",
          fontSize: "0.85rem",
          color: "var(--dust)",
          padding: 0,
          textDecoration: "underline",
          textUnderlineOffset: "2px",
        }}
      >
        {open ? "Hide" : "Show"} all scores across papers {open ? "▴" : "▾"}
      </button>
      {open && (
        <div style={{ marginTop: "0.5rem", marginBottom: "0.25rem", overflowX: "auto" }}>
          <table style={{ borderCollapse: "collapse", width: "100%", minWidth: "520px" }}>
            <thead>
              <tr>
                <th style={{ ...headerStyle, textAlign: "left" }}>Paper</th>
                <th style={{ ...headerStyle, textAlign: "left" }}>Reference</th>
                <th style={headerStyle}>Qwen 3.5+</th>
                <th style={headerStyle}>Sonnet 4.6</th>
                <th style={headerStyle}>Kimi K2.5</th>
              </tr>
            </thead>
            <tbody>
              {PAPERS_ORDER.map((paperName) => {
                const rows = SCORE_DATA.filter((r) => r.paper === paperName);
                return rows.map((row, i) => (
                  <tr key={`${paperName}-${row.refLabel}`}>
                    {i === 0 && (
                      <td style={{ ...paperCellStyle, borderBottom: i < rows.length - 1 ? "none" : cellStyle.borderBottom }} rowSpan={rows.length}>
                        {paperName}
                      </td>
                    )}
                    <td style={refCellStyle}>
                      <a
                        href={row.refLabel === "Stanford" ? COMPARISON_URLS.stanford : row.refLabel === "Reviewer 3" ? COMPARISON_URLS.reviewer3 : COMPARISON_URLS.refine}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ color: "inherit", textDecoration: "underline", textUnderlineOffset: "2px" }}
                      >
                        {row.refLabel}
                      </a>
                    </td>
                    {[row.qwen, row.claude, row.kimi].map((score, j) => (
                      <td key={j} style={{
                        ...cellStyle,
                        color: scoreColor(score),
                        fontWeight: score >= 5.0 ? 600 : 400,
                        background: score >= 5.0 ? "rgba(212, 168, 67, 0.12)" : "transparent",
                      }}>
                        {score.toFixed(2)}
                      </td>
                    ))}
                  </tr>
                ));
              })}
            </tbody>
          </table>
          <p
            style={{
              fontFamily: "var(--font-chalk)",
              fontSize: "0.8rem",
              color: "var(--dust)",
              marginTop: "0.375rem",
              fontStyle: "italic",
            }}
          >
            Evaluated by Gemini 3.1 Pro. 5.0 = matches reference quality. 5.5+ = exceeds it.
          </p>
        </div>
      )}
    </div>
  );
}

function JudgePromptCollapsible() {
  const [open, setOpen] = useState(false);
  const preStyle: CSSProperties = {
    fontFamily: "var(--font-space-mono), monospace",
    fontSize: "0.75rem",
    lineHeight: 1.5,
    color: "var(--chalk)",
    background: "var(--board)",
    border: "1px solid var(--tray)",
    borderRadius: "2px",
    padding: "1rem",
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
    overflowY: "auto",
    maxHeight: "300px",
    marginTop: "0.5rem",
  };

  return (
    <div style={{ padding: "0 2.5rem", flexShrink: 0 }}>
      <button
        onClick={() => setOpen(!open)}
        style={{
          background: "none",
          border: "none",
          cursor: "pointer",
          fontFamily: "var(--font-chalk)",
          fontSize: "0.85rem",
          color: "var(--dust)",
          padding: 0,
          textDecoration: "underline",
          textUnderlineOffset: "2px",
        }}
      >
        {open ? "Hide" : "Show"} judge prompt sent to Gemini 3.1 Pro {open ? "▴" : "▾"}
      </button>
      {open && (
        <div style={{ marginTop: "0.5rem", marginBottom: "0.25rem" }}>
          <p style={{ fontFamily: "var(--font-chalk)", fontSize: "0.8rem", color: "var(--chalk)", lineHeight: 1.6, margin: "0 0 0.75rem", maxWidth: "640px" }}>
            To mitigate known LLM-as-judge biases, the judge is run twice per evaluation with the two reviews swapped in presentation order, and scores are averaged across both orderings. This counteracts positional bias, where judges systematically favor whichever review appears first. The prompt also includes specific instructions to counteract verbosity bias (not rewarding length over substance), confidence bias (not rewarding assertive language over correct hedging), authority bias (not rewarding jargon or citation count over accuracy), and leniency bias (using the full 1-6 scoring range rather than clustering in the middle). Reviews are labeled neutrally as {'"'}Review A{'"'} and {'"'}Review B{'"'} rather than {'"'}reference{'"'} and {'"'}generated{'"'} to prevent provenance-based scoring.
          </p>
          <p style={{ fontFamily: "var(--font-chalk)", fontSize: "0.8rem", color: "var(--dust)", margin: "0 0 0.25rem" }}>
            System prompt
          </p>
          <pre style={preStyle}>{JUDGE_SYSTEM_PROMPT}</pre>
          <p style={{ fontFamily: "var(--font-chalk)", fontSize: "0.8rem", color: "var(--dust)", margin: "0.75rem 0 0.25rem" }}>
            User prompt (paper + reviews injected at runtime)
          </p>
          <pre style={preStyle}>{JUDGE_USER_TEMPLATE}</pre>
        </div>
      )}
    </div>
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
  const activeScores = effectiveModel.scores[comparisonId];

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
        {/* Paper selector — chalk tabs + PDF download */}
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
          <a
            href={paper.pdfPath}
            download
            style={{
              fontFamily: "var(--font-chalk)",
              fontSize: "0.85rem",
              color: "var(--dust)",
              textDecoration: "none",
              marginLeft: "auto",
              transition: "color 0.2s",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = "var(--chalk-bright)")}
            onMouseLeave={(e) => (e.currentTarget.style.color = "var(--dust)")}
          >
            ↓ paper PDF
          </a>
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
              {MODEL_LABELS[effectiveModelId]} vs <a href={COMPARISON_URLS[comparisonId]} target="_blank" rel="noopener noreferrer" style={{ color: "inherit", textDecoration: "underline", textUnderlineOffset: "2px" }}>{COMPARISON_LABELS[comparisonId]}</a>
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
              {activeScores.overall.replace(/\/[\d.]+$/, "")}
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
                ["Coverage", activeScores.coverage],
                ["Specificity", activeScores.specificity],
                ["Depth", activeScores.depth],
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

      <ScoresOverviewTable />
      <JudgePromptCollapsible />

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
              <span key={cid} style={{ display: "inline-flex", alignItems: "center", gap: "0.3rem" }}>
                <button
                  className="chalk-tab"
                  data-active={comparisonId === cid}
                  onClick={() => setComparisonId(cid)}
                >
                  {COMPARISON_LABELS[cid]}
                </button>
                <a
                  href={COMPARISON_URLS[cid]}
                  target="_blank"
                  rel="noopener noreferrer"
                  title={`Visit ${COMPARISON_LABELS[cid]}`}
                  style={{ color: "var(--dust)", fontSize: "0.7rem", textDecoration: "none", lineHeight: 1 }}
                >
                  ↗
                </a>
              </span>
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
