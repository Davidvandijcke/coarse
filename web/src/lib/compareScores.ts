/**
 * Compare-page score parsing and evidence labelling.
 *
 * Quality reports use a 1-6 judge scale. Display must keep the native
 * denominator (or a documented rescaling). Never substitute /6 -> /5.
 */

export const QUALITY_JUDGE_SCALE_MAX = 6;
export const UNAVAILABLE_SCORE = "N/A";

/** Fields a future reproducible run manifest should expose to the compare UI. */
export type RunManifestSummary = {
  model?: string;
  effort?: string;
  configuration?: string;
  sampleSize?: number;
  date?: string;
  benchmarkVersion?: string;
  confidenceInterval?: string;
  /** Repo-relative or URL path to the full manifest once #273 lands. */
  manifestPath?: string;
};

export type ScoreEvidenceKind = "historical_llm_judge" | "run_manifest" | "unavailable";

export type QualityScores = {
  overall: string;
  coverage: string;
  specificity: string;
  depth: string;
};

export type ScoreFraction = {
  numerator: number;
  denominator: number;
  /** Canonical display, e.g. "5.83/6". */
  display: string;
};

const FRACTION_RE = /^([\d.]+)\s*\/\s*([\d.]+)$/;

export function parseScoreFraction(score: string): ScoreFraction | null {
  if (!score || score === UNAVAILABLE_SCORE) return null;
  const m = score.trim().match(FRACTION_RE);
  if (!m) return null;
  const numerator = Number.parseFloat(m[1]);
  const denominator = Number.parseFloat(m[2]);
  if (!Number.isFinite(numerator) || !Number.isFinite(denominator) || denominator <= 0) {
    return null;
  }
  const display = `${formatNum(numerator)}/${formatNum(denominator)}`;
  return { numerator, denominator, display };
}

function formatNum(n: number): string {
  if (Number.isInteger(n)) return String(n);
  return n.toFixed(2).replace(/\.?0+$/, "");
}

/** True when a displayed fraction's numerator exceeds its denominator. */
export function scoreExceedsDenominator(score: string): boolean {
  const frac = parseScoreFraction(score);
  if (!frac) return false;
  return frac.numerator > frac.denominator + 1e-9;
}

/**
 * Format a stored score string for UI. Keeps the native denominator.
 * Unavailable / unparsable scores return the unavailable label.
 */
export function formatScoreForDisplay(
  score: string,
  unavailableLabel: string = UNAVAILABLE_SCORE,
): { text: string; available: boolean; exceedsDenominator: boolean } {
  if (!score || score === UNAVAILABLE_SCORE) {
    return { text: unavailableLabel, available: false, exceedsDenominator: false };
  }
  const frac = parseScoreFraction(score);
  if (!frac) {
    return { text: unavailableLabel, available: false, exceedsDenominator: false };
  }
  return {
    text: frac.display,
    available: true,
    exceedsDenominator: frac.numerator > frac.denominator + 1e-9,
  };
}

/** Numerator-only big display; denominator comes from the score itself. */
export function scoreNumeratorLabel(score: string): string {
  const frac = parseScoreFraction(score);
  if (!frac) return UNAVAILABLE_SCORE;
  return formatNum(frac.numerator);
}

/** Denominator suffix including slash, e.g. "/6". */
export function scoreDenominatorSuffix(score: string, fallbackMax = QUALITY_JUDGE_SCALE_MAX): string {
  const frac = parseScoreFraction(score);
  if (!frac) return `/${fallbackMax}`;
  return `/${formatNum(frac.denominator)}`;
}

export function parseQualityScores(report: string): QualityScores {
  // Keep the native validated scale from the report (typically /6).
  const overall = report.match(/Overall Score:\s*([\d.]+\/[\d.]+)/)?.[1] ?? UNAVAILABLE_SCORE;
  const dim = (name: string) =>
    report.match(new RegExp(`\\|\\s*${name}\\s*\\|\\s*([\\d.]+/\\d+(?:\\.\\d+)?)`))?.[1] ??
    UNAVAILABLE_SCORE;
  return {
    overall,
    coverage: dim("coverage"),
    specificity: dim("specificity"),
    depth: dim("depth"),
  };
}

export const NA_SCORES: QualityScores = {
  overall: UNAVAILABLE_SCORE,
  coverage: UNAVAILABLE_SCORE,
  specificity: UNAVAILABLE_SCORE,
  depth: UNAVAILABLE_SCORE,
};

/**
 * Classify how a score cell should be labelled.
 * Until run manifests exist (#273), file-backed LLM-judge scores are historical.
 */
export function classifyScoreEvidence(
  scores: QualityScores,
  manifest?: RunManifestSummary | null,
): ScoreEvidenceKind {
  if (manifest?.manifestPath) return "run_manifest";
  const anyAvailable = [scores.overall, scores.coverage, scores.specificity, scores.depth].some(
    (s) => s && s !== UNAVAILABLE_SCORE && parseScoreFraction(s) !== null,
  );
  if (!anyAvailable) return "unavailable";
  return "historical_llm_judge";
}

export function isHistoricalIllustrative(kind: ScoreEvidenceKind): boolean {
  return kind === "historical_llm_judge";
}

/**
 * Optional manifest overlay for the compare UI. When present, pages should
 * prefer manifest metadata over ad-hoc winner copy.
 */
export function resolveCompareEvidence(opts: {
  scores: QualityScores;
  manifest?: RunManifestSummary | null;
}): {
  kind: ScoreEvidenceKind;
  historical: boolean;
  overall: ReturnType<typeof formatScoreForDisplay>;
  dimensions: {
    coverage: ReturnType<typeof formatScoreForDisplay>;
    specificity: ReturnType<typeof formatScoreForDisplay>;
    depth: ReturnType<typeof formatScoreForDisplay>;
  };
  manifest: RunManifestSummary | null;
} {
  const kind = classifyScoreEvidence(opts.scores, opts.manifest);
  return {
    kind,
    historical: isHistoricalIllustrative(kind),
    overall: formatScoreForDisplay(opts.scores.overall),
    dimensions: {
      coverage: formatScoreForDisplay(opts.scores.coverage),
      specificity: formatScoreForDisplay(opts.scores.specificity),
      depth: formatScoreForDisplay(opts.scores.depth),
    },
    manifest: opts.manifest ?? null,
  };
}
