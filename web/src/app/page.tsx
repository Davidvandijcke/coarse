import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center px-4">
      <div className="max-w-2xl text-center">
        <h1 className="text-5xl font-bold tracking-tight">coarse</h1>
        <p className="mt-4 text-xl text-gray-600">
          Free AI paper reviewer. Get detailed feedback on your academic paper in
          minutes.
        </p>

        <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:justify-center">
          <Link
            href="/review/new"
            className="rounded-lg bg-black px-6 py-3 text-lg font-medium text-white hover:bg-gray-800"
          >
            Review a paper
          </Link>
          <a
            href="https://github.com/Davidvandijcke/coarse"
            className="rounded-lg border border-gray-300 px-6 py-3 text-lg font-medium hover:bg-gray-100"
            target="_blank"
            rel="noopener noreferrer"
          >
            View on GitHub
          </a>
        </div>

        <div className="mt-16 grid gap-8 text-left sm:grid-cols-3">
          <div>
            <h3 className="font-semibold">$2-5 per review</h3>
            <p className="mt-1 text-sm text-gray-600">
              Pay only the LLM provider cost. No markup, no subscription.
              Compare to $50 on refine.ink.
            </p>
          </div>
          <div>
            <h3 className="font-semibold">20+ detailed comments</h3>
            <p className="mt-1 text-sm text-gray-600">
              Verbatim quotes from your paper with specific, actionable feedback
              on every section.
            </p>
          </div>
          <div>
            <h3 className="font-semibold">Open source</h3>
            <p className="mt-1 text-sm text-gray-600">
              Run it locally with your own API key, or use our hosted version
              for free.
            </p>
          </div>
        </div>

        <div className="mt-16 rounded-lg border border-gray-200 bg-white p-6 text-left">
          <h2 className="text-lg font-semibold">Two ways to use coarse</h2>
          <div className="mt-4 space-y-4">
            <div>
              <h3 className="font-medium">
                Free tier — help advance AI review research
              </h3>
              <p className="text-sm text-gray-600">
                We cover the API costs. In exchange, your paper and review are
                shared (with your consent) for academic research on AI-assisted
                peer review.
              </p>
            </div>
            <div>
              <h3 className="font-medium">Bring your own key (BYOK)</h3>
              <p className="text-sm text-gray-600">
                Provide your OpenRouter API key. Your data stays private. No
                rate limits.
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
