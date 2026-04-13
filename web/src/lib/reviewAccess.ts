const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const REVIEW_KEY_RE =
  /^([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.([A-Za-z0-9_-]{20,})$/i;

export function isReviewId(value: string): boolean {
  return UUID_RE.test(value.trim());
}

export function buildReviewKey(reviewId: string, accessToken: string): string {
  return `${reviewId}.${accessToken}`;
}

export function buildReviewPath(
  kind: "review" | "status",
  reviewId: string,
  accessToken: string,
): string {
  return `/${kind}/${reviewId}?token=${encodeURIComponent(accessToken)}`;
}

export function buildReviewUrl(
  origin: string,
  kind: "review" | "status",
  reviewId: string,
  accessToken: string,
): string {
  return `${origin}${buildReviewPath(kind, reviewId, accessToken)}`;
}

export function parseReviewLocator(
  raw: string,
): { id: string; token: string | null } | null {
  const trimmed = raw.trim();
  if (!trimmed) return null;

  const keyMatch = trimmed.match(REVIEW_KEY_RE);
  if (keyMatch) {
    return { id: keyMatch[1], token: keyMatch[2] };
  }

  if (isReviewId(trimmed)) {
    return { id: trimmed, token: null };
  }

  try {
    const url = new URL(trimmed);
    const [, kind, id] = url.pathname.split("/");
    if ((kind === "review" || kind === "status") && id && isReviewId(id)) {
      return {
        id,
        token: (url.searchParams.get("token") ?? "").trim() || null,
      };
    }
  } catch {
    return null;
  }

  return null;
}
