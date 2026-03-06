"use client";

import { useCallback, useState } from "react";
import { createClient } from "@/lib/supabase";
import { useRouter } from "next/navigation";
import { useDropzone } from "react-dropzone";
import Link from "next/link";

export default function NewReviewPage() {
  const [file, setFile] = useState<File | null>(null);
  const [consent, setConsent] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();
  const supabase = createClient();

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted.length > 0) setFile(accepted[0]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024, // 50MB
  });

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    setSubmitting(true);
    setError("");

    const {
      data: { user },
    } = await supabase.auth.getUser();
    if (!user) {
      router.push("/login");
      return;
    }

    // Get user profile for tier info
    const { data: profile } = await supabase
      .from("profiles")
      .select("tier, data_sharing_consent")
      .eq("id", user.id)
      .single();

    const tier = profile?.tier ?? "free";

    // Free tier requires consent
    if (tier === "free" && !consent) {
      setError("Please agree to share your data for academic research to use the free tier.");
      setSubmitting(false);
      return;
    }

    // Check rate limit
    const { data: canReview } = await supabase.rpc("check_rate_limit", {
      p_user_id: user.id,
    });
    if (!canReview) {
      setError("Daily or monthly review limit reached. Add your own API key in Settings for unlimited reviews.");
      setSubmitting(false);
      return;
    }

    // Create review record
    const reviewId = crypto.randomUUID();
    const pdfPath = `${user.id}/${reviewId}.pdf`;

    const { error: uploadError } = await supabase.storage
      .from("papers")
      .upload(pdfPath, file);

    if (uploadError) {
      setError(`Upload failed: ${uploadError.message}`);
      setSubmitting(false);
      return;
    }

    const { error: insertError } = await supabase.from("reviews").insert({
      id: reviewId,
      user_id: user.id,
      tier,
      pdf_storage_path: pdfPath,
      data_shared_for_research: tier === "free" && consent,
    });

    if (insertError) {
      // Clean up orphaned PDF
      await supabase.storage.from("papers").remove([pdfPath]);
      setError(`Failed to create review: ${insertError.message}`);
      setSubmitting(false);
      return;
    }

    // Trigger Modal worker (via API route)
    const res = await fetch("/api/trigger-review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reviewId, pdfPath }),
    });

    if (!res.ok) {
      // Mark review as failed so it doesn't stay "queued" forever
      await supabase
        .from("reviews")
        .update({ status: "failed", error_message: "Failed to start review worker" })
        .eq("id", reviewId);
      setError("Failed to start review. Please try again.");
      setSubmitting(false);
      return;
    }

    router.push(`/review/${reviewId}`);
  }

  return (
    <main className="mx-auto max-w-2xl px-4 py-12">
      <Link
        href="/dashboard"
        className="text-sm text-gray-500 hover:text-gray-700"
      >
        &larr; Dashboard
      </Link>
      <h1 className="mt-4 text-2xl font-bold">New Review</h1>

      <form onSubmit={handleSubmit} className="mt-8 space-y-6">
        <div
          {...getRootProps()}
          className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed px-6 py-12 text-center transition-colors ${
            isDragActive
              ? "border-black bg-gray-100"
              : file
                ? "border-green-500 bg-green-50"
                : "border-gray-300 hover:border-gray-400"
          }`}
        >
          <input {...getInputProps()} />
          {file ? (
            <div>
              <p className="font-medium">{file.name}</p>
              <p className="mt-1 text-sm text-gray-500">
                {(file.size / 1024 / 1024).toFixed(1)} MB
              </p>
              <p className="mt-2 text-sm text-gray-400">
                Click or drag to replace
              </p>
            </div>
          ) : (
            <div>
              <p className="font-medium">Drop your PDF here</p>
              <p className="mt-1 text-sm text-gray-500">
                or click to browse (max 50 MB)
              </p>
            </div>
          )}
        </div>

        <label className="flex items-start gap-3">
          <input
            type="checkbox"
            checked={consent}
            onChange={(e) => setConsent(e.target.checked)}
            className="mt-1"
          />
          <span className="text-sm text-gray-600">
            I agree to share my uploaded paper and the resulting review for
            academic research on AI-assisted peer review. This helps improve
            AI review quality for the entire research community.
          </span>
        </label>

        {error && (
          <p className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={!file || submitting}
          className="w-full rounded-lg bg-black px-4 py-3 font-medium text-white hover:bg-gray-800 disabled:opacity-50"
        >
          {submitting ? "Uploading..." : "Start review"}
        </button>
      </form>
    </main>
  );
}
