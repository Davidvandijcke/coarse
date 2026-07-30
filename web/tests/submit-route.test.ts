import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => {
  const makeBuilder = (table: string) => {
    const result = { data: null, error: null };
    const builder: Record<string, unknown> = {};
    for (const method of ["select", "eq", "update", "delete"]) {
      builder[method] = vi.fn(() => builder);
    }
    builder.insert = vi.fn(async () => result);
    builder.single = vi.fn(async () =>
      table === "reviews"
        ? {
            data: {
              id: "00000000-0000-4000-8000-000000000001",
              paper_filename: "paper.pdf",
              status: "queued",
            },
            error: null,
          }
        : result,
    );
    builder.maybeSingle = vi.fn(async () => result);
    builder.then = (resolve: (value: typeof result) => unknown) =>
      Promise.resolve(result).then(resolve);
    return builder;
  };
  const supabase = {
    from: vi.fn((table: string) => makeBuilder(table)),
    rpc: vi.fn(async () => ({ data: 0, error: null })),
  };
  return {
    supabase,
    sendReviewEmail: vi.fn(async () => undefined),
  };
});

vi.mock("@supabase/supabase-js", () => ({
  createClient: vi.fn(() => mocks.supabase),
}));
vi.mock("@/lib/rateLimit", () => ({ checkRateLimit: vi.fn(async () => null) }));
vi.mock("@/lib/reviewAuth", () => ({
  extractReviewAccessToken: vi.fn(() => "access-token"),
  hasValidReviewAccessToken: vi.fn(() => true),
}));
vi.mock("@/lib/reviewAccess", () => ({
  buildReviewKey: vi.fn(() => "review-key"),
  buildReviewUrl: vi.fn(() => "https://coarse.test/status/review"),
}));
vi.mock("@/lib/emailCapacity", () => ({
  isEmailCapacityReached: vi.fn(async () => false),
}));
vi.mock("@/lib/routeHandoffAuth", () => ({
  consumeReviewHandoffSecret: vi.fn(async () => ({ ok: true })),
}));
vi.mock("@/lib/email", () => ({ sendReviewEmail: mocks.sendReviewEmail }));
vi.mock("@/lib/modalWebhook", () => ({
  buildModalWebhookHostSuffix: vi.fn(() => "-coarse-review-run-review.modal.run"),
  getModalWebhookConfig: vi.fn(() => ({
    url: "https://owner--coarse-review-run-review.modal.run",
    secret: "webhook-secret",
  })),
}));
vi.mock("@/lib/reviewCapacity", () => ({
  getActiveReviewWindowStartIso: vi.fn(() => "2026-07-30T00:00:00.000Z"),
  MAX_CONCURRENT_REVIEWS: 10,
}));
vi.mock("@/lib/systemStatus", () => ({
  getSubmissionPauseResponse: vi.fn(async () => null),
}));
vi.mock("@/lib/siteOrigin", () => ({
  getSiteOriginForRequest: vi.fn(() => "https://coarse.test"),
}));

import { NextRequest } from "next/server";

import { POST } from "@/app/api/submit/route";

const id = "00000000-0000-4000-8000-000000000001";

function requestWith(deepLiteratureSearch: unknown, includeField = true): NextRequest {
  const body: Record<string, unknown> = {
    id,
    email: "reader@example.com",
    api_key: "sk-or-test",
    model: "anthropic/claude-opus-5",
    storage_path: `${id}.pdf`,
    handoff_secret: "handoff-secret",
  };
  if (includeField) body.deep_literature_search = deepLiteratureSearch;
  return new NextRequest("https://coarse.test/api/submit", {
    method: "POST",
    body: JSON.stringify(body),
    headers: { "content-type": "application/json" },
  });
}

describe("POST /api/submit deep_literature_search", () => {
  beforeEach(() => {
    vi.stubEnv("NEXT_PUBLIC_SUPABASE_URL", "https://project.supabase.co");
    vi.stubEnv("SUPABASE_SERVICE_KEY", "service-key");
    vi.stubGlobal("fetch", vi.fn(async () => new Response(null, { status: 202 })));
  });

  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
  });

  it.each([
    ["omitted", undefined, false, false],
    ["enabled", true, true, true],
  ])("forwards %s as %s", async (_label, value, expected, includeField) => {
    const response = await POST(requestWith(value, includeField));
    expect(response.status).toBe(200);
    expect(fetch).toHaveBeenCalledTimes(1);
    const init = vi.mocked(fetch).mock.calls[0][1];
    const workerBody = JSON.parse(String(init?.body));
    expect(workerBody.deep_literature_search).toBe(expected);
  });

  it("rejects non-boolean values before dispatch", async () => {
    const response = await POST(requestWith("true"));
    expect(response.status).toBe(400);
    await expect(response.json()).resolves.toEqual({
      error: "deep_literature_search must be a boolean",
    });
    expect(fetch).not.toHaveBeenCalled();
  });
});
