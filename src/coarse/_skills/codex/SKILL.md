---
name: coarse-review
description: >
  Produce a rigorous academic peer review of a research paper, manuscript,
  or preprint (PDF, markdown, TeX, DOCX, HTML, or EPUB) using the full
  coarse pipeline with the user's local Codex CLI (ChatGPT subscription)
  doing all the review reasoning. Every review-reasoning stage — structure analysis,
  overview synthesis, per-section review, proof verification, editorial
  pass — is served by a headless `codex exec` subprocess instead of a
  paid API; PDF vision QA keeps its configured OpenRouter route. Use when the user asks to review, critique, referee, or
  provide feedback on an academic paper. Takes 10-25 minutes.
---

# coarse-review (Codex)

Runs the **full coarse review pipeline** on a paper using the local `codex exec` CLI as the review-reasoning backend. Review reasoning is served by headless Codex subprocesses using the user's ChatGPT Plus/Pro/Team plan. PDF sources use the user's OpenRouter key locally for ~$0.05-0.15 Mistral OCR and for a small post-extraction vision-QA charge when that check runs; non-PDF sources (.tex, .md, .txt, .docx, .html, .epub) extract locally with no OpenRouter key at all.

## Prerequisites

Use a current Codex installation with access to the selected model. Codex 0.160.0 was verified with GPT-6 Sol, GPT-6 Luna, and GPT-6.1 Sol. Check `codex --version` and update using the original installation method if the model is unsupported. Preserve the handoff command's exact `--model` and `--effort`; GPT-6 models support native `max` effort. Report any model-access error or fallback in the log. Do not change the model or switch to API billing silently.

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
  `uvx --python 3.12 --from 'coarse-ink==1.9.5' coarse install-skills --all --force`
  (If that fails with `No such command 'install-skills'`, you're on a
  PyPI release that predates the command — upgrade or ignore; the skill
  bundle is also loadable directly via `uvx --from` without install.)
- **OpenRouter API key required for PDF papers or an explicitly requested deep literature search** — PDFs use Mistral OCR (~$0.10 per paper) plus a small vision-QA charge when that check runs. Standard non-PDF reviews extract locally and need no OpenRouter key; `--deep-literature-search` uses Perplexity Sonar Deep Research for any format and normally adds about $0.30. Skip the probes below only when both conditions are absent. Prefer checking for the key with presence-only probes so you don't needlessly echo its value into the transcript, but if the user hands you the key directly just save it — don't lecture them.

  For PDF papers, or whenever deep literature search is requested, check whether `OPENROUTER_API_KEY` is already configured before running:
  - In the environment: `test -n "$OPENROUTER_API_KEY" && echo "env: set" || echo "env: missing"`
  - In a `.env` file in the current directory: `test -f .env && grep -q '^OPENROUTER_API_KEY=' .env && echo ".env: set" || echo ".env: missing"`

  If the paper is a PDF or deep literature was requested and neither probe reports "set", ask the user:

  > I need an OpenRouter API key for PDF OCR (~$0.10) and/or the requested deep literature search (~$0.30). A few options:
  >
  > 1. Paste the key here and I'll save it to `~/.coarse/config.toml` via `uvx --python 3.12 --from 'coarse-ink==1.9.5' coarse setup`. Note the key passes through the LLM provider (OpenAI) on its way to me, so treat it as slightly less private than one you typed into a local terminal — rotate at https://openrouter.ai/settings/keys if that worries you.
  > 2. Set it yourself in a separate terminal: `export OPENROUTER_API_KEY=sk-or-v1-...` or add it to `.env` in your current directory, then re-ask me.
  > 3. Run `uvx --python 3.12 --from 'coarse-ink==1.9.5' coarse setup` in a separate terminal yourself and paste the key into its interactive prompt — the key never touches this chat.
  >
  > Which do you want?

  If the user pastes a key here, save it via `uvx --python 3.12 --from 'coarse-ink==1.9.5' coarse setup` with the pasted value and confirm it's stored. Their chat, their choice.
