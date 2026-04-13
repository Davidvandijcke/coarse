import crypto from "node:crypto";
import type { NextRequest } from "next/server";

function getReviewAccessSecret(): string {
  const secret =
    process.env.REVIEW_ACCESS_SECRET?.trim() ||
    process.env.SUPABASE_SERVICE_KEY?.trim() ||
    "";
  if (!secret) {
    throw new Error("Review access secret is not configured");
  }
  return secret;
}

export function signReviewAccessToken(reviewId: string): string {
  return crypto
    .createHmac("sha256", getReviewAccessSecret())
    .update(`review:${reviewId}`)
    .digest("base64url");
}

export function extractReviewAccessToken(request: NextRequest): string {
  const auth = request.headers.get("authorization")?.trim() ?? "";
  return auth.startsWith("Bearer ") ? auth.slice("Bearer ".length).trim() : "";
}

export function hasValidReviewAccessToken(
  reviewId: string,
  candidateToken: string,
): boolean {
  const token = candidateToken.trim();
  if (!token) return false;

  const expected = signReviewAccessToken(reviewId);
  const actualBuf = Buffer.from(token);
  const expectedBuf = Buffer.from(expected);
  if (actualBuf.length !== expectedBuf.length) return false;
  return crypto.timingSafeEqual(actualBuf, expectedBuf);
}
