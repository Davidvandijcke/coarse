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
  `uvx --python 3.12 --from 'coarse-ink==1.3.0' coarse install-skills --all --force`
  (If that fails with `No such command 'install-skills'`, you're on a
  PyPI release that predates the command — upgrade or ignore; the skill
  bundle is also loadable directly via `uvx --from` without install.)
- **OpenRouter API key required** for Mistral OCR extraction (~$0.10 per paper). The key must be set locally on the user's machine. **Never ask the user to paste the key into this chat and never print it yourself** — anything that appears in the chat transcript is sent to the LLM provider and may be retained in logs.

  Before running the review, check whether `OPENROUTER_API_KEY` is already configured *without printing its value*. Use presence-only probes:
  - In the environment: `test -n "$OPENROUTER_API_KEY" && echo "env: set" || echo "env: missing"`
  - In a `.env` file in the current directory: `test -f .env && grep -q '^OPENROUTER_API_KEY=' .env && echo ".env: set" || echo ".env: missing"`

  Do **not** run `echo $OPENROUTER_API_KEY`, `printenv OPENROUTER_API_KEY`, `grep OPENROUTER_API_KEY .env`, or `cat .env` — those commands copy the key value into the transcript.

  If neither probe reports "set", tell the user:

  > I need an OpenRouter API key for the OCR extraction step (~$0.10 per paper). The key has to be set locally — **please don't paste it into this chat**, because anything here is transmitted to the LLM provider and may be logged. Pick one of:
  >
  > 1. **Save it via the setup helper** (recommended): run `uvx --python 3.12 --from 'coarse-ink==1.3.0' coarse setup` yourself in a terminal and paste the key into the interactive prompt. It lands in `~/.coarse/config.toml` and never passes through this chat.
  > 2. **Export it in your shell**: `export OPENROUTER_API_KEY=sk-or-v1-...`, then re-ask me.
  > 3. **Project-local `.env`**: `echo 'OPENROUTER_API_KEY=sk-or-v1-...' >> .env` in your current directory.
  >
  > Tell me once it's set and I'll re-check with the presence probes above.

  If the user pastes a key into chat anyway, **refuse to store it**, remind them that the key has now been exposed to the LLM provider and should be rotated at https://openrouter.ai/settings/keys, then re-offer the three options above.
- `gemini` CLI signed in (first run prompts for OAuth).

## How to run

**CRITICAL — if the user gives you a handoff URL, the paper is REMOTE.** Do NOT run `FindFiles`, `glob`, `find`, `ls`, or any filesystem search looking for a local PDF. Do NOT interpret the handoff URL or any paper ID as a local filename. Do NOT ask the user for a file path — the `--handoff` URL IS the paper source and coarse-review downloads it over the network itself. Run the command verbatim and let coarse-review handle the fetch.

**Two-step launch-and-wait, not foreground.** A full review takes 10-25 minutes, which exceeds Gemini CLI's default 5-minute tool timeout. Step 1 detaches the worker and returns in ~2 seconds. Step 2 uses `--attach` to block on the worker's PID file and stream the log, emitting a heartbeat every 30 seconds of idleness so Gemini's shell tool sees activity.

Use a **per-review unique log file** so parallel runs don't clobber each other's output:

```bash
LOG=/tmp/coarse-review-$(date +%s).log

# STEP 2a — launch (returns in ~2s with Review PID + Log file)
uvx --python 3.12 --from 'coarse-ink==1.3.0' \
  coarse-review --detach --log-file "$LOG" \
  <paper_path_or_handoff_url> --host gemini [--model gemini-3.1-pro-preview] [--effort high]

# STEP 2b — wait (one blocking call, ~10-25 min, emits heartbeats)
uvx --python 3.12 --from 'coarse-ink==1.3.0' \
  coarse-review --attach "$LOG"
```

Run the attach call with a long tool timeout (≥45 minutes) so Gemini CLI doesn't kill the blocking command prematurely. 45 minutes leaves ~20 minutes of margin on top of the 10-25 minute review runtime for cold starts, slow models, long papers, and `--effort max` runs — 30 minutes is too tight because the tool timeout is a wall clock, not an idle-stream cap. Bump to 60 minutes for book-length papers or the largest models. Do NOT re-run the `--detach` command if attach returns early (that would spawn a second worker). Safe to Ctrl+C the attach: the watcher detaches but the worker keeps running. Attach exit codes: `0` complete, `1` failure marker, `2` silent crash, `3` missing pidfile, `124` attach's own 30-min timeout, `130` user interrupt.

When attach exits cleanly, use the final log lines as the authoritative artifact locations:

```bash
rg '^  view:|^  local:' "$LOG"
```

If `local:` is present, read that exact file. If `view:` is present, use that URL (it already includes the signed access token — use it as-is). Do not run broad filesystem searches trying to rediscover the review file.
If `view:` says `unavailable`, report the callback failure and use only the `local:` path.

Available models: `gemini-3.1-pro-preview` (default), `gemini-3-flash-preview`, `gemini-3.1-flash-lite-preview`.
Available effort levels: `low`, `medium`, `high` (default), `max`.

**Handoff mode** (when the user came from the coarse web form): the paper is a REMOTE resource at the handoff URL. Do NOT search for a local PDF. Same two-step launch+attach pattern — coarse-review fetches the paper over the network:

```bash
LOG=/tmp/coarse-review-$(date +%s).log

# STEP 2a — launch
uvx --python 3.12 --from 'coarse-ink==1.3.0' \
  coarse-review --detach --log-file "$LOG" \
  --handoff https://coarse.ink/h/<token> --host gemini

# STEP 2b — wait
uvx --python 3.12 --from 'coarse-ink==1.3.0' \
  coarse-review --attach "$LOG"
```

**When complete**, show the user the output path, web URL (if present), recommendation, top issues, and comment count.

## Notes

- `uvx --python 3.12 --from ... coarse-review ...` runs coarse from a temporary environment, so the agent does not mutate the user's global tool install.
- The review process runs locally using the user's own Gemini CLI login; coarse.ink only receives the finished markdown callback.
- `coarse-review` monkey-patches `coarse.llm.LLMClient` → `coarse.headless_clients.GeminiClient`, which spawns `gemini --approval-mode yolo --output-format text` and feeds the prompt via stdin.
- Gemini session env vars are stripped so nested sessions don't conflict.
