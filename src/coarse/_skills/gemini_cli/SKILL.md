---
name: coarse-review
description: >
  Produce a rigorous academic peer review of a research paper, manuscript,
  or preprint (PDF, markdown, TeX, DOCX, HTML, or EPUB) using the full
  coarse pipeline with the user's local Gemini CLI (Google AI subscription)
  doing all the LLM reasoning. Every pipeline stage — structure analysis,
  overview synthesis, per-section review, proof verification, editorial
  pass — is served by a headless `gemini -p` subprocess instead of a
  paid API. Use when the user asks to review, critique, referee, or
  provide feedback on an academic paper. Takes 10-25 minutes.
---

# coarse-review (Gemini)

Runs the **full coarse review pipeline** on a paper using the local `gemini -p` CLI as the LLM backend. Every LLM call is served by a headless Gemini subprocess using the user's Google AI Pro / Ultra subscription. The only per-paper cost is the ~$0.05-0.15 Mistral OCR extraction, which uses the user's OpenRouter key locally.

## Prerequisites

- `coarse-ink` installed: `pipx install 'coarse-ink[mcp]'`
- OpenRouter key in `~/.coarse/config.toml`, or `OPENROUTER_API_KEY` env var, or `.env` in CWD.
- `gemini` CLI signed in (first run prompts for OAuth).

## How to run

Launch in the background — takes 10-25 minutes:

```bash
coarse-review <paper_path> --host gemini [--model gemini-3-pro] [--effort high]
```

Available models: `gemini-3-pro` (default), `gemini-3-flash`, `gemini-2.5-pro`.
Available effort levels: `low`, `medium`, `high` (default), `max`.

**Handoff mode** (when the user came from the coarse web form):

```bash
coarse-review --handoff coarse.vercel.app/h/<token> --host gemini
```

**When complete**, show the user the output path, recommendation, top issues, and comment count.

## Notes

- `coarse-review` monkey-patches `coarse.llm.LLMClient` → `coarse.headless_clients.GeminiClient`, which spawns `gemini --approval-mode yolo --output-format text` and feeds the prompt via stdin.
- Gemini session env vars are stripped so nested sessions don't conflict.
