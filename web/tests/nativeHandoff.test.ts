import { execFileSync } from "node:child_process";
import { afterEach, describe, expect, it, vi } from "vitest";
import { buildNativePrompt, nativeLaunchUrl, nativePilotAvailable } from "@/lib/nativeHandoff";

afterEach(() => vi.unstubAllEnvs());

describe("native handoff pilot", () => {
  it("is opt-in and leaves Gemini and paid deep search on their existing path", () => {
    vi.stubEnv("NEXT_PUBLIC_NATIVE_REVIEW_PILOT", "");
    expect(nativePilotAvailable("codex")).toBe(false);
    vi.stubEnv("NEXT_PUBLIC_NATIVE_REVIEW_PILOT", "1");
    expect(nativePilotAvailable("codex")).toBe(true);
    expect(nativePilotAvailable("claude-code")).toBe(true);
    expect(nativePilotAvailable("gemini-cli")).toBe(false);
    expect(nativePilotAvailable("codex", true)).toBe(false);
  });

  it.each(["codex", "claude-code"] as const)("preserves %s handoff through shell and app launch", (host) => {
    const url = "https://example.test/h/pilot?a=b%2Bc&name=O'Reilly";
    const prompt = buildNativePrompt({ handoffUrl: url, host, paperId: "pilot", reviewLanguage: "fr", authorNotes: "Check the author's proof & assumptions" });
    const blocks = [...prompt.matchAll(/```sh\n([^]*?)\n```/g)].map(m => m[1]);
    expect(blocks).toHaveLength(2);
    expect(blocks[0]).toContain("coarse-native install-skill");
    const args = execFileSync("/bin/sh", ["-c", `set -- ${blocks[1]}; printf '%s\\0' "$@"`])
      .toString().split("\0").filter(Boolean);
    expect(args[args.indexOf("--handoff") + 1]).toBe(url);
    expect(args[args.indexOf("--host") + 1]).toBe(host === "codex" ? "codex" : "claude");
    expect(args[args.indexOf("--language") + 1]).toBe("French");
    expect(args[args.indexOf("--author-notes") + 1]).toBe("Check the author's proof & assumptions");
    expect(args).not.toContain("--detach");
    expect(args).not.toContain("--model");
    const launch = nativeLaunchUrl(host, prompt);
    if (host === "codex") expect(new URL(launch).searchParams.get("prompt")).toBe(prompt);
    else expect(launch).toBe("claude://");
  });
});
