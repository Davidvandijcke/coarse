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

- `uvx` preferred, `uv` acceptable. First run:
  `command -v uvx || command -v uv`
  - If neither exists, install uv:
    `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Then refresh PATH for the current shell:
    `export PATH="$HOME/.local/bin:$PATH"`
  - If `uv` exists but `uvx` does not, replace `uvx --from ...` below with
    `uv tool run --from ...`.
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
- `codex` CLI logged in: `codex login`.

## How to run

**CRITICAL: Run in the background, not foreground.** A full review takes 10-25 minutes, which exceeds Codex's default 5-minute tool timeout. Foreground runs will be killed mid-review and reported as crashed when they're actually still working.

Use this pattern:

```bash
nohup uvx --from 'coarse-ink[mcp] @ git+https://github.com/Davidvandijcke/coarse@feat/mcp-server' \
  coarse-review <paper_path> --host codex [--model gpt-5.4] [--effort high] \
  > /tmp/coarse-review.log 2>&1 < /dev/null &
echo "Review PID: $!"
```

Then poll the log file every 60-90 seconds:

```bash
tail -20 /tmp/coarse-review.log
```

Do NOT kill the process because you think it hung — the review takes a genuine 10-25 minutes. When the log shows `REVIEW COMPLETE` or `PUBLISHED TO COARSE WEB`, it's done.

When the run finishes, use the final log lines as the authoritative artifact locations:

```bash
rg '^  view:|^  local:' /tmp/coarse-review.log
```

If `local:` is present, read that exact file. If `view:` is present, use that URL. Do not run broad filesystem searches trying to rediscover the review file.
If `view:` says `unavailable`, report the callback failure and use only the `local:` path.

Available models: `gpt-5.4` (default), `gpt-5.3-codex`, `gpt-5.4-mini`, `gpt-5.4-pro`.
Available effort levels: `low`, `medium`, `high` (default), `max`.

These map to Codex's internal reasoning effort:
- `low` → `minimal`
- `medium` → `low`
- `high` → `medium`
- `max` → `high`

**Handoff mode** (when the user came from the coarse web form), same background-process pattern:

```bash
nohup uvx --from 'coarse-ink[mcp] @ git+https://github.com/Davidvandijcke/coarse@feat/mcp-server' \
  coarse-review --handoff coarse.vercel.app/h/<token> --host codex \
  > /tmp/coarse-review.log 2>&1 < /dev/null &
echo "Review PID: $!"
```

**When complete**, show the user the output path, web URL (if present), recommendation, top issues, and comment count.

## Notes

- `uvx --from ... coarse-review ...` runs coarse from a temporary environment, so the agent does not mutate the user's global tool install.
- `coarse-review` monkey-patches `coarse.llm.LLMClient` → `coarse.headless_clients.CodexClient`, which spawns `codex exec -c model_reasoning_effort='<level>' -` for every pipeline LLM call, feeding the prompt via stdin.
- Codex session env vars are stripped so nested sessions don't conflict.
