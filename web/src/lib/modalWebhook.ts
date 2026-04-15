export interface ModalWebhookConfig {
  url: string;
  secret: string;
}

export function buildModalWebhookHostSuffix(appName: string, functionName: string): string {
  return `--${appName}-${functionName}.modal.run`;
}

function isLocalhost(hostname: string): boolean {
  return hostname === "localhost" || hostname === "127.0.0.1" || hostname === "::1" || hostname === "[::1]";
}

function formatAllowedHosts(suffixes: string[]): string {
  return suffixes.map((suffix) => `*${suffix}`).join(" or ");
}

export function getModalWebhookConfig(args: {
  rawUrl: string | undefined;
  rawSecret: string | undefined;
  allowedHostSuffixes: string[];
  urlEnvVarName: string;
}): ModalWebhookConfig | null {
  const { rawUrl, rawSecret, allowedHostSuffixes, urlEnvVarName } = args;
  const trimmedUrl = rawUrl?.trim();
  if (!trimmedUrl) return null;

  let parsed: URL;
  try {
    parsed = new URL(trimmedUrl);
  } catch {
    throw new Error(`${urlEnvVarName} must be a valid absolute URL`);
  }

  const secret = rawSecret?.trim() ?? "";
  if (!secret) {
    throw new Error(`MODAL_WEBHOOK_SECRET must be set when ${urlEnvVarName} is configured`);
  }

  if (parsed.protocol === "https:") {
    if (!allowedHostSuffixes.some((suffix) => parsed.hostname.endsWith(suffix))) {
      throw new Error(`${urlEnvVarName} must target ${formatAllowedHosts(allowedHostSuffixes)}`);
    }
    return { url: parsed.toString(), secret };
  }

  if (parsed.protocol === "http:" && process.env.NODE_ENV !== "production" && isLocalhost(parsed.hostname)) {
    return { url: parsed.toString(), secret };
  }

  throw new Error(`${urlEnvVarName} must use https (except http://localhost in development)`);
}
