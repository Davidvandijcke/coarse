import { createHash, randomBytes, timingSafeEqual } from "crypto";

export const HANDOFF_SECRET_BYTES = 32;

function normalizeSecret(secret: string): string {
  return secret.trim();
}

export function mintHandoffSecret(): string {
  return randomBytes(HANDOFF_SECRET_BYTES).toString("hex");
}

export function hashHandoffSecret(secret: string): string {
  return createHash("sha256").update(normalizeSecret(secret), "utf8").digest("hex");
}

export function isValidHandoffSecret(secret: string): boolean {
  return /^[0-9a-f]{64}$/i.test(normalizeSecret(secret));
}

export function handoffSecretMatches(secret: string, expectedHash: string): boolean {
  const normalizedSecret = normalizeSecret(secret);
  const normalizedHash = expectedHash.trim().toLowerCase();
  if (!isValidHandoffSecret(normalizedSecret) || !/^[0-9a-f]{64}$/i.test(normalizedHash)) {
    return false;
  }
  const actual = Buffer.from(hashHandoffSecret(normalizedSecret), "hex");
  const expected = Buffer.from(normalizedHash, "hex");
  return actual.length === expected.length && timingSafeEqual(actual, expected);
}
