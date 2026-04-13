import { createBrowserClient } from "@supabase/ssr";

export function createClient(reviewId?: string) {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    reviewId
      ? {
          // Disable singleton when header varies by route param (review id).
          // Otherwise the first header can be reused across SPA navigations.
          isSingleton: false,
          global: {
            headers: { "x-review-id": reviewId },
          },
        }
      : undefined
  );
}
