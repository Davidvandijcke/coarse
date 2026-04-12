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

- `coarse-ink` installed: `pip install 'coarse-ink[mcp] @ git+https://github.com/Davidvandijcke/coarse@feat/mcp-server'` (or `pip install 'coarse-ink[mcp]'` once released)
- **OpenRouter API key required** for Mistral OCR extraction (~$0.10 per paper). The key is NOT passed through the web handoff for security reasons.

  Before running the review, check if `OPENROUTER_API_KEY` is set:
  - In the environment: `echo $OPENROUTER_API_KEY` or `printenv OPENROUTER_API_KEY`
  - In a `.env` file in the current directory: `grep OPENROUTER_API_KEY .env`

  If neither is set, tell the user:

  > I need an OpenRouter API key for the OCR extraction step (~$0.10 per paper). You have three options:
  >
  > 1. **Get a key** at https://openrouter.ai/settings/keys (or via http://localhost:3000/setup) and **paste it to me** — I'll save it to a `.env` file in this directory for you.
  > 2. **Set it yourself**: `export OPENROUTER_API_KEY=sk-or-v1-...` then re-ask me.
  > 3. **Add it to `.env`** yourself: `echo 'OPENROUTER_API_KEY=sk-or-v1-...' >> .env`
  >
  > Which would you like?

  If the user pastes a key, save it to `./.env` (create the file if missing, or **append** if it exists — never overwrite existing vars). Verify the key starts with `sk-or-` before saving.
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
