/**
 * Side-by-side comparison data loader.
 *
 * Score sources — each model × paper combination references specific quality
 * evaluation files in data/refine_examples/ so results are reproducible.
 *
 * Sonnet 4.6 & Kimi K2.5 reviews: generated 2026-03-15 via the coarse web app.
 * GPT-5 Mini reviews: generated 2026-03-16 via coarse CLI.
 *
 * Quality scores vs refine.ink: scored using Gemini 3.1 Pro as judge with PDF
 * multimodal input (no format dimension).
 *   Sonnet & Kimi: quality_{model}_20260315_vs_refine_gemini31pro_pdf.md
 *   GPT-5 Mini:   quality_gpt5mini_20260316_vs_refine_gemini31pro_pdf.md
 *
 * Quality scores vs Stanford/Reviewer 3: scored 2026-03-16 using Gemini 3.1 Pro
 * as judge with PDF multimodal input (no format dimension).
 *   Files: quality_{model}_20260316_vs_{ref}_gemini31pro_pdf.md
 */
import fs from "fs";
import path from "path";
import type { QualityScores, ComparisonId, PaperId, PaperData } from "./compare-types";

export type { QualityScores, ModelId, ComparisonId, PaperId, ModelEntry, ComparisonEntry, PaperData } from "./compare-types";
export { MODEL_LABELS, COMPARISON_LABELS, COMPARISON_URLS } from "./compare-types";

