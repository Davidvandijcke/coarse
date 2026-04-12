---
name: coarse-review
description: >
  Produce a rigorous academic peer review of a research paper, manuscript,
  or preprint (PDF, markdown, TeX, DOCX, HTML, or EPUB) using the full
  coarse pipeline with the user's local Codex CLI (ChatGPT subscription)
  doing all the LLM reasoning. Every pipeline stage — structure analysis,
  overview synthesis, per-section review, proof verification, editorial
  pass — is served by a headless `codex exec` subprocess instead of a
  paid API. Use when the user asks to review, critique, referee, or
  provide feedback on an academic paper. Takes 10-25 minutes.
---

# coarse-review (Codex)

Runs the **full coarse review pipeline** on a paper using the local `codex exec` CLI as the LLM backend. Every LLM call is served by a headless Codex subprocess using the user's ChatGPT Plus/Pro/Team plan. The only per-paper cost is the ~$0.05-0.15 Mistral OCR extraction, which uses the user's OpenRouter key locally.

## Prerequisites

- `coarse-ink` installed: `uvx --from 'coarse-ink[mcp] @ git+https://github.com/Davidvandijcke/coarse@feat/mcp-server' coarse --help` (or `pip install 'coarse-ink[mcp]'` once released)
- OpenRouter key in `~/.coarse/config.toml`, or `OPENROUTER_API_KEY` env var, or `.env` in CWD.
- `codex` CLI logged in: `codex login`.

## How to run

Launch in the background — takes 10-25 minutes:

```bash
coarse-review <paper_path> --host codex [--model gpt-5.4] [--effort high]
```

Available models: `gpt-5.4` (default), `gpt-5.3-codex`, `gpt-5.4-mini`, `gpt-5.4-pro`.
Available effort levels: `low`, `medium`, `high` (default), `max`.

These map to Codex's internal reasoning effort:
- `low` → `minimal`
- `medium` → `low`
- `high` → `medium`
- `max` → `high`

**Handoff mode** (when the user came from the coarse web form):

```bash
coarse-review --handoff coarse.vercel.app/h/<token> --host codex
```

**When complete**, show the user the output path, recommendation, top issues, and comment count.

## Notes

- `coarse-review` monkey-patches `coarse.llm.LLMClient` → `coarse.headless_clients.CodexClient`, which spawns `codex exec -c model_reasoning_effort='<level>' -` for every pipeline LLM call, feeding the prompt via stdin.
- Codex session env vars are stripped so nested sessions don't conflict.
