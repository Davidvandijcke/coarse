import { execFileSync } from "node:child_process";
import { describe, expect, it } from "vitest";

import { buildAgentPrompt, buildCliCommands, getHostModels, type ChatHost } from "@/lib/mcpHandoff";

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


describe("subscription model selection", () => {
  it.each([
    ["claude-code", "anthropic/claude-fable-5.1", "claude-fable-5-1"],
    ["claude-code", "anthropic/claude-opus-5.5", "claude-opus-5-5"],
    ["claude-code", "anthropic/claude-sonnet-5.5", "claude-sonnet-5-5"],
    ["codex", "openai/gpt-6-astra", "gpt-6-astra"],
    ["codex", "openai/gpt-6-sol", "gpt-6-sol"],
    ["codex", "openai/gpt-6-luna", "gpt-6-luna"],
    ["codex", "openai/gpt-6.1-sol", "gpt-6.1-sol"],
    ["gemini-cli", "google/gemini-3.8-flash", "gemini-3.8-flash"],
    ["gemini-cli", "google/gemini-99-flash:free", "gemini-99-flash"],
  ] as const)("carries %s selection into the native command", (host, selected, expected) => {
    const models = getHostModels(host, selected);
    expect(models[0]).toBe(expected);
    expect(new Set(models).size).toBe(models.length);
    const { runCmd } = buildCliCommands({
      handoffUrl: "https://example.test/h/token", host, model: models[0],
      effort: "high", paperId: "00000000-0000-4000-8000-000000000000",
    });
    expect(runCmd).toContain(expected);
    expect(runCmd).not.toContain(selected);
  });

  it.each(["claude-code", "codex", "gemini-cli"] as ChatHost[])(
    "does not carry a different provider into %s", (host) => {
      expect(getHostModels(host, "other/model")).toEqual(getHostModels(host, ""));
    },
  );
});


describe("current agent handoff instructions", () => {
  it.each(["codex", "claude-code", "gemini-cli"] as const)(
    "keeps %s shell commands in literal code fences with bare URL arguments",
    (host) => {
      const handoffUrl = "https://example.test/h/token?a=b%2Bc&next=(paper)&name=O'Reilly";
      const commands = buildCliCommands({
        handoffUrl, host, model: getHostModels(host, "")[0],
        effort: "high", paperId: "test-paper",
      });
      const prompt = buildAgentPrompt({ ...commands, isPdf: false });
      const shellBlocks = [...prompt.matchAll(/```sh\n([^]*?)\n```/g)].map((m) => m[1]);
      expect(shellBlocks).toEqual([commands.setupCmd, commands.runCmd, commands.attachCmd]);
      // Exercise a real POSIX shell without launching uvx or spending credits.
      const argv = execFileSync("/bin/sh", ["-c", `set -- ${shellBlocks[1]}; printf '%s\\0' "$@"`])
        .toString().split("\0").filter(Boolean);
      expect(argv[argv.indexOf("--handoff") + 1]).toBe(handoffUrl);
      expect(argv[argv.indexOf("--host") + 1]).toBe(
        { codex: "codex", "claude-code": "claude", "gemini-cli": "gemini" }[host],
      );
      expect(argv[argv.indexOf("--model") + 1]).toBe(getHostModels(host, "")[0]);
      expect(argv[argv.indexOf("--effort") + 1]).toBe("high");
      expect(prompt).toContain("This formatting correction is authorized");
      expect(prompt).toContain("preserve the entire destination, including query parameters");
      expect(prompt).not.toContain("Do not substitute, rewrite, or interpret any argument");
      expect(prompt).toContain("Read the log and resolve any launch error before retrying");
      expect(prompt).not.toContain("launcher never started");
    },
  );

  it("preserves launch choices and uses supported terminal sessions", () => {
    const prompt = buildAgentPrompt({ ...baseCommands, isPdf: false });
    expect(prompt).toContain(baseCommands.runCmd);
    expect(prompt).toContain("2.1.284");
    expect(prompt).toContain("write_stdin");
    expect(prompt).toContain("run_in_background");
    expect(prompt).not.toContain("--timeout 2700");
    expect(prompt).not.toContain("2700000");
  });
});
