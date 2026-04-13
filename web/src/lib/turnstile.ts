const TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify";
const TURNSTILE_VERIFY_TIMEOUT_MS = 5_000;

export function isTurnstileEnabled(): boolean {
  return !!process.env.TURNSTILE_SECRET_KEY?.trim();
}

export async function verifyTurnstileToken(
  token: string,
  remoteIp: string,
): Promise<{ ok: true } | { ok: false; error: string }> {
  const secret = process.env.TURNSTILE_SECRET_KEY?.trim();
  if (!secret) {
    return { ok: true };
  }

  const trimmed = (token ?? "").trim();
  if (!trimmed) {
    return { ok: false, error: "Missing Turnstile token" };
  }
  if (trimmed.length > 2048) {
    return { ok: false, error: "Invalid Turnstile token" };
  }

  const form = new URLSearchParams();
  form.append("secret", secret);
  form.append("response", trimmed);
  if (remoteIp && remoteIp !== "unknown") {
    form.append("remoteip", remoteIp);
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), TURNSTILE_VERIFY_TIMEOUT_MS);
  try {
    const resp = await fetch(TURNSTILE_VERIFY_URL, {
      method: "POST",
      body: form,
      signal: controller.signal,
    });
    if (!resp.ok) {
      return { ok: false, error: `Turnstile verify HTTP ${resp.status}` };
    }
    const data = (await resp.json()) as { success?: boolean; "error-codes"?: string[] };
    if (data.success === true) return { ok: true };
    return { ok: false, error: "Turnstile challenge failed" };
  } catch (err) {
    if (err instanceof Error && err.name === "AbortError") {
      return { ok: false, error: "Turnstile verify timed out" };
    }
    return { ok: false, error: "Turnstile verify request failed" };
  } finally {
    clearTimeout(timeoutId);
  }
}
