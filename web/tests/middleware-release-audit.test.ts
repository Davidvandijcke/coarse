import { NextRequest } from "next/server";
import { afterEach, describe, expect, it, vi } from "vitest";

async function loadMiddleware() {
  vi.resetModules();
  return import("../src/middleware");
}

afterEach(() => {
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
  vi.resetModules();
});

describe("production preview-config drift warning", () => {
  it.each([
    ["PREVIEW_BASIC_AUTH_USERNAME", "preview-user", "PREVIEW_BASIC_AUTH_PASSWORD"],
    ["PREVIEW_BASIC_AUTH_PASSWORD", "preview-password", "PREVIEW_BASIC_AUTH_USERNAME"],
  ] as const)("warns and passes through when only %s leaks", async (leakedName, leakedValue, absentName) => {
    vi.stubEnv("VERCEL_ENV", "production");
    vi.stubEnv(leakedName, leakedValue);
    vi.stubEnv(absentName, "");
    const error = vi.spyOn(console, "error").mockImplementation(() => undefined);
    const { middleware } = await loadMiddleware();

    const response = middleware(new NextRequest("https://coarse.ink/"));

    expect(response.status).toBe(200);
    expect(error).toHaveBeenCalledTimes(1);
    expect(error.mock.calls[0]?.[0]).toContain(leakedName);
    expect(error.mock.calls[0]?.[0]).not.toContain(absentName);
  });

  it("warns once per module instance when preview Basic Auth leaks into production", async () => {
    vi.stubEnv("VERCEL_ENV", "production");
    vi.stubEnv("PREVIEW_BASIC_AUTH_USERNAME", "preview-user");
    vi.stubEnv("PREVIEW_BASIC_AUTH_PASSWORD", "preview-password");
    const error = vi.spyOn(console, "error").mockImplementation(() => undefined);
    const { middleware } = await loadMiddleware();
    const request = new NextRequest("https://coarse.ink/");

    middleware(request);
    middleware(request);

    expect(error).toHaveBeenCalledTimes(1);
    expect(error.mock.calls[0]?.[0]).toContain("[release-audit]");
    expect(error.mock.calls[0]?.[0]).toContain("PREVIEW_BASIC_AUTH_USERNAME");
    expect(error.mock.calls[0]?.[0]).toContain("PREVIEW_BASIC_AUTH_PASSWORD");
  });

  it("does not warn about intentional preview Basic Auth on preview", async () => {
    vi.stubEnv("VERCEL_ENV", "preview");
    vi.stubEnv("PREVIEW_BASIC_AUTH_USERNAME", "preview-user");
    vi.stubEnv("PREVIEW_BASIC_AUTH_PASSWORD", "preview-password");
    const error = vi.spyOn(console, "error").mockImplementation(() => undefined);
    const { middleware } = await loadMiddleware();

    middleware(new NextRequest("https://preview.example.com/"));

    expect(error).not.toHaveBeenCalled();
  });

  it("does not treat Vercel's production automation-bypass system variable as a leak", async () => {
    vi.stubEnv("VERCEL_ENV", "production");
    vi.stubEnv("PREVIEW_BASIC_AUTH_USERNAME", "");
    vi.stubEnv("PREVIEW_BASIC_AUTH_PASSWORD", "");
    vi.stubEnv("VERCEL_AUTOMATION_BYPASS_SECRET", "platform-managed-value");
    const error = vi.spyOn(console, "error").mockImplementation(() => undefined);
    const { middleware } = await loadMiddleware();

    middleware(new NextRequest("https://coarse.ink/"));

    expect(error).not.toHaveBeenCalled();
  });
});

describe("preview Basic Auth", () => {
  it("accepts the configured pair and rejects an incorrect password", async () => {
    vi.stubEnv("VERCEL_ENV", "preview");
    vi.stubEnv("PREVIEW_BASIC_AUTH_USERNAME", "preview-user");
    vi.stubEnv("PREVIEW_BASIC_AUTH_PASSWORD", "preview-password");
    const { middleware } = await loadMiddleware();
    const authorized = new NextRequest("https://preview.example.com/", {
      headers: {
        authorization: `Basic ${btoa("preview-user:preview-password")}`,
      },
    });
    const rejected = new NextRequest("https://preview.example.com/", {
      headers: {
        authorization: `Basic ${btoa("preview-user:wrong-password")}`,
      },
    });

    expect(middleware(authorized).status).toBe(200);
    expect(middleware(rejected).status).toBe(401);
  });
});
