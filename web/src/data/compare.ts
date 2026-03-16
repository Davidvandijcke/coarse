/**
 * Side-by-side comparison data loader.
 *
 * Score sources — each model × paper combination references specific quality
 * evaluation files in data/refine_examples/ so results are reproducible.
 *
 * Sonnet 4.6 & Kimi K2.5 reviews: generated 2026-03-15 via the coarse web app.
 * Qwen 3.5 Plus reviews: generated 2026-03-08 via coarse CLI.
 *
 * Quality scores vs refine.ink (Sonnet & Kimi): scored 2026-03-15 using
 * Gemini 3.1 Pro as judge with PDF multimodal input (no format dimension).
 * Files: quality_{model}_20260315_vs_refine_gemini31pro_pdf.md
 *
 * Quality scores vs Stanford/Reviewer 3 (all models): scored 2026-03-09
 * using Gemini 3.1 Pro as judge with extracted text (includes format dimension,
 * but format is no longer displayed).
 * Files: quality_{model}_vs_{ref}_{TS}.md
 */
import fs from "fs";
import path from "path";
import type { QualityScores, ComparisonId, PaperId, PaperData } from "./compare-types";

export type { QualityScores, ModelId, ComparisonId, PaperId, ModelEntry, ComparisonEntry, PaperData } from "./compare-types";
export { MODEL_LABELS, COMPARISON_LABELS, COMPARISON_URLS } from "./compare-types";

function parseQualityScores(report: string): QualityScores {
  const overall = report.match(/Overall Score:\s*([\d.]+\/[\d.]+)/)?.[1] ?? "N/A";
  const dim = (name: string) =>
    report.match(new RegExp(`\\|\\s*${name}\\s*\\|\\s*([\\d.]+/\\d+)`))?.[1] ?? "N/A";
  return {
    overall,
    coverage: dim("coverage"),
    specificity: dim("specificity"),
    depth: dim("depth"),
  };
}

function readFile(filePath: string): string {
  return fs.readFileSync(filePath, "utf8");
}

function tryReadFile(filePath: string): string | null {
  try {
    return fs.readFileSync(filePath, "utf8");
  } catch {
    return null;
  }
}

const NA_SCORES: QualityScores = { overall: "N/A", coverage: "N/A", specificity: "N/A", depth: "N/A" };

function loadScoresForRef(dir: string, qualityFile: string): QualityScores {
  const content = tryReadFile(path.join(dir, qualityFile));
  return content ? parseQualityScores(content) : NA_SCORES;
}

const dataRoot = path.join(process.cwd(), "..", "data", "refine_examples");
const STANFORD_REVIEWER3_TS = "20260309_114443"; // timestamp of Stanford/Reviewer3 quality eval run

function loadModelScores(
  dir: string,
  modelSlug: string,
  refineQualityFile: string,
): Record<ComparisonId, QualityScores> {
  return {
    refine: loadScoresForRef(dir, refineQualityFile),
    stanford: loadScoresForRef(dir, `quality_${modelSlug}_vs_stanford_${STANFORD_REVIEWER3_TS}.md`),
    reviewer3: loadScoresForRef(dir, `quality_${modelSlug}_vs_reviewer3_${STANFORD_REVIEWER3_TS}.md`),
  };
}

const corticalDir = path.join(dataRoot, "cortical_circuits");
const cosetDir = path.join(dataRoot, "coset_codes");
const popgenDir = path.join(dataRoot, "population_genetics");
const targetDir = path.join(dataRoot, "targeting_interventions");