function parseQualityScores(report: string): QualityScores {
  // Display denominator as /5 (public-facing) even though judge uses a /6 scale internally
  const swapDenom = (s: string) => s.replace(/\/\d+(\.\d+)?$/, "/5");
  const overall = report.match(/Overall Score:\s*([\d.]+\/[\d.]+)/)?.[1] ?? "N/A";
  const dim = (name: string) =>
    report.match(new RegExp(`\\|\\s*${name}\\s*\\|\\s*([\\d.]+/\\d+)`))?.[1] ?? "N/A";
  return {
    overall: overall !== "N/A" ? swapDenom(overall) : overall,
    coverage: dim("coverage") !== "N/A" ? swapDenom(dim("coverage")) : "N/A",
    specificity: dim("specificity") !== "N/A" ? swapDenom(dim("specificity")) : "N/A",
    depth: dim("depth") !== "N/A" ? swapDenom(dim("depth")) : "N/A",
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

function loadModelScores(
  dir: string,
  refineFile: string,
  stanfordFile: string,
  reviewer3File: string,
): Record<ComparisonId, QualityScores> {
  return {
    refine: loadScoresForRef(dir, refineFile),
    stanford: loadScoresForRef(dir, stanfordFile),
    reviewer3: loadScoresForRef(dir, reviewer3File),
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
      // Review: review_sonnet46_20260315.md
      claude: {
        review: readFile(path.join(corticalDir, "review_sonnet46_20260315.md")),
        scores: loadModelScores(corticalDir,
          "quality_sonnet46_20260315_vs_refine_gemini31pro_pdf.md",
          "quality_sonnet46_20260316_vs_stanford_gemini31pro_pdf.md",
          "quality_sonnet46_20260316_vs_reviewer3_gemini31pro_pdf.md",
        ),
      },
      // Review: review_kimik25_20260315.md
      kimi: {
        review: readFile(path.join(corticalDir, "review_kimik25_20260315.md")),
        scores: loadModelScores(corticalDir,
          "quality_kimik25_20260315_vs_refine_gemini31pro_pdf.md",
          "quality_kimik25_20260316_vs_stanford_gemini31pro_pdf.md",
          "quality_kimik25_20260316_vs_reviewer3_gemini31pro_pdf.md",
        ),
      },
      // Review: review_gpt5mini_20260316.md
      gpt5mini: {
        review: readFile(path.join(corticalDir, "review_gpt5mini_20260316.md")),
        scores: loadModelScores(corticalDir,
          "quality_gpt5mini_20260316_vs_refine_gemini31pro_pdf.md",
          "quality_gpt5mini_20260316_vs_stanford_gemini31pro_pdf.md",
          "quality_gpt5mini_20260316_vs_reviewer3_gemini31pro_pdf.md",
        ),
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
      // Review: review_sonnet46_20260315.md
      claude: {
        review: readFile(path.join(cosetDir, "review_sonnet46_20260315.md")),
        scores: loadModelScores(cosetDir,
          "quality_sonnet46_20260315_vs_refine_gemini31pro_pdf.md",
          "quality_sonnet46_20260316_vs_stanford_gemini31pro_pdf.md",
          "quality_sonnet46_20260316_vs_reviewer3_gemini31pro_pdf.md",
        ),
      },
      // Review: review_kimik25_20260315.md
      kimi: {
        review: readFile(path.join(cosetDir, "review_kimik25_20260315.md")),
        scores: loadModelScores(cosetDir,
          "quality_kimik25_20260315_vs_refine_gemini31pro_pdf.md",
          "quality_kimik25_20260316_vs_stanford_gemini31pro_pdf.md",
          "quality_kimik25_20260316_vs_reviewer3_gemini31pro_pdf.md",
        ),
      },
      // Review: review_gpt5mini_20260316.md
      gpt5mini: {
        review: readFile(path.join(cosetDir, "review_gpt5mini_20260316.md")),
        scores: loadModelScores(cosetDir,
          "quality_gpt5mini_20260316_vs_refine_gemini31pro_pdf.md",
          "quality_gpt5mini_20260316_vs_stanford_gemini31pro_pdf.md",
          "quality_gpt5mini_20260316_vs_reviewer3_gemini31pro_pdf.md",
        ),
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
      // Review: review_sonnet46_20260315.md
      claude: {
        review: readFile(path.join(popgenDir, "review_sonnet46_20260315.md")),
        scores: loadModelScores(popgenDir,
          "quality_sonnet46_20260315_vs_refine_gemini31pro_pdf.md",
          "quality_sonnet46_20260316_vs_stanford_gemini31pro_pdf.md",
          "quality_sonnet46_20260316_vs_reviewer3_gemini31pro_pdf.md",
        ),
      },
      // Review: review_kimik25_20260315.md
      kimi: {
        review: readFile(path.join(popgenDir, "review_kimik25_20260315.md")),
        scores: loadModelScores(popgenDir,
          "quality_kimik25_20260315_vs_refine_gemini31pro_pdf.md",
          "quality_kimik25_20260316_vs_stanford_gemini31pro_pdf.md",
          "quality_kimik25_20260316_vs_reviewer3_gemini31pro_pdf.md",
        ),
      },
      // Review: review_gpt5mini_20260316.md
      gpt5mini: {
        review: readFile(path.join(popgenDir, "review_gpt5mini_20260316.md")),
        scores: loadModelScores(popgenDir,
          "quality_gpt5mini_20260316_vs_refine_gemini31pro_pdf.md",
          "quality_gpt5mini_20260316_vs_stanford_gemini31pro_pdf.md",
          "quality_gpt5mini_20260316_vs_reviewer3_gemini31pro_pdf.md",
        ),
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
      // Review: review_sonnet46_20260315.md
      claude: {
        review: readFile(path.join(targetDir, "review_sonnet46_20260315.md")),
        scores: loadModelScores(targetDir,
          "quality_sonnet46_20260315_vs_refine_gemini31pro_pdf.md",
          "quality_sonnet46_20260316_vs_stanford_gemini31pro_pdf.md",
          "quality_sonnet46_20260316_vs_reviewer3_gemini31pro_pdf.md",
        ),
      },
      // Review: review_kimik25_20260315.md
      kimi: {
        review: readFile(path.join(targetDir, "review_kimik25_20260315.md")),
        scores: loadModelScores(targetDir,
          "quality_kimik25_20260315_vs_refine_gemini31pro_pdf.md",
          "quality_kimik25_20260316_vs_stanford_gemini31pro_pdf.md",
          "quality_kimik25_20260316_vs_reviewer3_gemini31pro_pdf.md",
        ),
      },
      // Review: review_gpt5mini_20260316.md
      gpt5mini: {
        review: readFile(path.join(targetDir, "review_gpt5mini_20260316.md")),
        scores: loadModelScores(targetDir,
          "quality_gpt5mini_20260316_vs_refine_gemini31pro_pdf.md",
          "quality_gpt5mini_20260316_vs_stanford_gemini31pro_pdf.md",
          "quality_gpt5mini_20260316_vs_reviewer3_gemini31pro_pdf.md",
        ),
      },
    },
    comparisons: {
      refine: { content: readFile(path.join(targetDir, "reference_review.md")), pdfPath: null },
      stanford: { content: readFile(path.join(targetDir, "reference_review_stanford.md")), pdfPath: null },
      reviewer3: { content: readFile(path.join(targetDir, "reviewer3_review.md")), pdfPath: null },
    },
  },
};
