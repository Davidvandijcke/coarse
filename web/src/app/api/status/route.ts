import { createClient } from "@supabase/supabase-js";
import { NextResponse } from "next/server";
import { EMAIL_CAPACITY_REVIEW_THRESHOLD } from "@/lib/emailCapacity";

export const revalidate = 10; // ISR: revalidate every 10 seconds

const MAX_CONCURRENT_REVIEWS = 20;

// Only count rows as "active" if they were created recently. The Modal worker
// has a 2-hour timeout, so any queued/running row older than this window is
// not actually occupying a Modal slot — it's a presign row that was never
// submitted (user closed the tab before /api/submit fired) or a worker that
// crashed between `status=running` and the `except BaseException` handler.
// Without this filter, every abandoned presign leaks one phantom slot forever
// and the landing-page busy banner fires on pure DB debris. The sweeper in
// .github/workflows/sweep_stale_reviews.yml flips these to `failed` so the
// /review/<id> page stays honest, but the banner math must not wait on the
// cron. 2.5h = 2h Modal timeout + a small cushion for the tail of an
// in-flight worker that's about to transition.
const ACTIVE_REVIEW_WINDOW_MS = 2.5 * 60 * 60 * 1000;

export async function GET() {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_KEY;

  if (!supabaseUrl || !supabaseKey) {
    return NextResponse.json(
      {
        accepting: false,
        banner: "Service temporarily unavailable.",
        activeReviews: 0,
        capacity: MAX_CONCURRENT_REVIEWS,
        emailCapacityReached: false,
      },
      { headers: { "Cache-Control": "public, s-maxage=10" } },
    );
  }

  const supabase = createClient(supabaseUrl, supabaseKey);
  const now = Date.now();
  const since24h = new Date(now - 24 * 60 * 60 * 1000).toISOString();
  const activeSince = new Date(now - ACTIVE_REVIEW_WINDOW_MS).toISOString();

  const [statusResult, activeResult, dailyResult] = await Promise.all([
    supabase.from("system_status").select("accepting_reviews, banner_message").eq("id", 1).single(),
    supabase
      .from("reviews")
      .select("id", { count: "exact", head: true })
      .in("status", ["queued", "running"])
      .gte("created_at", activeSince),
    supabase.from("reviews").select("id", { count: "exact", head: true }).gte("created_at", since24h),
  ]);

  const accepting = statusResult.data?.accepting_reviews ?? true;
  const banner = statusResult.data?.banner_message ?? null;
  const activeReviews = activeResult.count ?? 0;
  const dailyReviews = dailyResult.count ?? 0;
  const emailCapacityReached = dailyReviews >= EMAIL_CAPACITY_REVIEW_THRESHOLD;

  return NextResponse.json(
    { accepting, banner, activeReviews, capacity: MAX_CONCURRENT_REVIEWS, emailCapacityReached },
    { headers: { "Cache-Control": "public, s-maxage=10" } },
  );
}
