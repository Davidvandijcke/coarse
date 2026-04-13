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

This is the **same pipeline** that powers coarse.vercel.app — only the LLM backend is swapped.

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
  `uvx --python 3.12 --from 'coarse-ink[mcp]==1.2.2' coarse install-skills --all --force`
- **OpenRouter API key required** for Mistral OCR extraction (~$0.10 per paper). The key is NOT passed through the web handoff for security reasons.

  Before running the review, check if `OPENROUTER_API_KEY` is set:
  - In the environment: `echo $OPENROUTER_API_KEY` or `printenv OPENROUTER_API_KEY`
  - In a `.env` file in the current directory: `grep OPENROUTER_API_KEY .env`

  If neither is set, tell the user:

  > I need an OpenRouter API key for the OCR extraction step (~$0.10 per paper). You have three options:
  >
  > 1. **Get a key** at https://openrouter.ai/settings/keys (or via http://localhost:3000/setup) and **paste it to me** — I'll save it to `~/.coarse/config.toml` for you with `uvx --python 3.12 --from 'coarse-ink[mcp]==1.2.2' coarse setup`.
  > 2. **Set it yourself**: `export OPENROUTER_API_KEY=sk-or-v1-...` then re-ask me.
  > 3. **If you explicitly prefer project-local storage**, add it to `.env` yourself: `echo 'OPENROUTER_API_KEY=sk-or-v1-...' >> .env`
  >
  > Which would you like?

  If the user pastes a key, prefer saving it with `uvx --python 3.12 --from 'coarse-ink[mcp]==1.2.2' coarse setup` so it lands in `~/.coarse/config.toml`. Only write `./.env` if the user explicitly asks for project-local storage. Verify the key starts with `sk-or-` before saving.
- `claude` CLI logged in.

## How to run

**Get the paper path from the user.** PDF is most common but any coarse-supported format works.

**If they already have a pre-extracted markdown** (from a previous coarse run), pass it with `--pre-extracted` to skip OCR.

**Launch in the background** — full review takes 10-25 minutes, which exceeds Claude Code's default 2-minute tool timeout. Always use `run_in_background: true` or redirect to a log file so it's not killed mid-run:

```bash
uvx --python 3.12 --from 'coarse-ink[mcp]==1.2.2' \
  coarse-review --detach --log-file /tmp/coarse-review.log \
  <paper_path> --host claude [--model claude-opus-4-6] [--effort high]
```

This returns immediately with the review PID and writes all output to
`/tmp/coarse-review.log`.

Then poll the log every 60-90 seconds with `tail -20 /tmp/coarse-review.log`. Do NOT kill the process because it looks stuck — it takes a genuine 10-25 minutes. When the log shows `REVIEW COMPLETE` or `PUBLISHED TO COARSE WEB`, it's done.

**When the run finishes, do NOT hunt across the filesystem for the review file.** `coarse-review` prints the authoritative paths in the final log lines:

```bash
rg '^  view:|^  local:' /tmp/coarse-review.log
```

- `local:` is the exact markdown path that was written, even if `uvx` used a temporary working directory.
- `view:` is the canonical coarse web URL in handoff mode.

If `view:` says `unavailable`, treat that as a callback failure and report only the local path. Do **not** try to discover another web URL, and do **not** run broad `find`, `locate`, `lsof`, or whole-computer searches trying to rediscover the output.

Available models: `claude-opus-4-6` (default), `claude-sonnet-4-6`, `claude-haiku-4-5`.
Available effort levels: `low`, `medium`, `high` (default), `max`.

If the user came from the coarse web form, they'll have a handoff URL instead. Run:

```bash
uvx --python 3.12 --from 'coarse-ink[mcp]==1.2.2' \
  coarse-review --detach --log-file /tmp/coarse-review.log \
  --handoff coarse.vercel.app/h/<token> --host claude [--model ...] [--effort ...]
```

This downloads the paper, runs the pipeline, and POSTs the final review back so it shows up at `coarse.vercel.app/review/<paper_id>`.

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
- Check progress via `tail -f /tmp/coarse-run.log` if stdout is redirected.
