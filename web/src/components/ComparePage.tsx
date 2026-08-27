"use client";

import React, { useState, useRef, useMemo, useCallback, type CSSProperties } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import type { PaperId, ModelId, ComparisonId, PaperData } from "@/data/compare-types";
import { MODEL_LABELS, COMPARISON_LABELS, COMPARISON_URLS } from "@/data/compare-types";
import type { Components } from "react-markdown";
import { SiteLanguageProvider, useSiteLanguageContext, type MessageKey } from "@/lib/i18n";
import {
  resolveCompareEvidence,
  scoreDenominatorSuffix,
  scoreNumeratorLabel,
} from "@/lib/compareScores";

const katexOptions = { strict: false, throwOnError: false };

class PanelErrorBoundary extends React.Component<
  { children: React.ReactNode; message: string },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode; message: string }) {
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
          {this.props.message}
        </div>
      );
    }
    return this.props.children;
  }
}

const PAPER_LABEL_KEYS: Record<PaperId, MessageKey> = {
  cortical_circuits: "comparePaperCorticalCircuits",
  coset_codes: "comparePaperCosetCodes",
  population_genetics: "comparePaperPopulationGenetics",
  targeting_interventions: "comparePaperTargetingInterventions",
};

const OVERVIEW_MODEL_ORDER = ["gpt5mini", "gpt54", "claude", "kimi"] as const;
const OVERVIEW_REFERENCE_ORDER = ["stanford", "reviewer3", "refine"] as const;
const OVERVIEW_PAPER_ORDER: PaperId[] = [
  "cortical_circuits",
  "coset_codes",
  "population_genetics",
  "targeting_interventions",
];

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

For each dimension, provide a brief reasoning string (1-2 sentences).

Also provide 2-3 strengths and 2-3 weaknesses of Review B as brief bullet strings.

Do not compute overall_score — it will be computed externally.`;

const JUDGE_USER_TEMPLATE = `Evaluate Review B below. Use the paper text as the primary source of truth and Review A for calibration (Review A is not an answer key).

## Original Paper
{paper PDF attached as multimodal input — the judge reads the actual PDF}

## Review A (for calibration)
<review_a>
{one of the two reviews — assignment alternates to mitigate positional bias}
</review_a>

## Review B (evaluate this)
<review_b>
{the other review}
</review_b>

Score Review B on: coverage, specificity, and depth (each 1.0-6.0 in half-point increments, where 5.0 = matches Review A, 5.5-6.0 = exceeds Review A).
Verify quotes against the paper text. Assess coverage and depth against the paper itself — does Review B find the paper's real issues and engage with its actual methodology and assumptions? Credit valid issues Review A missed — if Review B catches real errors Review A overlooked, that warrants a score above 5.0. Provide reasoning for each score, plus 2-3 strengths and 2-3 weaknesses.

