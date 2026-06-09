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

export interface Review {
  id: string;
  paper_filename: string;
  status: "queued" | "running" | "done" | "failed" | "cancelled";
  paper_title: string | null;
  model: string | null;
  domain: string | null;
  result_markdown: string | null;
  result_json: ReviewJson | null;
  paper_markdown: string | null;
  cost_usd: number | null;
  duration_seconds: number | null;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
}
