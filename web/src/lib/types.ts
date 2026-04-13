export interface Review {
  id: string;
  paper_filename: string;
  status: "queued" | "running" | "done" | "failed" | "cancelled";
  paper_title: string | null;
  model: string | null;
  domain: string | null;
  result_markdown: string | null;
  paper_markdown: string | null;
  cost_usd: number | null;
  duration_seconds: number | null;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
}
