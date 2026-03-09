export type QualityScores = {
  overall: string;
  coverage: string;
  specificity: string;
  depth: string;
  format: string;
};

export type ModelId = "claude" | "kimi" | "qwen";
export type ComparisonId = "refine" | "stanford" | "reviewer3";
export type PaperId = "coset_codes" | "targeting_interventions";

export type ModelEntry = {
  review: string;
  scores: QualityScores;
};

export type ComparisonEntry = {
  content: string | null;
  pdfPath: string | null;
};

export type PaperData = {
  title: string;
  pdfPath: string;
  models: Partial<Record<ModelId, ModelEntry>>;
  comparisons: Record<ComparisonId, ComparisonEntry>;
};

export const MODEL_LABELS: Record<ModelId, string> = {
  claude: "Claude Sonnet 4.6",
  kimi: "Kimi K2.5",
  qwen: "Qwen 3.5 Plus",
};

export const COMPARISON_LABELS: Record<ComparisonId, string> = {
  refine: "refine.ink",
  stanford: "Stanford Agentic",
  reviewer3: "Reviewer 3",
};
