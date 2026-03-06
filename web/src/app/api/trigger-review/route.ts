import { createClient } from "@supabase/supabase-js";
import { createServerClient } from "@supabase/ssr";
import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";

// Admin client for reading profiles (bypasses RLS)
const supabaseAdmin = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_KEY!
);

export async function POST(request: NextRequest) {
  // Authenticate the caller via Supabase session cookie
  const cookieStore = await cookies();
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { cookies: { getAll: () => cookieStore.getAll() } }
  );

  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { reviewId, pdfPath } = await request.json();
  if (!reviewId || !pdfPath) {
    return NextResponse.json({ error: "Missing reviewId or pdfPath" }, { status: 400 });
  }

  // Verify the review exists AND belongs to this user
  const { data: review } = await supabaseAdmin
    .from("reviews")
    .select("user_id, tier")
    .eq("id", reviewId)
    .eq("user_id", user.id)
    .single();

  if (!review) {
    return NextResponse.json({ error: "Review not found" }, { status: 404 });
  }

  // Server-side rate limit check (defense in depth)
  const { data: canReview } = await supabaseAdmin.rpc("check_rate_limit", {
    p_user_id: user.id,
  });
  if (!canReview) {
    return NextResponse.json({ error: "Rate limit exceeded" }, { status: 429 });
  }

  // For BYOK tier, get the user's API key
  let userApiKey: string | null = null;
  if (review.tier === "byok") {
    const { data: profile } = await supabaseAdmin
      .from("profiles")
      .select("openrouter_key")
      .eq("id", review.user_id)
      .single();

    userApiKey = profile?.openrouter_key ?? null;
  }

  // Trigger Modal worker via webhook
  const modalUrl = process.env.MODAL_FUNCTION_URL;
  if (!modalUrl) {
    return NextResponse.json({ error: "Modal not configured" }, { status: 500 });
  }

  const resp = await fetch(modalUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${process.env.MODAL_WEBHOOK_SECRET ?? ""}`,
    },
    body: JSON.stringify({
      job_id: reviewId,
      pdf_storage_path: pdfPath,
      user_api_key: userApiKey,
    }),
  });

  if (!resp.ok) {
    // Mark review as failed so it doesn't stay "queued" forever
    await supabaseAdmin
      .from("reviews")
      .update({ status: "failed", error_message: "Failed to start review worker" })
      .eq("id", reviewId);
    return NextResponse.json(
      { error: "Failed to trigger review worker" },
      { status: 502 }
    );
  }

  return NextResponse.json({ status: "triggered", reviewId });
}
