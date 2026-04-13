import type { SupabaseClient } from "@supabase/supabase-js";

// Resend Pro is 50k emails/month. Each review sends up to 2 emails (submit
// confirmation + completion), so the daily share of the monthly cap is the
// practical ceiling. 2500 reviews/24h ≈ 5000 emails — well within the daily
// share while leaving headroom for retries and the monitor cron.
export const EMAIL_CAPACITY_REVIEW_THRESHOLD = 2500;

// Kill switch retained as an operational escape hatch. Flip to true to force
// empty-email submissions and surface a banner while email is broken (e.g.
// Resend outage, API key revoked, domain verification lost). The landing
// page and /api/status both gate on this constant, so toggling it is a
// single-file deploy with no DB write. Default off — Resend is live as of
// the coarse.ink migration (2026-04-13).
export const EMAIL_DELIVERY_DISABLED = false;

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
  if (EMAIL_DELIVERY_DISABLED) return true;
  const count = await countReviewsLast24h(supabase);
  return count >= EMAIL_CAPACITY_REVIEW_THRESHOLD;
}