NOTE: To mitigate positional bias, the judge runs twice with Review A and Review B swapped. Scores are inverted and averaged across both orderings.`;

/* ── Scores overview table ────────────────────────────────── */
function parseOverallScore(score: string): number | null {
  const [raw] = score.split("/");
  const parsed = Number.parseFloat(raw);
  return Number.isFinite(parsed) ? parsed : null;
}

function ScoresOverviewTable({ papers }: { papers: Record<PaperId, PaperData> }) {
  const { t } = useSiteLanguageContext();
  const [open, setOpen] = useState(false);
  const rows = OVERVIEW_PAPER_ORDER.flatMap((paperId) => {
    const paper = papers[paperId];
    return OVERVIEW_REFERENCE_ORDER.map((comparisonId) => ({
      key: `${paperId}-${comparisonId}`,
      paperId,
      paperLabel: paper.citation,
      comparisonId,
      refLabel: COMPARISON_LABELS[comparisonId],
      scores: Object.fromEntries(
        OVERVIEW_MODEL_ORDER.map((modelId) => [
          modelId,
          parseOverallScore(paper.models[modelId]?.scores[comparisonId]?.overall ?? "N/A"),
        ]),
      ) as Record<(typeof OVERVIEW_MODEL_ORDER)[number], number | null>,
    }));
  });

  const cellStyle: CSSProperties = {
    padding: "0.375rem 0.625rem",
    fontFamily: "var(--font-space-mono), monospace",
    fontSize: "1.05rem",
    textAlign: "center" as const,
    color: "var(--chalk)",
    borderBottom: "1px solid var(--tray)",
  };
  const headerStyle: CSSProperties = {
    ...cellStyle,
    fontFamily: "var(--font-chalk)",
    fontSize: "1.1rem",
    color: "var(--dust)",
    fontWeight: 400,
  };
  const paperCellStyle: CSSProperties = {
    ...cellStyle,
    fontFamily: "Georgia, serif",
    fontSize: "1.05rem",
    textAlign: "left" as const,
    color: "var(--chalk-bright)",
    whiteSpace: "nowrap" as const,
  };
  const refCellStyle: CSSProperties = {
    ...cellStyle,
    fontFamily: "var(--font-chalk)",
    fontSize: "1.05rem",
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
          fontSize: "1rem",
          color: "var(--dust)",
          padding: 0,
          textDecoration: "underline",
          textUnderlineOffset: "2px",
        }}
      >
        {open ? t("compareScoresHide") : t("compareScoresShow")}{t("compareScoresToggleSuffix")}{open ? "▴" : "▾"}
      </button>
      {open && (
        <div style={{ marginTop: "0.5rem", marginBottom: "0.25rem", overflowX: "auto" }}>
          <table style={{ borderCollapse: "collapse", width: "100%", minWidth: "520px" }}>
            <thead>
              <tr>
                <th style={{ ...headerStyle, textAlign: "left" }}>{t("compareScoresColPaper")}</th>
                <th style={{ ...headerStyle, textAlign: "left" }}>{t("compareScoresColReference")}</th>
                <th style={headerStyle}>{t("compareScoresColGpt5Mini")}</th>
                <th style={headerStyle}>{t("compareScoresColGpt54")}</th>
                <th style={headerStyle}>{t("compareScoresColSonnet")}</th>
                <th style={headerStyle}>{t("compareScoresColKimi")}</th>
              </tr>
            </thead>
            <tbody>
              {OVERVIEW_PAPER_ORDER.map((paperId) => {
                const paperRows = rows.filter((r) => r.paperId === paperId);
                return paperRows.map((row, i) => (
                  <tr key={row.key}>
                    {i === 0 && (
                      <td style={{ ...paperCellStyle, borderBottom: i < paperRows.length - 1 ? "none" : cellStyle.borderBottom }} rowSpan={paperRows.length}>
                        {row.paperLabel}
                      </td>
                    )}
                    <td style={refCellStyle}>
                      <a
                        href={COMPARISON_URLS[row.comparisonId]}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ color: "inherit", textDecoration: "underline", textUnderlineOffset: "2px" }}
                      >
                        {row.refLabel}
                      </a>
                    </td>
                    {OVERVIEW_MODEL_ORDER.map((modelId) => {
                      const score = row.scores[modelId];
                      const active = score !== null;
                      return (
                        <td
                          key={modelId}
                          style={{
                            ...cellStyle,
                            color: active ? scoreColor(score) : "var(--dust)",
                            fontWeight: active && score >= 5.0 ? 600 : 400,
                            background: active && score >= 5.0 ? "rgba(212, 168, 67, 0.12)" : "transparent",
                          }}
                        >
                          {active ? score.toFixed(2) : t("compareEvidenceUnavailable")}
                        </td>
                      );
                    })}
                  </tr>
                ));
              })}
            </tbody>
          </table>
          <p
            style={{
              fontFamily: "var(--font-chalk)",
              fontSize: "1.1rem",
              color: "var(--dust)",
              marginTop: "0.375rem",
              fontStyle: "italic",
            }}
          >
            {t("compareScoresFootnote")}
          </p>
        </div>
      )}
    </div>
  );
}

function JudgePromptCollapsible() {
  const { t } = useSiteLanguageContext();
  const [open, setOpen] = useState(false);
  const preStyle: CSSProperties = {
    fontFamily: "var(--font-space-mono), monospace",
    fontSize: "1.05rem",
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
          fontSize: "1rem",
          color: "var(--dust)",
          padding: 0,
          textDecoration: "underline",
          textUnderlineOffset: "2px",
        }}
      >
        {open ? t("compareJudgeHide") : t("compareJudgeShow")}{t("compareJudgeToggleSuffix")}{open ? "▴" : "▾"}
      </button>
      {open && (
        <div style={{ marginTop: "0.5rem", marginBottom: "0.25rem" }}>
          <p style={{ fontFamily: "var(--font-chalk)", fontSize: "1rem", color: "var(--chalk)", lineHeight: 1.6, margin: "0 0 0.75rem", maxWidth: "640px" }}>
            {t("compareJudgeExplain")}
          </p>
          <p style={{ fontFamily: "var(--font-chalk)", fontSize: "1rem", color: "var(--dust)", margin: "0 0 0.25rem" }}>
            {t("compareJudgeSystemPromptLabel")}
          </p>
          <pre style={preStyle}>{JUDGE_SYSTEM_PROMPT}</pre>
          <p style={{ fontFamily: "var(--font-chalk)", fontSize: "1rem", color: "var(--dust)", margin: "0.75rem 0 0.25rem" }}>
            {t("compareJudgeUserPromptLabel")}
          </p>
          <pre style={preStyle}>{JUDGE_USER_TEMPLATE}</pre>
        </div>
      )}
    </div>
  );
}

/* ── Main component ─────────────────────────────────────────── */
export function ComparePage({ papers }: { papers: Record<PaperId, PaperData> }) {
  // The site-language context must sit ABOVE every consumer, so the provider
  // wraps the body here and the page content lives in ComparePageBody, whose
  // descendants read the context (mirrors status/[id]/page.tsx's pattern).
  return (
    <SiteLanguageProvider>
      <ComparePageBody papers={papers} />
    </SiteLanguageProvider>
  );
}

function ComparePageBody({ papers }: { papers: Record<PaperId, PaperData> }) {
  const { t } = useSiteLanguageContext();
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
  // File-backed LLM-judge rows are historical until run manifests (#273) exist.
  const evidence = resolveCompareEvidence({ scores: activeScores });

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
            {t("navSetup")}
          </a>
          <span
            style={{
              fontFamily: "var(--font-chalk)",
              fontSize: "1.05rem",
              color: "var(--chalk)",
            }}
          >
            {t("navSideBySide")}
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
            {t("navGithub")}
          </a>
        </div>
      </header>

      {/* Top controls */}
      <section style={{ padding: "0.5rem 2.5rem 0" }}>
        {/* Paper selector — chalk tabs. The paper PDF download link
            used to live here but was removed: the papers on this
            comparison page are published through journal / preprint
            servers whose terms prohibit re-hosted redistribution. */}
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
              {t(PAPER_LABEL_KEYS[pid])}
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
          {/* Scrawled grade — native scale, no denominator rewrite */}
          <div style={{ transform: "rotate(-1.5deg)", transformOrigin: "center" }}>
            <p
              style={{
                fontFamily: "var(--font-chalk)",
                fontSize: "1rem",
                color: "var(--dust)",
                margin: "0 0 0.125rem",
              }}
            >
              {MODEL_LABELS[effectiveModelId]}{t("compareVsMid")}<a href={COMPARISON_URLS[comparisonId]} target="_blank" rel="noopener noreferrer" style={{ color: "inherit", textDecoration: "underline", textUnderlineOffset: "2px" }}>{COMPARISON_LABELS[comparisonId]}</a>
            </p>
            <span
              style={{
                fontFamily: "var(--font-chalk)",
                fontSize: "3rem",
                fontWeight: 700,
                color: evidence.overall.available ? "var(--yellow-chalk)" : "var(--dust)",
                lineHeight: 1,
              }}
            >
              {evidence.overall.available
                ? scoreNumeratorLabel(activeScores.overall)
                : t("compareEvidenceUnavailable")}
              {evidence.overall.available && (
                <span style={{ fontSize: "1.25rem", fontWeight: 400, color: "var(--dust)" }}>
                  {scoreDenominatorSuffix(activeScores.overall)}
                </span>
              )}
            </span>
            {evidence.historical && (
              <p
                data-testid="compare-historical-badge"
                style={{
                  fontFamily: "var(--font-chalk)",
                  fontSize: "0.95rem",
                  color: "var(--dust)",
                  margin: "0.35rem 0 0",
                  maxWidth: "16rem",
                  lineHeight: 1.35,
                  fontStyle: "italic",
                }}
              >
                {t("compareHistoricalBadge")}
              </p>
            )}
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
                ["compareMetricCoverage", evidence.dimensions.coverage],
                ["compareMetricSpecificity", evidence.dimensions.specificity],
                ["compareMetricDepth", evidence.dimensions.depth],
              ] as const).map(([labelKey, dim]) => (
                <span key={labelKey} style={{ fontSize: "0.92rem" }}>
                  <span style={{ fontFamily: "var(--font-chalk)", color: "var(--dust)" }}>
                    {t(labelKey)}
                  </span>{" "}
                  <span style={{ fontFamily: "var(--font-chalk)", color: "var(--chalk-bright)", fontWeight: 600 }}>
                    {dim.available ? dim.text : t("compareEvidenceUnavailable")}
                  </span>
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      <ScoresOverviewTable papers={papers} />
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
        <span style={{ fontFamily: "var(--font-chalk)", fontSize: "1.05rem", color: "var(--dust)" }}>{t("compareJumpTo")}</span>
        {([
          ["Overall Feedback", "compareSectionOverallFeedback"],
          ["Detailed Comments", "compareSectionDetailedComments"],
        ] as const).map(([section, labelKey]) => (
          <button
            key={section}
            className="chalk-tab"
            style={{ fontSize: "0.9rem" }}
            onClick={() => scrollBothTo(section)}
          >
            {t(labelKey)}
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
            <span style={{ fontFamily: "var(--font-serif)", fontSize: "1rem", color: "var(--dust)", letterSpacing: "0.02em" }}>&lsquo;coarse</span>
            {(["claude", "kimi", "gpt5mini", "gpt54"] as const).map((mid) => {
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
            <PanelErrorBoundary message={t("comparePanelErrorBody")}>
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
                  title={`${t("compareVisitPrefix")}${COMPARISON_LABELS[cid]}`}
                  style={{ color: "var(--dust)", fontSize: "1.05rem", textDecoration: "none", lineHeight: 1 }}
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
              <PanelErrorBoundary message={t("comparePanelErrorBody")}>
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
                title={`${COMPARISON_LABELS[comparisonId]}${t("comparePdfReviewSuffix")}`}
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
                  fontSize: "1.05rem",
                  color: "var(--dust)",
                  marginTop: "0.5rem",
                  textDecoration: "underline",
                  textUnderlineOffset: "2px",
                }}
              >
                {t("comparePdfFallback")}
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
