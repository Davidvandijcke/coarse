import { SupabaseClient } from "@supabase/supabase-js";
import { handoffSecretMatches, hashHandoffSecret, isValidHandoffSecret } from "@/lib/handoffAuth";

export async function requireReviewHandoffSecret(
  supabase: SupabaseClient,
  reviewId: string,
  presentedSecret: string,
): Promise<{ ok: true } | { ok: false; status: number; error: string }> {
  const trimmed = presentedSecret.trim();
  if (!isValidHandoffSecret(trimmed)) {
    return { ok: false, status: 401, error: "Missing or invalid handoff secret" };
  }

  const { data, error } = await supabase
    .from("review_handoff_secrets")
    .select("secret_hash")
    .eq("review_id", reviewId)
    .maybeSingle();
  if (error) {
    return { ok: false, status: 500, error: `Handoff secret lookup failed: ${error.message}` };
  }
  if (!data?.secret_hash || !handoffSecretMatches(trimmed, String(data.secret_hash))) {
    return { ok: false, status: 403, error: "Handoff secret did not match this review" };
  }
  return { ok: true };
}

export async function consumeReviewHandoffSecret(
  supabase: SupabaseClient,
  reviewId: string,
  presentedSecret: string,
): Promise<{ ok: true } | { ok: false; status: number; error: string }> {
  const trimmed = presentedSecret.trim();
  if (!isValidHandoffSecret(trimmed)) {
    return { ok: false, status: 401, error: "Missing or invalid handoff secret" };
  }

  const { data, error } = await supabase
    .from("review_handoff_secrets")
    .delete()
    .eq("review_id", reviewId)
    .eq("secret_hash", hashHandoffSecret(trimmed))
    .select("review_id")
    .maybeSingle();
  if (error) {
    return { ok: false, status: 500, error: `Handoff secret consume failed: ${error.message}` };
  }
  if (!data?.review_id) {
    return { ok: false, status: 403, error: "Handoff secret did not match this review" };
  }
  return { ok: true };
}
