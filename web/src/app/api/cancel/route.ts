import { createClient } from "@supabase/supabase-js";
import { NextRequest, NextResponse } from "next/server";
import { checkRateLimit } from "@/lib/rateLimit";
import {
  extractReviewAccessToken,
  hasValidReviewAccessToken,
} from "@/lib/reviewAuth";

export async function POST(request: NextRequest) {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_KEY;

  if (!supabaseUrl || !supabaseKey) {
    return NextResponse.json({ error: "Server not configured" }, { status: 503 });
  }

  const supabaseAdmin = createClient(supabaseUrl, supabaseKey);

  const ip = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ?? "unknown";
  const rateLimited = await checkRateLimit(supabaseAdmin, ip, "cancel");
  if (rateLimited) return rateLimited;

  let id = "";
  try {
    const body = await request.json();
    id = (body.id ?? "").trim();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (!id || !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id)) {
    return NextResponse.json({ error: "Invalid review ID" }, { status: 400 });
  }
  const accessToken = extractReviewAccessToken(request);
  if (!hasValidReviewAccessToken(id, accessToken)) {
    return NextResponse.json(
      { error: "Missing or invalid review access token" },
      { status: 401 },
    );
  }

  // Only allow cancelling queued or running reviews
  const { data: review, error: fetchError } = await supabaseAdmin
    .from("reviews")
    .select("id, status")
    .eq("id", id)
    .single();

  if (fetchError || !review) {
    return NextResponse.json({ error: "Review not found" }, { status: 404 });
  }

  if (review.status !== "queued" && review.status !== "running") {
    return NextResponse.json({ error: "Review cannot be cancelled" }, { status: 409 });
  }

  await supabaseAdmin.from("review_emails").delete().eq("review_id", id);
  await supabaseAdmin.from("review_secrets").delete().eq("review_id", id);
  await supabaseAdmin
    .from("reviews")
    .update({ status: "cancelled", error_message: "Review cancelled by user" })
    .eq("id", id);

  return NextResponse.json({ ok: true });
}
