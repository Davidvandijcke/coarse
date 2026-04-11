import { createClient } from "@supabase/supabase-js";
import { NextResponse } from "next/server";
import { EMAIL_CAPACITY_REVIEW_THRESHOLD } from "@/lib/emailCapacity";

export const revalidate = 10; // ISR: revalidate every 10 seconds

const MAX_CONCURRENT_REVIEWS = 20;

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
  const since24h = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();

  const [statusResult, activeResult, dailyResult] = await Promise.all([
    supabase.from("system_status").select("accepting_reviews, banner_message").eq("id", 1).single(),
    supabase.from("reviews").select("id", { count: "exact", head: true }).in("status", ["queued", "running"]),
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
