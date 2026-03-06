"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase";
import { useRouter } from "next/navigation";
import Link from "next/link";
import type { Review, Profile } from "@/lib/types";

const STATUS_LABELS: Record<string, string> = {
  queued: "Queued",
  running: "Reviewing...",
  done: "Done",
  failed: "Failed",
};

const STATUS_COLORS: Record<string, string> = {
  queued: "bg-yellow-100 text-yellow-800",
  running: "bg-blue-100 text-blue-800",
  done: "bg-green-100 text-green-800",
  failed: "bg-red-100 text-red-800",
};

export default function DashboardPage() {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const supabase = createClient();

  useEffect(() => {
    async function load() {
      const {
        data: { user },
      } = await supabase.auth.getUser();
      if (!user) {
        router.push("/login");
        return;
      }

      const [profileRes, reviewsRes] = await Promise.all([
        supabase.from("profiles").select("*").eq("id", user.id).single(),
        supabase
          .from("reviews")
          .select("*")
          .eq("user_id", user.id)
          .order("created_at", { ascending: false }),
      ]);

      if (profileRes.data) setProfile(profileRes.data);
      if (reviewsRes.data) setReviews(reviewsRes.data);
      setLoading(false);
    }

    load();

    // Realtime: update review status in place
    const channel = supabase
      .channel("reviews")
      .on(
        "postgres_changes",
        { event: "UPDATE", schema: "public", table: "reviews" },
        (payload) => {
          setReviews((prev) =>
            prev.map((r) =>
              r.id === payload.new.id ? { ...r, ...payload.new } : r
            )
          );
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-gray-500">Loading...</p>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-4xl px-4 py-12">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Your Reviews</h1>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-500">
            {profile?.tier === "byok" ? "BYOK" : "Free tier"} &middot;{" "}
            {reviews.length} reviews
          </span>
          <Link
            href="/review/new"
            className="rounded-lg bg-black px-4 py-2 text-sm font-medium text-white hover:bg-gray-800"
          >
            New review
          </Link>
          <Link
            href="/settings"
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            Settings
          </Link>
        </div>
      </div>

      {reviews.length === 0 ? (
        <div className="mt-16 text-center">
          <p className="text-gray-500">No reviews yet.</p>
          <Link
            href="/review/new"
            className="mt-4 inline-block text-sm font-medium text-black underline"
          >
            Upload your first paper
          </Link>
        </div>
      ) : (
        <div className="mt-8 space-y-3">
          {reviews.map((review) => (
            <Link
              key={review.id}
              href={`/review/${review.id}`}
              className="flex items-center justify-between rounded-lg border border-gray-200 bg-white px-5 py-4 hover:bg-gray-50"
            >
              <div>
                <p className="font-medium">
                  {review.paper_title ?? "Processing..."}
                </p>
                <p className="mt-0.5 text-sm text-gray-500">
                  {new Date(review.created_at).toLocaleDateString()}
                  {review.duration_seconds
                    ? ` \u00b7 ${review.duration_seconds}s`
                    : ""}
                  {review.cost_usd
                    ? ` \u00b7 $${review.cost_usd.toFixed(2)}`
                    : ""}
                </p>
              </div>
              <span
                className={`rounded-full px-3 py-1 text-xs font-medium ${STATUS_COLORS[review.status]}`}
              >
                {STATUS_LABELS[review.status]}
              </span>
            </Link>
          ))}
        </div>
      )}
    </main>
  );
}
