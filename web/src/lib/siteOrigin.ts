function normalizeOrigin(rawUrl: string): string | null {
  const trimmed = rawUrl.trim();
  if (!trimmed) return null;
  try {
    return new URL(trimmed).origin.replace(/\/$/, "");
  } catch {
    return null;
  }
}

function configuredSiteOrigin(): string | null {
  const explicitOrigin = normalizeOrigin(process.env.NEXT_PUBLIC_SITE_URL ?? "");
  if (explicitOrigin) return explicitOrigin;

  const vercelUrl = (process.env.NEXT_PUBLIC_VERCEL_URL ?? "").trim();
  if (!vercelUrl) return null;

  return normalizeOrigin(`https://${vercelUrl}`);
}

export function getSiteOriginForRequest(requestUrl: string): string {
  const requestOrigin = normalizeOrigin(requestUrl);
  if (!requestOrigin) {
    return configuredSiteOrigin() ?? "https://coarse.ink";
  }

  // Preview deployments often inherit production-facing defaults such as
  // NEXT_PUBLIC_SITE_URL=coarse.ink. Prefer the concrete preview request
  // origin so generated links stay on the deployment being tested.
  if (process.env.VERCEL_ENV === "preview") {
    return requestOrigin;
  }

  return configuredSiteOrigin() ?? requestOrigin;
}

export function getVisibleSiteHost(): string {
  if (typeof window !== "undefined" && window.location.host) {
    return window.location.host;
  }

  const origin = configuredSiteOrigin();
  if (!origin) return "this site";

  try {
    return new URL(origin).host;
  } catch {
    return "this site";
  }
}
