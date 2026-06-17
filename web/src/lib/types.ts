/**
 * Structured Review JSON persisted alongside the rendered markdown
 * (`reviews.result_json`, a dump of the Python `Review` Pydantic model).
 * NULL for legacy / CLI-handoff reviews — consumers fall back to parsing
 * `result_markdown`.
 */
export interface ReviewJsonComment {
  number: number;
  title: string;
  quote: string;
  feedback: string;
  status?: string;
  severity?: "critical" | "major" | "minor";
  confidence?: "high" | "medium" | "low";
}

export interface ReviewJsonOverall {
  summary?: string;
  assessment?: string;
  issues?: { title: string; body: string }[];
  recommendation?: string;
  revision_targets?: string[];
}

export interface ReviewJson {
  title: string;
  domain: string;
  taxonomy: string;
  date: string;
  overall_feedback: ReviewJsonOverall;
  detailed_comments: ReviewJsonComment[];
}

/**
 * Language contract carried across the web, pipeline, and rendering layers
 * (mirrors `src/coarse/types.py::LanguageContext`). Additive; an unset context
 * is the English default path. An empty `review_language` means "follow the
 * detected `paper_language`". There is intentionally no `analysis_language`
 * (deferred to the contingent English-pivot design — see MULTILINGUAL_PLAN.md).
 */
export type TextDirection = "ltr" | "rtl";

export interface LanguageContext {
  site_language: string;
  review_language: string;
  paper_language: string | null;
  text_direction: TextDirection;
  paper_language_source?: "detected" | "user" | "default";
}

export interface Review {
  id: string;
  paper_filename: string;
  status: "queued" | "running" | "done" | "failed" | "cancelled";
  paper_title: string | null;
  model: string | null;
  domain: string | null;
  taxonomy: string | null;
  site_language: string | null;
  review_language: string | null;
  paper_language: string | null;
  paper_language_source: "detected" | "user" | "default" | null;
  text_direction: TextDirection | null;
  result_markdown: string | null;
  result_json: ReviewJson | null;
  paper_markdown: string | null;
  cost_usd: number | null;
  duration_seconds: number | null;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
}