- `codex` CLI logged in: `codex login`.

## How to run

**Two-step launch-and-wait, not foreground.** A full review takes 10-25 minutes, which exceeds Codex's default 5-minute tool timeout. Foreground runs will be killed mid-review and reported as crashed when they're actually still working.

Step 1 detaches the worker (~2 seconds) and writes `<log>.pid`. Step 2 uses `--attach` to block on that pidfile and stream the log until the worker exits, emitting a heartbeat every 30 seconds of log idleness so the Codex shell doesn't flag the command as hung. Use a **per-review unique log file** so parallel runs don't clobber each other's output:

```bash
LOG=/tmp/coarse-review-$(basename <paper_path> .pdf).log

# STEP 2a — launch (returns in ~2s)
uvx --python 3.12 --from 'coarse-ink==1.9.5' \
  coarse-review --detach --log-file "$LOG" \
  <paper_path> --host codex [--model gpt-6-sol] [--effort high] [--deep-literature-search]

# STEP 2b — wait (one blocking call, ~10-25 min, emits heartbeats)
uvx --python 3.12 --from 'coarse-ink==1.9.5' \
  coarse-review --attach "$LOG"
```

Run the attach command with Codex's terminal session mechanism. If `exec_command` returns a session ID, retain it and resume with `write_stdin` until completion; use the documented equivalents if your tool names differ. Do not invent a `--timeout` flag. If the terminal tool ends the watcher early, re-run the same attach command to reconnect. Never repeat `--detach` while that worker is running. Attach exit codes: `0` complete, `1` failure marker, `2` silent crash, `3` missing pidfile, `124` attach's own 30-minute timeout, `130` user interrupt.

When attach exits cleanly, use the final log lines as the authoritative artifact locations:

```bash
rg '^  view:|^  local:' "$LOG"
```

If `local:` is present, read that exact file. If `view:` is present, use that URL (it already includes the signed access token — use it as-is). Do not run broad filesystem searches trying to rediscover the review file.
If `view:` says `unavailable`, report the callback failure and use only the `local:` path.

Available models: `gpt-6-sol` (default), `gpt-6.1-sol`, `gpt-6-luna`, `gpt-6-astra`, `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, `gpt-5.5`, `gpt-5.4`.
Available effort levels: `low`, `medium`, `high` (default), `max`.

These map to Codex's internal reasoning effort:
- `low` → `low`
- `medium` → `medium`
- `high` → `high`
- `max` → the model's highest supported setting (`max` for GPT-5.6 Sol/Terra/Luna; `xhigh` for GPT-5.5 and GPT-5.4)

**Handoff mode** (when the user came from the coarse web form): the paper is a REMOTE resource at the handoff URL. Do NOT search for a local PDF and do NOT ask the user for a file path — the `--handoff` URL IS the paper source. Same two-step launch+attach pattern:

```bash
LOG=/tmp/coarse-review-$(date +%s).log

# STEP 2a — launch
uvx --python 3.12 --from 'coarse-ink==1.9.5' \
  coarse-review --detach --log-file "$LOG" \
  --handoff https://coarse.ink/h/<token> --host codex

# STEP 2b — wait
uvx --python 3.12 --from 'coarse-ink==1.9.5' \
  coarse-review --attach "$LOG"
```

**When complete**, show the user the output path, web URL (if present), recommendation, top issues, and comment count.

## Notes

- `uvx --python 3.12 --from ... coarse-review ...` runs coarse from a temporary environment, so the agent does not mutate the user's global tool install.
- The review process runs locally using the user's own Codex login; coarse.ink only receives the finished markdown callback.
- `coarse-review` monkey-patches `coarse.llm.LLMClient` → `coarse.headless_clients.CodexClient`, which spawns `codex exec -c model_reasoning_effort='<level>' -` for every pipeline LLM call, feeding the prompt via stdin.
- Codex session env vars are stripped so nested sessions don't conflict.
