export const MAX_CONCURRENT_REVIEWS = 20;

// Modal's review timeout is 2 hours. Count only reviews that were actually
// submitted and are still plausibly occupying worker capacity.
export const ACTIVE_REVIEW_WINDOW_MS = 2.5 * 60 * 60 * 1000;

export function getActiveReviewWindowStartIso(nowMs: number = Date.now()): string {
  return new Date(nowMs - ACTIVE_REVIEW_WINDOW_MS).toISOString();
}
