import { createClient } from "@supabase/supabase-js";
import { NextRequest, NextResponse } from "next/server";
import { checkRateLimit } from "@/lib/rateLimit";

export async function POST(request: NextRequest) {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_KEY;

  if (!supabaseUrl || !supabaseKey) {
    return NextResponse.json({ error: "Server not configured" }, { status: 503 });
  }

  const supabaseAdmin = createClient(supabaseUrl, supabaseKey);

  const ip = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ?? "unknown";
  const rateLimited = await checkRateLimit(supabaseAdmin, ip, "delete");
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

  const { data: review, error: fetchError } = await supabaseAdmin
    .from("reviews")
    .select("id")
    .eq("id", id)
    .single();

  if (fetchError || !review) {
    return NextResponse.json({ error: "Review not found" }, { status: 404 });
  }

  await supabaseAdmin.from("review_emails").delete().eq("review_id", id);
  await supabaseAdmin.from("reviews").delete().eq("id", id);

  return NextResponse.json({ ok: true });
}
