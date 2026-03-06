"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase";
import { useRouter } from "next/navigation";
import Link from "next/link";
import type { Profile } from "@/lib/types";

export default function SettingsPage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [apiKey, setApiKey] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
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

      const { data } = await supabase
        .from("profiles")
        .select("*")
        .eq("id", user.id)
        .single();

      if (data) setProfile(data);
    }
    load();
  }, []);

  async function handleSaveKey(e: React.FormEvent) {
    e.preventDefault();
    if (!profile) return;
    setSaving(true);
    setMessage("");

    const { error } = await supabase
      .from("profiles")
      .update({
        tier: apiKey ? "byok" : "free",
        openrouter_key: apiKey || null,
      })
      .eq("id", profile.id);

    if (error) {
      setMessage(`Error: ${error.message}`);
    } else {
      setMessage("Saved.");
      setProfile({
        ...profile,
        tier: apiKey ? "byok" : "free",
        openrouter_key: apiKey || null,
      });
    }
    setSaving(false);
  }

  async function handleSignOut() {
    await supabase.auth.signOut();
    router.push("/");
  }

  if (!profile) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-gray-500">Loading...</p>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-2xl px-4 py-12">
      <Link
        href="/dashboard"
        className="text-sm text-gray-500 hover:text-gray-700"
      >
        &larr; Dashboard
      </Link>
      <h1 className="mt-4 text-2xl font-bold">Settings</h1>

      <div className="mt-8 space-y-8">
        <section>
          <h2 className="text-lg font-semibold">API Key</h2>
          <p className="mt-1 text-sm text-gray-600">
            Add your OpenRouter API key to use the BYOK tier. Your data stays
            private and there are no rate limits.
          </p>
          <form onSubmit={handleSaveKey} className="mt-4 space-y-3">
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder={
                profile.openrouter_key
                  ? "sk-or-v1-****** (key saved)"
                  : "sk-or-v1-..."
              }
              className="w-full rounded-lg border border-gray-300 px-4 py-2.5 font-mono text-sm focus:border-black focus:outline-none"
            />
            <div className="flex items-center gap-3">
              <button
                type="submit"
                disabled={saving}
                className="rounded-lg bg-black px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50"
              >
                {saving ? "Saving..." : "Save key"}
              </button>
              {profile.openrouter_key && (
                <button
                  type="button"
                  onClick={async () => {
                    setApiKey("");
                    const { error } = await supabase
                      .from("profiles")
                      .update({
                        tier: "free",
                        openrouter_key: null,
                      })
                      .eq("id", profile.id);
                    if (!error)
                      setProfile({
                        ...profile,
                        tier: "free",
                        openrouter_key: null,
                      });
                  }}
                  className="text-sm text-red-600 hover:text-red-800"
                >
                  Remove key
                </button>
              )}
              {message && (
                <span className="text-sm text-gray-500">{message}</span>
              )}
            </div>
          </form>
        </section>

        <section>
          <h2 className="text-lg font-semibold">Your Plan</h2>
          <p className="mt-1 text-sm text-gray-600">
            {profile.tier === "byok"
              ? "BYOK tier: using your own API key, no rate limits, data stays private."
              : "Free tier: we cover API costs, data shared for research (with consent)."}
          </p>
        </section>

        <section>
          <h2 className="text-lg font-semibold">Data Sharing</h2>
          <label className="mt-2 flex items-start gap-3">
            <input
              type="checkbox"
              checked={profile.data_sharing_consent}
              onChange={async (e) => {
                const val = e.target.checked;
                await supabase
                  .from("profiles")
                  .update({
                    data_sharing_consent: val,
                    consent_date: val ? new Date().toISOString() : null,
                  })
                  .eq("id", profile.id);
                setProfile({
                  ...profile,
                  data_sharing_consent: val,
                  consent_date: val ? new Date().toISOString() : null,
                });
              }}
              className="mt-1"
            />
            <span className="text-sm text-gray-600">
              I agree to share my uploaded papers and reviews for academic
              research on AI-assisted peer review.
            </span>
          </label>
        </section>

        <hr />

        <button
          onClick={handleSignOut}
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          Sign out
        </button>
      </div>
    </main>
  );
}
