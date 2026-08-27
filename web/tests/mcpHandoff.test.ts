import { describe, expect, it } from "vitest";

import { buildAgentPrompt, buildCliCommands } from "@/lib/mcpHandoff";

const baseCommands = {
  setupCmd: "uvx --from coarse-ink coarse install-skills --all --force",
  runCmd: "uvx --from coarse-ink coarse-review --handoff https://example.test/h/token",
  attachCmd: "uvx --from coarse-ink coarse-review --attach /tmp/review.log",
  logFile: "/tmp/review.log",
};

describe("deep-literature subscription handoff", () => {
  it.each([false, true])(
    "emits the CLI flag exactly when enabled (enabled=%s)",
    (deepLiteratureSearch) => {
      const { runCmd } = buildCliCommands({
        handoffUrl: "https://example.test/h/token?a=b&c=d",
        host: "codex",
        model: "gpt-5.6-sol",
        effort: "high",
        paperId: "00000000-0000-4000-8000-000000000000",
        deepLiteratureSearch,
      });
      const occurrences = runCmd.match(/--deep-literature-search/g)?.length ?? 0;
      expect(occurrences).toBe(deepLiteratureSearch ? 1 : 0);
    },
  );

  it("keeps a standard non-PDF review key-free", () => {
    const prompt = buildAgentPrompt({
      ...baseCommands,
      isPdf: false,
      deepLiteratureSearch: false,
    });
    expect(prompt).toContain("No OpenRouter API key is needed for this review");
    expect(prompt).toContain("Do NOT ask me for an OpenRouter key");
  });

  it("requires a key for deep search on a non-PDF source", () => {
    const prompt = buildAgentPrompt({
      ...baseCommands,
      isPdf: false,
      deepLiteratureSearch: true,
    });
    expect(prompt).toContain("requested Perplexity deep literature search");
    expect(prompt).not.toContain("No OpenRouter API key is needed for this review");
  });

  it("continues to require a key for PDF OCR", () => {
    const prompt = buildAgentPrompt({
      ...baseCommands,
      isPdf: true,
      deepLiteratureSearch: false,
    });
    expect(prompt).toContain("PDF processing");
    expect(prompt).toContain("triggered vision QA");
    expect(prompt).not.toContain("No OpenRouter API key is needed for this review");
  });
});
