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
  - coarse requires Python 3.12+. If needed, install it with:
    `uv python install 3.12`
  - If `uv` exists but `uvx` does not, replace `uvx --python 3.12 --from ...` below with
    `uv tool run --python 3.12 --from ...`.
- Refresh the bundled `coarse-review` skill with an ephemeral install:
  `uvx --python 3.12 --from 'coarse-ink[mcp]==1.3.0' coarse install-skills --all --force`
  (If that fails with `No such command 'install-skills'`, you're on a
  PyPI release that predates the command — upgrade or ignore; the skill
  bundle is also loadable directly via `uvx --from` without install.)
- **OpenRouter API key required** for Mistral OCR extraction (~$0.10 per paper). The key is NOT passed through the web handoff for security reasons.

  Before running the review, check if `OPENROUTER_API_KEY` is set:
  - In the environment: `echo $OPENROUTER_API_KEY` or `printenv OPENROUTER_API_KEY`
  - In a `.env` file in the current directory: `grep OPENROUTER_API_KEY .env`

  If neither is set, tell the user:

  > I need an OpenRouter API key for the OCR extraction step (~$0.10 per paper). You have three options:
  >
  > 1. **Get a key** at https://openrouter.ai/settings/keys (or via http://localhost:3000/setup) and **paste it to me** — I'll save it to `~/.coarse/config.toml` for you with `uvx --python 3.12 --from 'coarse-ink[mcp]==1.3.0' coarse setup`.
  > 2. **Set it yourself**: `export OPENROUTER_API_KEY=sk-or-v1-...` then re-ask me.
  > 3. **If you explicitly prefer project-local storage**, add it to `.env` yourself: `echo 'OPENROUTER_API_KEY=sk-or-v1-...' >> .env`
  >
  > Which would you like?

  If the user pastes a key, prefer saving it with `uvx --python 3.12 --from 'coarse-ink[mcp]==1.3.0' coarse setup` so it lands in `~/.coarse/config.toml`. Only write `./.env` if the user explicitly asks for project-local storage. Verify the key starts with `sk-or-` before saving.
- `codex` CLI logged in: `codex login`.

## How to run

**Two-step launch-and-wait, not foreground.** A full review takes 10-25 minutes, which exceeds Codex's default 5-minute tool timeout. Foreground runs will be killed mid-review and reported as crashed when they're actually still working.

Step 1 detaches the worker (~2 seconds) and writes `<log>.pid`. Step 2 uses `--attach` to block on that pidfile and stream the log until the worker exits, emitting a heartbeat every 30 seconds of log idleness so the Codex shell doesn't flag the command as hung. Use a **per-review unique log file** so parallel runs don't clobber each other's output:

```bash
LOG=/tmp/coarse-review-$(basename <paper_path> .pdf).log

# STEP 2a — launch (returns in ~2s)
uvx --python 3.12 --from 'coarse-ink[mcp]==1.3.0' \
  coarse-review --detach --log-file "$LOG" \
  <paper_path> --host codex [--model gpt-5.4] [--effort high]

# STEP 2b — wait (one blocking call, ~10-25 min, emits heartbeats)
uvx --python 3.12 --from 'coarse-ink[mcp]==1.3.0' \
  coarse-review --attach "$LOG"
```

Run the attach call with a long tool timeout — at least 30 minutes — so Codex doesn't kill the blocking command prematurely. Do NOT re-run the `--detach` command from STEP 2a if the attach call returns early (that would spawn a second worker). Safe to Ctrl+C the attach: the watcher detaches but the worker keeps running, and re-attaching with the same command is idempotent. Attach exit codes: `0` complete, `1` failure marker, `2` silent crash, `3` missing pidfile, `124` attach's own 30-min timeout, `130` user interrupt.

When attach exits cleanly, use the final log lines as the authoritative artifact locations:

```bash
rg '^  view:|^  local:' "$LOG"
```

If `local:` is present, read that exact file. If `view:` is present, use that URL (it already includes the signed access token — use it as-is). Do not run broad filesystem searches trying to rediscover the review file.
If `view:` says `unavailable`, report the callback failure and use only the `local:` path.

Available models: `gpt-5.4` (default), `gpt-5.3-codex`, `gpt-5.4-mini`, `gpt-5.4-pro`.
Available effort levels: `low`, `medium`, `high` (default), `max`.

These map to Codex's internal reasoning effort:
- `low` → `low`
- `medium` → `medium`
- `high` → `high`
- `max` → `high`

**Handoff mode** (when the user came from the coarse web form): the paper is a REMOTE resource at the handoff URL. Do NOT search for a local PDF and do NOT ask the user for a file path — the `--handoff` URL IS the paper source. Same two-step launch+attach pattern:

```bash
LOG=/tmp/coarse-review-$(date +%s).log

# STEP 2a — launch
uvx --python 3.12 --from 'coarse-ink[mcp]==1.3.0' \
  coarse-review --detach --log-file "$LOG" \
  --handoff https://coarse.ink/h/<token> --host codex

# STEP 2b — wait
uvx --python 3.12 --from 'coarse-ink[mcp]==1.3.0' \
  coarse-review --attach "$LOG"
```

**When complete**, show the user the output path, web URL (if present), recommendation, top issues, and comment count.

## Notes

- `uvx --python 3.12 --from ... coarse-review ...` runs coarse from a temporary environment, so the agent does not mutate the user's global tool install.
- The review process runs locally using the user's own Codex login; coarse.ink only receives the finished markdown callback.
- `coarse-review` monkey-patches `coarse.llm.LLMClient` → `coarse.headless_clients.CodexClient`, which spawns `codex exec -c model_reasoning_effort='<level>' -` for every pipeline LLM call, feeding the prompt via stdin.
- Codex session env vars are stripped so nested sessions don't conflict.
