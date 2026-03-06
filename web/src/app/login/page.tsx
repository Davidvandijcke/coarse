"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase";
import Link from "next/link";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const supabase = createClient();

  async function handleEmailLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    const { error } = await supabase.auth.signInWithOtp({
      email,
      options: { emailRedirectTo: `${window.location.origin}/dashboard` },
    });

    if (error) {
      setMessage(error.message);
    } else {
      setMessage("Check your email for a login link.");
    }
    setLoading(false);
  }

  async function handleOAuthLogin(provider: "google" | "github") {
    await supabase.auth.signInWithOAuth({
      provider,
      options: { redirectTo: `${window.location.origin}/dashboard` },
    });
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <Link href="/" className="text-sm text-gray-500 hover:text-gray-700">
          &larr; Back
        </Link>
        <h1 className="mt-4 text-2xl font-bold">Sign in to coarse</h1>

        <div className="mt-6 space-y-3">
          <button
            onClick={() => handleOAuthLogin("google")}
            className="flex w-full items-center justify-center gap-2 rounded-lg border border-gray-300 px-4 py-2.5 font-medium hover:bg-gray-50"
          >
            Continue with Google
          </button>
          <button
            onClick={() => handleOAuthLogin("github")}
            className="flex w-full items-center justify-center gap-2 rounded-lg border border-gray-300 px-4 py-2.5 font-medium hover:bg-gray-50"
          >
            Continue with GitHub
          </button>
        </div>

        <div className="my-6 flex items-center gap-4">
          <hr className="flex-1" />
          <span className="text-sm text-gray-500">or</span>
          <hr className="flex-1" />
        </div>

        <form onSubmit={handleEmailLogin} className="space-y-4">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@university.edu"
            required
            className="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-black focus:outline-none"
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-black px-4 py-2.5 font-medium text-white hover:bg-gray-800 disabled:opacity-50"
          >
            {loading ? "Sending..." : "Send magic link"}
          </button>
        </form>

        {message && (
          <p className="mt-4 text-center text-sm text-gray-600">{message}</p>
        )}
      </div>
    </main>
  );
}
