import type { SupabaseClient } from "@supabase/supabase-js";

// Gmail's free-tier cap is 500 messages/day per sender. Each review sends up
// to 2 emails (submit confirmation + completion). 240 reviews/24h ≈ 480
// emails, leaving a small buffer for retries and the monitoring cron.
export const EMAIL_CAPACITY_REVIEW_THRESHOLD = 240;

export async function countReviewsLast24h(
  supabase: SupabaseClient,
): Promise<number> {
  const since = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
  const { count, error } = await supabase
    .from("reviews")
    .select("id", { count: "exact", head: true })
    .gte("created_at", since);
  if (error) return 0;
  return count ?? 0;
}

export async function isEmailCapacityReached(
  supabase: SupabaseClient,
): Promise<boolean> {
  const count = await countReviewsLast24h(supabase);
  return count >= EMAIL_CAPACITY_REVIEW_THRESHOLD;
}
