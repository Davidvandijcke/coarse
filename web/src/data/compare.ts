import fs from "fs";
import path from "path";
import type { QualityScores, PaperId, PaperData } from "./compare-types";

export type { QualityScores, ModelId, ComparisonId, PaperId, ModelEntry, ComparisonEntry, PaperData } from "./compare-types";
export { MODEL_LABELS, COMPARISON_LABELS } from "./compare-types";

function parseQualityScores(report: string): QualityScores {
  const overall = report.match(/Overall Score:\s*([\d.]+\/[\d.]+)/)?.[1] ?? "N/A";
  const dim = (name: string) =>
    report.match(new RegExp(`\\|\\s*${name}\\s*\\|\\s*([\\d.]+/\\d+)`))?.[1] ?? "N/A";
  return {
    overall,
    coverage: dim("coverage"),
    specificity: dim("specificity"),
    depth: dim("depth"),
    format: dim("format"),
  };
}

function readFile(filePath: string): string {
  return fs.readFileSync(filePath, "utf8");
}

function loadModelEntry(dir: string, reviewFile: string, qualityFile: string) {
  return {
    review: readFile(path.join(dir, reviewFile)),
    scores: parseQualityScores(readFile(path.join(dir, qualityFile))),
  };
}

const dataRoot = path.join(process.cwd(), "..", "data", "refine_examples");
const cosetDir = path.join(dataRoot, "coset_codes");
const targetDir = path.join(dataRoot, "targeting_interventions");

export const papers: Record<PaperId, PaperData> = {
  coset_codes: {
    title: "Coset Codes, Part I — Introduction and Geometrical Classification",
    pdfPath: "/compare/paper.pdf",
    models: {
      claude: loadModelEntry(cosetDir, "review_sonnet46_20260308_131015.md", "paper_quality_sonnet46_20260308_131015.md"),
      qwen: loadModelEntry(cosetDir, "review_qwen35plus_20260308_130637.md", "paper_quality_qwen35plus_20260308_130637.md"),
      kimi: loadModelEntry(cosetDir, "review_kimik25_20260308_153416.md", "paper_quality_kimik25_20260308_153416.md"),
    },
    comparisons: {
      refine: { content: readFile(path.join(cosetDir, "reference_review.md")), pdfPath: null },
      stanford: { content: readFile(path.join(cosetDir, "reference_review_stanford.md")), pdfPath: null },
      reviewer3: { content: null, pdfPath: "/compare/reviewer3.pdf" },
    },
  },
  targeting_interventions: {
    title: "Targeting Interventions in Networks",
    pdfPath: "/compare/targeting_paper.pdf",
    models: {
      claude: loadModelEntry(targetDir, "review_sonnet46_20260308_130643.md", "paper_quality_sonnet46_20260308_130643.md"),
      qwen: loadModelEntry(targetDir, "review_qwen35plus_20260308_134638.md", "paper_quality_qwen35plus_20260308_134638.md"),
    },
    comparisons: {
      refine: { content: readFile(path.join(targetDir, "reference_review.md")), pdfPath: null },
      stanford: { content: readFile(path.join(targetDir, "reference_review_stanford.md")), pdfPath: null },
      reviewer3: { content: null, pdfPath: "/compare/targeting_reviewer3.pdf" },
    },
  },
};
