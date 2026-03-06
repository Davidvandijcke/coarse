"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase";
import { useParams, useRouter } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Link from "next/link";
import type { Review } from "@/lib/types";

export default function ReviewPage() {
  const { id } = useParams<{ id: string }>();
  const [review, setReview] = useState<Review | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const supabase = createClient();

  useEffect(() => {
    async function load() {
      const { data } = await supabase
        .from("reviews")
        .select("*")
        .eq("id", id)
        .single();

      if (!data) {
        router.push("/dashboard");
        return;
      }
      setReview(data);
      setLoading(false);
    }

    load();

    // Realtime status updates
    const channel = supabase
      .channel(`review-${id}`)
      .on(
        "postgres_changes",
        {
          event: "UPDATE",
          schema: "public",
          table: "reviews",
          filter: `id=eq.${id}`,
        },
        (payload) => {
          setReview((prev) => (prev ? { ...prev, ...payload.new } : null));
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [id]);

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-gray-500">Loading...</p>
      </main>
    );
  }

  if (!review) return null;

  return (
    <main className="mx-auto max-w-4xl px-4 py-12">
      <div className="flex items-center justify-between">
        <Link
          href="/dashboard"
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          &larr; Dashboard
        </Link>
        {review.status === "done" && (
          <div className="flex items-center gap-3">
            <button
              onClick={async () => {
                await supabase
                  .from("reviews")
                  .update({ shareable: !review.shareable })
                  .eq("id", review.id);
                setReview({ ...review, shareable: !review.shareable });
              }}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              {review.shareable ? "Disable sharing" : "Enable sharing"}
            </button>
            {review.shareable && (
              <button
                onClick={() =>
                  navigator.clipboard.writeText(
                    `${window.location.origin}/review/${review.id}`
                  )
                }
                className="rounded border border-gray-300 px-3 py-1 text-sm hover:bg-gray-50"
              >
                Copy link
              </button>
            )}
          </div>
        )}
      </div>

      <h1 className="mt-6 text-2xl font-bold">
        {review.paper_title ?? "Review in progress..."}
      </h1>

      {review.status === "queued" && (
        <div className="mt-8 text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-gray-300 border-t-black" />
          <p className="mt-4 text-gray-500">Queued. Starting shortly...</p>
        </div>
      )}

      {review.status === "running" && (
        <div className="mt-8 text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-gray-300 border-t-black" />
          <p className="mt-4 text-gray-500">
            Reviewing your paper. This typically takes 1-3 minutes.
          </p>
        </div>
      )}

      {review.status === "failed" && (
        <div className="mt-8 rounded-lg bg-red-50 px-6 py-4">
          <p className="font-medium text-red-800">Review failed</p>
          <p className="mt-1 text-sm text-red-600">
            {review.error_message ?? "An unexpected error occurred."}
          </p>
        </div>
      )}

      {review.status === "done" && review.result_markdown && (
        <div className="mt-8">
          <div className="flex items-center gap-4 text-sm text-gray-500">
            {review.duration_seconds && (
              <span>Completed in {review.duration_seconds}s</span>
            )}
            {review.cost_usd && (
              <span>Cost: ${review.cost_usd.toFixed(2)}</span>
            )}
            {review.domain && <span>{review.domain}</span>}
          </div>

          <article className="prose prose-gray mt-6 max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {review.result_markdown}
            </ReactMarkdown>
          </article>
        </div>
      )}
    </main>
  );
}
