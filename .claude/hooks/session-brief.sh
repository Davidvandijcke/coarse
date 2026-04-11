#!/usr/bin/env bash
# SessionStart hook: injects a mandatory onboarding brief at the top of every
# new Claude Code session in this repo. Wired in .claude/settings.json.
#
# The hook prints to stdout; Claude Code captures that output as additional
# session context. Nothing here runs against the user's message yet — this
# is about giving Claude a working mental model of coarse before it takes
# its first action.
#
# Edit this script to adjust the mandatory-reading list as the codebase
# evolves. Keep it short: the goal is "enough to understand", not "read
# everything".

set -euo pipefail

cat <<'BRIEF'
# Session brief — coarse

This repo is `coarse`, a free open-source AI academic paper reviewer (BYOK).
Before responding to the user's first message, you MUST read the files listed
under "Required" below so you have a working model of the codebase. This is
a hard requirement, not a suggestion — the rest of the project assumes you've
seen these files.

## Required reading (do these first, in order)

1. `CLAUDE.md` — project overview, pipeline diagram, package structure,
   slash commands, worktree discipline, model manifest rules, development
   principles. Everything else in the repo assumes you know this.
2. `CONTRIBUTING.md` — git workflow (dev/main split), pre-PR checklist,
   branch naming, versioning, release process, security reporting.
3. `src/coarse/__init__.py` — the public Python API surface.
4. `src/coarse/types.py` — Pydantic models that are the vocabulary of the
   whole pipeline (`PaperText`, `PaperStructure`, `SectionInfo`, `Review`,
   `DetailedComment`, etc.). You cannot reason about the code without these.
5. `src/coarse/models.py` — single source of truth for every model ID.
   NEVER write a model ID string literal outside this file.
6. `src/coarse/pipeline.py` — `review_paper()` orchestrator, i.e. the main
   control flow the whole project hangs off.

## Skim (run `ls` or glance, don't deep-read)

7. `src/coarse/` — top-level module names
8. `src/coarse/agents/` — agent module names (one file per agent class)
9. `tests/` — test file names (tests mirror modules 1:1)
10. `.claude/commands/` — available slash commands (`/pre-pr`,
    `/security-review`, `/architecture-review`, `/module-review`,
    `/dev-loop`, `/worktree-start`)

## Read on demand (only if the user's task touches the area)

| Area                        | File(s) to read                                    |
|-----------------------------|----------------------------------------------------|
| PDF / OCR / extraction      | `src/coarse/extraction.py`, `extraction_qa.py`     |
| Section parsing / structure | `src/coarse/structure.py`                          |
| A specific agent            | `src/coarse/agents/<name>.py` + `tests/test_<name>.py` |
| LLM provider routing / cost | `src/coarse/llm.py`                                |
| CLI behaviour               | `src/coarse/cli.py`                                |
| Prompt templates            | `src/coarse/prompts.py` (~1700 lines — grep, don't linear-read) |
| Quote verification          | `src/coarse/quote_verify.py`                       |
| Output format               | `src/coarse/synthesis.py`, `data/refine_examples/r3d/feedback-*.md` |
| Config / API keys           | `src/coarse/config.py`                             |
| Web frontend / submission   | `web/`                                             |
| Modal deploy / worker       | `deploy/modal_worker.py`                           |
| Security scanner            | `scripts/security_scanner.py`, `tests/test_security.py` |

## Hard rules (from CLAUDE.md — re-stated so you don't miss them)

- **Model IDs live in `src/coarse/models.py` only.** Import constants, never
  hardcode the string anywhere else. `/security-review` enforces this.
- **Prompts live in `src/coarse/prompts.py` only.** Don't scatter prompt
  strings across agents.
- **LLM calls go through `LLMClient`** (wraps litellm + instructor). No
  direct `litellm.completion(...)` outside `src/coarse/llm.py`.
- **Structured output uses `instructor` + Pydantic.** No raw JSON parsing
  of LLM responses outside `llm.py`.
- **Worktree discipline** for any non-trivial change: branch off `dev` in
  `/private/tmp/coarse-<issue>-<slug>/`, use full paths on every Edit/Write,
  prefix file-modifying Bash with `cd /private/tmp/coarse-<slug> &&`.
- **Feature PRs target `dev`**, not `main`. Release PRs from `dev` to `main`
  are the maintainer's job.
- **Before pushing**, run `/pre-pr` (or at minimum `make security &&
  make check`).

## What to do after reading

Reply to the user's first message normally. Do NOT recite what you read —
one sentence acknowledging you have the context is enough. Then answer
their actual question.

If the user's first message is a trivial question that doesn't require
codebase knowledge (e.g. "what time is it", "help"), skip steps 3–6 but
still read 1 and 2.
BRIEF
