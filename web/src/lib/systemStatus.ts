import { type SupabaseClient } from "@supabase/supabase-js";
import { NextResponse } from "next/server";

export const DEFAULT_SUBMISSIONS_PAUSED_MESSAGE =
  "Submissions are temporarily paused. Please try again later or use the CLI: pip install coarse-ink";
export const DEFAULT_SUBMISSIONS_UNAVAILABLE_MESSAGE =
  "Service temporarily unavailable. Please try again in a moment.";

type SystemStatusRow = {
  accepting_reviews: boolean;
  banner_message: string | null;
};

export function getSubmissionPauseMessage(
  bannerMessage: string | null | undefined,
): string {
  const trimmed = bannerMessage?.trim();
  return trimmed ? trimmed : DEFAULT_SUBMISSIONS_PAUSED_MESSAGE;
}

export async function getSubmissionPauseState(
  supabase: SupabaseClient,
): Promise<{ accepting: boolean; message: string | null }> {
  const { data, error } = await supabase
    .from("system_status")
    .select("accepting_reviews, banner_message")
    .eq("id", 1)
    .maybeSingle<SystemStatusRow>();

  if (error || !data) {
    return {
      accepting: false,
      message: DEFAULT_SUBMISSIONS_UNAVAILABLE_MESSAGE,
    };
  }

  if (!data.accepting_reviews) {
    return {
      accepting: false,
      message: getSubmissionPauseMessage(data.banner_message),
    };
  }

  return {
    accepting: true,
    message: null,
  };
}

export async function getSubmissionPauseResponse(
  supabase: SupabaseClient,
): Promise<NextResponse | null> {
  const pauseState = await getSubmissionPauseState(supabase);
  if (pauseState.accepting) {
    return null;
  }
  return NextResponse.json(
    { error: pauseState.message ?? DEFAULT_SUBMISSIONS_PAUSED_MESSAGE },
    { status: 503 },
  );
}
