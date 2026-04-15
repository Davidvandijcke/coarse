---
name: coarse-review
description: >
  Produce a rigorous academic peer review of a research paper, manuscript,
  or preprint (PDF, markdown, TeX, DOCX, HTML, or EPUB) using the full
  coarse pipeline with the user's local Claude Code subscription doing
  all the LLM reasoning. Every pipeline stage — structure analysis,
  overview synthesis, per-section review, proof verification, editorial
  pass — is served by a headless `claude -p` subprocess instead of a
  paid API. Use when the user asks to review, critique, referee, or
  provide feedback on an academic paper. Takes 10-25 minutes. Do NOT
  use for code review, blog posts, or non-academic documents.
---

# coarse-review (Claude Code)

Runs the **full coarse review pipeline** on a paper using the local `claude -p` CLI as the LLM backend. Every LLM call the pipeline makes — structure metadata, overview, per-section review, proof verification, editorial dedup — is served by a headless Claude Code subprocess using the user's Claude Max subscription. The only per-paper cost is the ~$0.05-0.15 Mistral OCR extraction, which uses the user's OpenRouter key locally.

This is the **same pipeline** that powers coarse.ink — only the LLM backend is swapped.

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
- **OpenRouter API key required** for Mistral OCR extraction (~$0.10 per paper). Prefer checking for the key with presence-only probes so you don't needlessly echo its value into the transcript, but if the user hands you the key directly just save it — don't lecture them.

  Before running the review, check whether `OPENROUTER_API_KEY` is already configured:
  - In the environment: `test -n "$OPENROUTER_API_KEY" && echo "env: set" || echo "env: missing"`
  - In a `.env` file in the current directory: `test -f .env && grep -q '^OPENROUTER_API_KEY=' .env && echo ".env: set" || echo ".env: missing"`

  If neither probe reports "set", ask the user:

  > I need an OpenRouter API key for the OCR extraction step (~$0.10 per paper). A few options:
  >
  > 1. Paste the key here and I'll save it to `~/.coarse/config.toml` via `uvx --python 3.12 --from 'coarse-ink==1.3.0' coarse setup`. Note the key passes through the LLM provider (Anthropic / OpenAI / Google) on its way to me, so treat it as slightly less private than one you typed into a local terminal — rotate at https://openrouter.ai/settings/keys if that worries you.
  > 2. Set it yourself in a separate terminal: `export OPENROUTER_API_KEY=sk-or-v1-...` or add it to `.env` in your current directory, then re-ask me.
  > 3. Run `uvx --python 3.12 --from 'coarse-ink==1.3.0' coarse setup` in a separate terminal yourself and paste the key into its interactive prompt — the key never touches this chat.
  >
  > Which do you want?

  If the user pastes a key here, save it via `uvx --python 3.12 --from 'coarse-ink==1.3.0' coarse setup` with the pasted value and confirm it's stored. Their chat, their choice.
- `claude` CLI logged in.

## How to run

**Get the paper path from the user.** PDF is most common but any coarse-supported format works.

**If they already have a pre-extracted markdown** (from a previous coarse run), pass it with `--pre-extracted` to skip OCR.

**Launch in the background, then wait with `--attach` — two Bash calls, one approval per call.** A full review takes 10-25 minutes, which exceeds Claude Code's default 2-minute tool timeout, so you can't just run coarse-review in the foreground. Instead, split the run into two steps: `--detach` starts a background worker and returns in ~2 seconds; `--attach` blocks on the worker's PID and streams the log until completion, emitting a heartbeat every 30 seconds of log idleness so the Bash tool sees activity.

Use a **per-review unique log file** so parallel runs in the same shell don't clobber each other's output:

```bash
# Pick a unique suffix — use the paper filename stem or `$(date +%s)`:
LOG=/tmp/coarse-review-$(basename <paper_path> .pdf).log

# STEP 2a — launch (returns within 2 seconds with Review PID + Log file)
uvx --python 3.12 --from 'coarse-ink==1.3.0' \
  coarse-review --detach --log-file "$LOG" \
  <paper_path> --host claude [--model claude-opus-4-6] [--effort high]

# STEP 2b — wait (one blocking call, ~10-25 min, emits heartbeats)
uvx --python 3.12 --from 'coarse-ink==1.3.0' \
  coarse-review --attach "$LOG"
```

