import { createClient } from "@supabase/supabase-js";
import { NextRequest, NextResponse } from "next/server";
import {
  extractReviewAccessToken,
  hasValidReviewAccessToken,
} from "@/lib/reviewAuth";
import { isReviewId } from "@/lib/reviewAccess";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  if (!isReviewId(id)) {
    return NextResponse.json({ error: "Invalid review ID" }, { status: 400 });
  }

  const token = extractReviewAccessToken(request);
  if (!hasValidReviewAccessToken(id, token)) {
    return NextResponse.json(
      { error: "Missing or invalid review access token" },
      { status: 401 },
    );
  }

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
  if (!supabaseUrl || !supabaseKey) {
    return NextResponse.json({ error: "Server not configured" }, { status: 503 });
  }

  const supabaseAdmin = createClient(supabaseUrl, supabaseKey);
  const { data, error } = await supabaseAdmin
    .from("reviews")
    .select("*")
    .eq("id", id)
    .single();

  if (error || !data) {
    return NextResponse.json({ error: "Review not found" }, { status: 404 });
  }

  return NextResponse.json(data);
}
