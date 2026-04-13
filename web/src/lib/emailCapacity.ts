import type { SupabaseClient } from "@supabase/supabase-js";

// Gmail's free-tier cap is 500 messages/day per sender. Each review sends up
// to 2 emails (submit confirmation + completion). 240 reviews/24h ≈ 480
// emails, leaving a small buffer for retries and the monitoring cron.
export const EMAIL_CAPACITY_REVIEW_THRESHOLD = 240;

// TEMP KILL SWITCH (2026-04-13): the coarse Gmail account has been suspended,
// so every submission that went through the normal email branch was crashing
// /api/submit on `mailer.sendMail(...)` (uncaught rejection → empty 500 →
// browser saw "Failed to execute 'json' on 'Response': Unexpected end of
// JSON input"). Until the account is restored (or we migrate to a
// transactional provider), force the email-capacity gate on so the landing
// page disables the email field, the submit route accepts empty-email
// submissions, and the top banner tells users to save their review key and
// check back in about an hour. Flip this constant to `false` once email is
// healthy again.
export const EMAIL_DELIVERY_DISABLED = true;

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
