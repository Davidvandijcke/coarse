export type QualityScores = {
  overall: string;
  coverage: string;
  specificity: string;
  depth: string;
};

export type ModelId = "claude" | "kimi" | "qwen";
export type ComparisonId = "refine" | "stanford" | "reviewer3";
export type PaperId = "cortical_circuits" | "coset_codes" | "population_genetics" | "targeting_interventions";

export type ModelEntry = {
  review: string;
  scores: Record<ComparisonId, QualityScores>;
};

export type ComparisonEntry = {
  content: string | null;
  pdfPath: string | null;
};

export type PaperData = {
  title: string;
  citation: string;
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

export const COMPARISON_URLS: Record<ComparisonId, string> = {
  refine: "https://refine.ink",
  stanford: "https://paperreview.ai",
  reviewer3: "https://reviewer3.com",
};
