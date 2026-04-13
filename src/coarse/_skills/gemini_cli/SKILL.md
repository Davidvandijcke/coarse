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

- Refresh the bundled `coarse-review` skill with an ephemeral install:
  `uvx --from 'coarse-ink[mcp] @ git+https://github.com/Davidvandijcke/coarse@feat/mcp-server' coarse install-skills --all --force`
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

**CRITICAL: Run the command as a background process, not in the foreground.** A full review takes 10-25 minutes, which exceeds Gemini CLI's default 5-minute tool timeout. If you run it in the foreground, the tool will kill it mid-review and report a false crash.

Use this exact pattern:

```bash
nohup uvx --from 'coarse-ink[mcp] @ git+https://github.com/Davidvandijcke/coarse@feat/mcp-server' \
  coarse-review <paper_path> --host gemini [--model gemini-3.1-pro-preview] [--effort high] \
  > /tmp/coarse-review.log 2>&1 < /dev/null &
echo "Review PID: $!"
```

Then poll the log file every 60-90 seconds:

```bash
tail -20 /tmp/coarse-review.log
```

Do NOT kill the process because you think it hung — it takes a genuine 10-25 minutes. When the log shows `REVIEW COMPLETE` or `PUBLISHED TO COARSE WEB`, the run is done.

Available models: `gemini-3.1-pro-preview` (default), `gemini-3-flash-preview`, `gemini-3.1-flash-lite-preview`.
Available effort levels: `low`, `medium`, `high` (default), `max`.

**Handoff mode** (when the user came from the coarse web form), same background-process pattern:

```bash
nohup uvx --from 'coarse-ink[mcp] @ git+https://github.com/Davidvandijcke/coarse@feat/mcp-server' \
  coarse-review --handoff coarse.vercel.app/h/<token> --host gemini \
  > /tmp/coarse-review.log 2>&1 < /dev/null &
echo "Review PID: $!"
```

**When complete**, show the user the output path, recommendation, top issues, and comment count.

## Notes

- `uvx --from ... coarse-review ...` runs coarse from a temporary environment, so the agent does not mutate the user's global tool install.
- `coarse-review` monkey-patches `coarse.llm.LLMClient` → `coarse.headless_clients.GeminiClient`, which spawns `gemini --approval-mode yolo --output-format text` and feeds the prompt via stdin.
- Gemini session env vars are stripped so nested sessions don't conflict.
