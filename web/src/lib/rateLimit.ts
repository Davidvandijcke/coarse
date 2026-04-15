import { SupabaseClient } from "@supabase/supabase-js";
import { NextResponse } from "next/server";

const LIMITS: Record<string, { windowSeconds: number; maxRequests: number }> = {
  presign: { windowSeconds: 60, maxRequests: 10 },
  submit: { windowSeconds: 60, maxRequests: 5 },
  cancel: { windowSeconds: 60, maxRequests: 10 },
  delete: { windowSeconds: 60, maxRequests: 10 },
  "cli-handoff": { windowSeconds: 60, maxRequests: 10 },
  "mcp-finalize": { windowSeconds: 60, maxRequests: 5 },
};

export async function checkRateLimit(
  supabase: SupabaseClient,
  ip: string,
  endpoint: string,
): Promise<NextResponse | null> {
  const limit = LIMITS[endpoint] ?? { windowSeconds: 60, maxRequests: 10 };

  const { data, error } = await supabase.rpc("check_rate_limit", {
    p_ip: ip,
    p_endpoint: endpoint,
    p_window_seconds: limit.windowSeconds,
    p_max_requests: limit.maxRequests,
  });

  // If the RPC function doesn't exist yet, fail open (allow the request)
  if (error) return null;

  if (data === false) {
    return NextResponse.json(
      { error: "Too many requests. Please wait a minute." },
      { status: 429, headers: { "Retry-After": "60" } },
    );
  }

  return null;
}
