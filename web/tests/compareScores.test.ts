import { describe, expect, it } from "vitest";

import {
  NA_SCORES,
  QUALITY_JUDGE_SCALE_MAX,
  classifyScoreEvidence,
  formatScoreForDisplay,
  isHistoricalIllustrative,
  parseQualityScores,
  parseScoreFraction,
  resolveCompareEvidence,
  scoreDenominatorSuffix,
  scoreExceedsDenominator,
  scoreNumeratorLabel,
} from "@/lib/compareScores";

const SAMPLE_REPORT = `# Quality Evaluation

## Overall Score: 5.83/6.0

## Dimensions

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| coverage | 6.0/6 | Finds real issues. |
| specificity | 5.5/6 | Precise quotes. |
| depth | 6.0/6 | Deep engagement. |
`;

describe("parseQualityScores", () => {
  it("keeps the native /6 denominator (no /5 substitution)", () => {
    const scores = parseQualityScores(SAMPLE_REPORT);
    expect(scores.overall).toBe("5.83/6.0");
    expect(scores.coverage).toBe("6.0/6");
    expect(scores.specificity).toBe("5.5/6");
    expect(scores.depth).toBe("6.0/6");
    for (const value of Object.values(scores)) {
      expect(scoreExceedsDenominator(value)).toBe(false);
      expect(value.endsWith("/5")).toBe(false);
    }
  });

  it("returns N/A dimensions when the report has no scores", () => {
    expect(parseQualityScores("# empty")).toEqual(NA_SCORES);
  });
});

describe("score scale display", () => {
  it("parses fractions and formats numerator/denominator separately", () => {
    const frac = parseScoreFraction("5.83/6.0");
    expect(frac).toEqual({ numerator: 5.83, denominator: 6, display: "5.83/6" });
    expect(scoreNumeratorLabel("5.83/6.0")).toBe("5.83");
    expect(scoreDenominatorSuffix("5.83/6.0")).toBe("/6");
    expect(scoreDenominatorSuffix("N/A")).toBe(`/${QUALITY_JUDGE_SCALE_MAX}`);
  });

  it("flags impossible displays created by denominator substitution", () => {
    expect(scoreExceedsDenominator("5.83/5")).toBe(true);
    expect(formatScoreForDisplay("5.83/5").exceedsDenominator).toBe(true);
    expect(formatScoreForDisplay("5.0/6").exceedsDenominator).toBe(false);
  });

  it("surfaces unavailable evidence without inventing a score", () => {
    const missing = formatScoreForDisplay("N/A", "Evidence unavailable");
    expect(missing).toEqual({
      text: "Evidence unavailable",
      available: false,
      exceedsDenominator: false,
    });
    expect(formatScoreForDisplay("not-a-score").available).toBe(false);
  });
});

describe("historical artifact labelling", () => {
  it("labels file-backed LLM-judge scores as historical illustrative", () => {
    const scores = parseQualityScores(SAMPLE_REPORT);
    const kind = classifyScoreEvidence(scores);
    expect(kind).toBe("historical_llm_judge");
    expect(isHistoricalIllustrative(kind)).toBe(true);
  });

  it("labels missing scores as unavailable evidence", () => {
    expect(classifyScoreEvidence(NA_SCORES)).toBe("unavailable");
    expect(isHistoricalIllustrative("unavailable")).toBe(false);
  });

  it("prefers run_manifest when a manifest path is present", () => {
    const scores = parseQualityScores(SAMPLE_REPORT);
    expect(
      classifyScoreEvidence(scores, {
        model: "openai/gpt-5",
        effort: "max",
        sampleSize: 30,
        date: "2026-08-01",
        benchmarkVersion: "spot-v1",
        confidenceInterval: "95%",
        manifestPath: "output/runs/example.json",
      }),
    ).toBe("run_manifest");
  });

  it("resolveCompareEvidence bundles display + provenance for the UI", () => {
    const resolved = resolveCompareEvidence({
      scores: parseQualityScores(SAMPLE_REPORT),
    });
    expect(resolved.historical).toBe(true);
    expect(resolved.overall.text).toBe("5.83/6");
    expect(resolved.overall.exceedsDenominator).toBe(false);
    expect(resolved.manifest).toBeNull();
  });
});