Run the attach call with a long Bash-tool timeout: in Claude Code, pass `timeout: 2700000` (45 minutes) on the `Bash` tool invocation so the tool doesn't kill the blocking command. The 45-minute recommendation leaves ~20 minutes of margin on top of the 10-25 minute review runtime for cold starts, slow models, long papers, and `--effort max` runs — 30 minutes is too tight because the tool timeout is a wall clock, not an idle-stream cap. Bump to 60 minutes for book-length papers or the largest models. Do NOT re-run the `--detach` command from STEP 2a if the attach call returns early — that would spawn a second worker. Safe to Ctrl+C the attach: the watcher detaches but the worker keeps running, and you can re-attach with the same command. Attach exit codes: `0` complete, `1` failure marker, `2` silent crash, `3` missing pidfile, `124` attach's own 30-min timeout, `130` user interrupt.

**When attach exits with code 0, do NOT hunt across the filesystem for the review file.** `coarse-review` prints the authoritative paths in the final log lines:

```bash
rg '^  view:|^  local:' "$LOG"
```

- `local:` is the exact markdown path that was written, even if `uvx` used a temporary working directory.
- `view:` is the canonical coarse web URL in handoff mode.

If `view:` says `unavailable`, treat that as a callback failure and report only the local path. Do **not** try to discover another web URL, and do **not** run broad `find`, `locate`, `lsof`, or whole-computer searches trying to rediscover the output.

Available models: `claude-opus-4-6` (default), `claude-sonnet-4-6`, `claude-haiku-4-5`.
Available effort levels: `low`, `medium`, `high` (default), `max`.

If the user came from the coarse web form, they'll paste a handoff URL instead of a local file path. The paper is a REMOTE resource at that URL — do NOT search for a local PDF and do NOT ask the user for a file path. Same two-step launch+attach pattern:

```bash
LOG=/tmp/coarse-review-$(date +%s).log

# STEP 2a — launch
uvx --python 3.12 --from 'coarse-ink==1.3.0' \
  coarse-review --detach --log-file "$LOG" \
  --handoff https://coarse.ink/h/<token> --host claude [--model ...] [--effort ...]

# STEP 2b — wait (same long-timeout discipline as local mode)
uvx --python 3.12 --from 'coarse-ink==1.3.0' \
  coarse-review --attach "$LOG"
```

This downloads the paper from the handoff URL, runs the pipeline, and POSTs the final review back so it shows up at `https://coarse.ink/review/<paper_id>?token=<access_token>`. The `view:` line in the log will already include the signed access token — use that URL as-is.

**When the script completes** (you'll be notified), read the output markdown and show the user:

- Output path
- Web URL from the `view:` line in handoff mode
- Recommendation (accept / revise_and_resubmit / reject)
- Top 2-3 macro issues from the overall feedback section
- Total comment count

## Notes

- `uvx --python 3.12 --from ... coarse-review ...` runs coarse from a temporary environment, so the agent does not mutate the user's global tool install.
- The review process runs locally using the user's own Claude Code login; coarse.ink only receives the finished markdown callback.
- The driver monkey-patches `coarse.llm.LLMClient` → `coarse.headless_clients.ClaudeCodeClient`, which spawns `claude -p` subprocesses for every pipeline LLM call.
- Host-CLI env vars (`CLAUDECODE`, `CLAUDE_CODE_ENTRYPOINT`, etc.) are stripped from the subprocess environment so nested sessions don't conflict with the parent.
- If a single `claude -p` call exceeds 30 minutes, it's killed and the pipeline continues without that section's comments.
- Check progress via `tail -f $LOG` where `$LOG` is the per-review log path you set in step 2 (e.g. `/tmp/coarse-review-<paper-stem>.log`). Prefer the `coarse-review --attach "$LOG"` pattern above — it replaces per-poll `tail` calls with a single blocking watch command that emits heartbeats every 30 seconds of log idleness.
