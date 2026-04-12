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

- `coarse-ink` installed: `pip install 'coarse-ink[mcp] @ git+https://github.com/Davidvandijcke/coarse@feat/mcp-server'` (or `pip install 'coarse-ink[mcp]'` once released)
- **OpenRouter API key required** for Mistral OCR extraction (~$0.10 per paper). Before running the review, check if the key is available. If not, **ask the user** to provide it. Then either:
  - `export OPENROUTER_API_KEY=sk-or-v1-...` in the current shell, or
  - Create a `.env` file in the working directory with `OPENROUTER_API_KEY=sk-or-v1-...`
  - The key is NOT passed through the web handoff for security reasons.
- `claude` CLI logged in.

## How to run

**Get the paper path from the user.** PDF is most common but any coarse-supported format works.

**If they already have a pre-extracted markdown** (from a previous coarse run), pass it with `--pre-extracted` to skip OCR.

**Launch in the background** — full review takes 10-25 minutes:

```bash
coarse-review <paper_path> --host claude [--model claude-opus-4-6] [--effort high]
```

`run_in_background: true` in the Bash tool. Don't block the conversation on it.

Available models: `claude-opus-4-6` (default), `claude-sonnet-4-6`, `claude-haiku-4-5`.
Available effort levels: `low`, `medium`, `high` (default), `max`.

If the user came from the coarse web form, they'll have a handoff URL instead. Run:

```bash
coarse-review --handoff coarse.vercel.app/h/<token> --host claude [--model ...] [--effort ...]
```

This downloads the paper, runs the pipeline, and POSTs the final review back so it shows up at `coarse.vercel.app/review/<paper_id>`.

**When the script completes** (you'll be notified), read the output markdown and show the user:

- Output path
- Recommendation (accept / revise_and_resubmit / reject)
- Top 2-3 macro issues from the overall feedback section
- Total comment count
- If handoff mode: the `coarse.vercel.app/review/<id>` URL

## Notes

- The driver monkey-patches `coarse.llm.LLMClient` → `coarse.headless_clients.ClaudeCodeClient`, which spawns `claude -p` subprocesses for every pipeline LLM call.
- Host-CLI env vars (`CLAUDECODE`, `CLAUDE_CODE_ENTRYPOINT`, etc.) are stripped from the subprocess environment so nested sessions don't conflict with the parent.
- If a single `claude -p` call exceeds 30 minutes, it's killed and the pipeline continues without that section's comments.
- Check progress via `tail -f /tmp/coarse-run.log` if stdout is redirected.
