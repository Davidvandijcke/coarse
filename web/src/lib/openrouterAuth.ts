// OpenRouter OAuth PKCE helper.
// Reference: https://github.com/OpenRouterTeam/skills/blob/main/skills/openrouter-oauth/SKILL.md

const AUTH_URL = "https://openrouter.ai/auth";
const KEY_EXCHANGE_URL = "https://openrouter.ai/api/v1/auth/keys";
const VERIFIER_STORAGE_KEY = "coarse.or_verifier";
const API_KEY_STORAGE_KEY = "coarse.or_key";

function isBrowser(): boolean {
  return typeof window !== "undefined";
}

function base64UrlEncode(bytes: Uint8Array): string {
  let binary = "";
  for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

async function sha256(input: string): Promise<Uint8Array> {
  const data = new TextEncoder().encode(input);
  const hash = await window.crypto.subtle.digest("SHA-256", data);
  return new Uint8Array(hash);
}

async function generatePkcePair(): Promise<{ verifier: string; challenge: string }> {
  const randomBytes = new Uint8Array(32);
  window.crypto.getRandomValues(randomBytes);
  const verifier = base64UrlEncode(randomBytes);
  const challenge = base64UrlEncode(await sha256(verifier));
  return { verifier, challenge };
}

export async function beginLogin(callbackUrl: string): Promise<void> {
  if (!isBrowser()) return;
  if (!window.crypto || !window.crypto.subtle) {
    throw new Error("Web Crypto API not available (needs HTTPS or localhost)");
  }
  window.sessionStorage.removeItem(VERIFIER_STORAGE_KEY);
  const { verifier, challenge } = await generatePkcePair();
  window.sessionStorage.setItem(VERIFIER_STORAGE_KEY, verifier);
  const url =
    `${AUTH_URL}?callback_url=${encodeURIComponent(callbackUrl)}` +
    `&code_challenge=${encodeURIComponent(challenge)}&code_challenge_method=S256`;
  window.location.assign(url);
}

export async function completeLogin(code: string): Promise<string> {
  if (!isBrowser()) throw new Error("completeLogin called outside the browser");
  const verifier = window.sessionStorage.getItem(VERIFIER_STORAGE_KEY);
  if (!verifier) throw new Error("Missing PKCE verifier");
  const res = await fetch(KEY_EXCHANGE_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, code_verifier: verifier, code_challenge_method: "S256" }),
  });
  if (!res.ok) {
    throw new Error(`OpenRouter key exchange failed (${res.status})`);
  }
  const data = (await res.json()) as { key?: string };
  const key = (data.key ?? "").trim();
  if (!key) throw new Error("OpenRouter response missing key");
  window.sessionStorage.removeItem(VERIFIER_STORAGE_KEY);
  return key;
}

export function loadStoredKey(): string | null {
  if (!isBrowser()) return null;
  const stored = window.localStorage.getItem(API_KEY_STORAGE_KEY);
  if (stored === null) return null;
  const trimmed = stored.trim();
  return trimmed.length > 0 ? trimmed : null;
}

export function saveStoredKey(key: string): void {
  if (!isBrowser()) return;
  const trimmed = key.trim();
  if (!trimmed) return;
  window.localStorage.setItem(API_KEY_STORAGE_KEY, trimmed);
}

export function clearStoredKey(): void {
  if (!isBrowser()) return;
  window.localStorage.removeItem(API_KEY_STORAGE_KEY);
}
