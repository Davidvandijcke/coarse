export interface Profile {
  id: string;
  tier: "free" | "byok";
  openrouter_key: string | null;
  data_sharing_consent: boolean;
  consent_date: string | null;
  created_at: string;
}

export interface Review {
  id: string;
  user_id: string;
  status: "queued" | "running" | "done" | "failed";
  tier: "free" | "byok";
  paper_title: string | null;
  domain: string | null;
  taxonomy: string | null;
  pdf_storage_path: string | null;
  result_markdown: string | null;
  result_json: Record<string, unknown> | null;
  cost_usd: number | null;
  duration_seconds: number | null;
  error_message: string | null;
  shareable: boolean;
  data_shared_for_research: boolean;
  created_at: string;
  completed_at: string | null;
}
