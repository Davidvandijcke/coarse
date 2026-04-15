import { createClient } from "@supabase/supabase-js";
import { NextResponse } from "next/server";
import { EMAIL_CAPACITY_REVIEW_THRESHOLD, EMAIL_DELIVERY_DISABLED } from "@/lib/emailCapacity";
import {
  getActiveReviewWindowStartIso,
  MAX_CONCURRENT_REVIEWS,
} from "@/lib/reviewCapacity";
import { DEFAULT_SUBMISSIONS_UNAVAILABLE_MESSAGE } from "@/lib/systemStatus";

// TEMP banner shown while EMAIL_DELIVERY_DISABLED is true. Flip the kill
// switch in `lib/emailCapacity.ts` to re-enable emails; this constant can
// stay — it is only rendered when the switch is on, and the DB
// `system_status.banner_message` still overrides it when an operator sets
// an incident-specific notice.
const EMAIL_DISABLED_BANNER =
  "Email delivery is temporarily down — save your review key when you submit and check back at /status/<your-key> in about an hour.";

export const revalidate = 10; // ISR: revalidate every 10 seconds

export async function GET() {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_KEY;

  if (!supabaseUrl || !supabaseKey) {
    console.error("[status] missing Supabase configuration", {
      hasSupabaseUrl: Boolean(supabaseUrl),
      hasSupabaseServiceKey: Boolean(supabaseKey),
      vercelEnv: process.env.VERCEL_ENV ?? null,
    });
    return NextResponse.json(
      {
        accepting: false,
        banner: DEFAULT_SUBMISSIONS_UNAVAILABLE_MESSAGE,
        activeReviews: 0,
        capacity: MAX_CONCURRENT_REVIEWS,
        emailCapacityReached: EMAIL_DELIVERY_DISABLED,
      },
      { headers: { "Cache-Control": "public, s-maxage=10" } },
    );
  }

  const supabase = createClient(supabaseUrl, supabaseKey);
  const now = Date.now();
  const since24h = new Date(now - 24 * 60 * 60 * 1000).toISOString();
  const activeSince = getActiveReviewWindowStartIso(now);

  const [statusResult, activeResult, dailyResult] = await Promise.all([
    supabase.from("system_status").select("accepting_reviews, banner_message").eq("id", 1).single(),
    supabase.rpc("count_active_submitted_reviews", { since: activeSince }),
    supabase.from("reviews").select("id", { count: "exact", head: true }).gte("created_at", since24h),
  ]);

  const activeCountError = activeResult.error;
  const statusUnavailable = Boolean(statusResult.error || !statusResult.data);
  const serviceUnavailable = statusUnavailable || Boolean(activeCountError);
  const statusRow = statusResult.data;
  if (activeCountError) {
    console.error("[status] count_active_submitted_reviews failed", activeCountError);
  }
  if (statusResult.error) {
    console.error("[status] system_status lookup failed", statusResult.error);
  }
  const accepting = serviceUnavailable
    ? false
    : (statusRow?.accepting_reviews ?? false);
  const dbBanner = statusRow?.banner_message ?? null;
  const activeReviews = activeCountError
    ? MAX_CONCURRENT_REVIEWS
    : Number(activeResult.data ?? 0);
  const dailyReviews = dailyResult.count ?? 0;
  const emailCapacityReached =
    EMAIL_DELIVERY_DISABLED || dailyReviews >= EMAIL_CAPACITY_REVIEW_THRESHOLD;

  // DB-controlled banner still wins when an operator has set an
  // incident-specific message; otherwise fall back to the hardcoded email-
  // outage notice while the kill switch is on.
  const banner =
    dbBanner
    ?? (serviceUnavailable ? DEFAULT_SUBMISSIONS_UNAVAILABLE_MESSAGE : null)
    ?? (EMAIL_DELIVERY_DISABLED ? EMAIL_DISABLED_BANNER : null);

  return NextResponse.json(
    { accepting, banner, activeReviews, capacity: MAX_CONCURRENT_REVIEWS, emailCapacityReached },
    { headers: { "Cache-Control": "public, s-maxage=10" } },
  );
}