export const papers: Record<PaperId, PaperData> = {
  cortical_circuits: {
    title: "Chaotic Balanced State in a Model of Cortical Circuits",
    citation: "van Vreeswijk & Sompolinsky (1998)",
    pdfPath: "/compare/cortical_paper.pdf",
    models: {
      // Review: review_sonnet46_20260315.md | Refine quality: quality_sonnet46_20260315_vs_refine_gemini31pro_pdf.md
      claude: {
        review: readFile(path.join(corticalDir, "review_sonnet46_20260315.md")),
        scores: loadModelScores(corticalDir, "sonnet46", "quality_sonnet46_20260315_vs_refine_gemini31pro_pdf.md"),
      },
      // Review: review_qwen35plus_20260308_130637.md | Refine quality: paper_quality_qwen35plus_20260308_130637.md
      qwen: {
        review: readFile(path.join(corticalDir, "review_qwen35plus_20260308_130637.md")),
        scores: loadModelScores(corticalDir, "qwen35plus", "paper_quality_qwen35plus_20260308_130637.md"),
      },
      // Review: review_kimik25_20260315.md | Refine quality: quality_kimik25_20260315_vs_refine_gemini31pro_pdf.md
      kimi: {
        review: readFile(path.join(corticalDir, "review_kimik25_20260315.md")),
        scores: loadModelScores(corticalDir, "kimik25", "quality_kimik25_20260315_vs_refine_gemini31pro_pdf.md"),
      },
    },
    comparisons: {
      refine: { content: readFile(path.join(corticalDir, "reference_review.md")), pdfPath: null },
      stanford: { content: readFile(path.join(corticalDir, "reference_review_stanford.md")), pdfPath: null },
      reviewer3: { content: readFile(path.join(corticalDir, "review_reviewer3.md")), pdfPath: null },
    },
  },
  coset_codes: {
    title: "Coset Codes, Part I — Introduction and Geometrical Classification",
    citation: "Forney (1988)",
    pdfPath: "/compare/paper.pdf",
    models: {
      // Review: review_sonnet46_20260315.md | Refine quality: quality_sonnet46_20260315_vs_refine_gemini31pro_pdf.md
      claude: {
        review: readFile(path.join(cosetDir, "review_sonnet46_20260315.md")),
        scores: loadModelScores(cosetDir, "sonnet46", "quality_sonnet46_20260315_vs_refine_gemini31pro_pdf.md"),
      },
      // Review: review_qwen35plus_20260308_130637.md | Refine quality: paper_quality_qwen35plus_20260308_130637.md
      qwen: {
        review: readFile(path.join(cosetDir, "review_qwen35plus_20260308_130637.md")),
        scores: loadModelScores(cosetDir, "qwen35plus", "paper_quality_qwen35plus_20260308_130637.md"),
      },
      // Review: review_kimik25_20260315.md | Refine quality: quality_kimik25_20260315_vs_refine_gemini31pro_pdf.md
      kimi: {
        review: readFile(path.join(cosetDir, "review_kimik25_20260315.md")),
        scores: loadModelScores(cosetDir, "kimik25", "quality_kimik25_20260315_vs_refine_gemini31pro_pdf.md"),
      },
    },
    comparisons: {
      refine: { content: readFile(path.join(cosetDir, "reference_review.md")), pdfPath: null },
      stanford: { content: readFile(path.join(cosetDir, "reference_review_stanford.md")), pdfPath: null },
      reviewer3: { content: readFile(path.join(cosetDir, "review_reviewer3.md")), pdfPath: null },
    },
  },
  population_genetics: {
    title: "Inference in Molecular Population Genetics",
    citation: "Stephens & Donnelly (2000)",
    pdfPath: "/compare/popgen_paper.pdf",
    models: {
      // Review: review_sonnet46_20260315.md | Refine quality: quality_sonnet46_20260315_vs_refine_gemini31pro_pdf.md
      claude: {
        review: readFile(path.join(popgenDir, "review_sonnet46_20260315.md")),
        scores: loadModelScores(popgenDir, "sonnet46", "quality_sonnet46_20260315_vs_refine_gemini31pro_pdf.md"),
      },
      // Review: review_qwen35plus_20260308_134638.md | Refine quality: paper_quality_qwen35plus_20260308_134638.md
      qwen: {
        review: readFile(path.join(popgenDir, "review_qwen35plus_20260308_134638.md")),
        scores: loadModelScores(popgenDir, "qwen35plus", "paper_quality_qwen35plus_20260308_134638.md"),
      },
      // Review: review_kimik25_20260315.md | Refine quality: quality_kimik25_20260315_vs_refine_gemini31pro_pdf.md
      kimi: {
        review: readFile(path.join(popgenDir, "review_kimik25_20260315.md")),
        scores: loadModelScores(popgenDir, "kimik25", "quality_kimik25_20260315_vs_refine_gemini31pro_pdf.md"),
      },
    },
    comparisons: {
      refine: { content: readFile(path.join(popgenDir, "reference_review.md")), pdfPath: null },
      stanford: { content: readFile(path.join(popgenDir, "reference_review_stanford.md")), pdfPath: null },
      reviewer3: { content: readFile(path.join(popgenDir, "review_reviewer3.md")), pdfPath: null },
    },
  },
  targeting_interventions: {
    title: "Targeting Interventions in Networks",
    citation: "Galeotti, Golub & Goyal (2020)",
    pdfPath: "/compare/targeting_paper.pdf",
    models: {
      // Review: review_sonnet46_20260315.md | Refine quality: quality_sonnet46_20260315_vs_refine_gemini31pro_pdf.md
      claude: {
        review: readFile(path.join(targetDir, "review_sonnet46_20260315.md")),
        scores: loadModelScores(targetDir, "sonnet46", "quality_sonnet46_20260315_vs_refine_gemini31pro_pdf.md"),
      },
      // Review: review_qwen35plus_20260308_134638.md | Refine quality: paper_quality_qwen35plus_20260308_134638.md
      qwen: {
        review: readFile(path.join(targetDir, "review_qwen35plus_20260308_134638.md")),
        scores: loadModelScores(targetDir, "qwen35plus", "paper_quality_qwen35plus_20260308_134638.md"),
      },
      // Review: review_kimik25_20260315.md | Refine quality: quality_kimik25_20260315_vs_refine_gemini31pro_pdf.md
      kimi: {
        review: readFile(path.join(targetDir, "review_kimik25_20260315.md")),
        scores: loadModelScores(targetDir, "kimik25", "quality_kimik25_20260315_vs_refine_gemini31pro_pdf.md"),
      },
    },
    comparisons: {
      refine: { content: readFile(path.join(targetDir, "reference_review.md")), pdfPath: null },
      stanford: { content: readFile(path.join(targetDir, "reference_review_stanford.md")), pdfPath: null },
      reviewer3: { content: readFile(path.join(targetDir, "reviewer3_review.md")), pdfPath: null },
    },
  },
};
