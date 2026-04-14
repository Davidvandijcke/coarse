# Module Review for coarse

Focused code review of a single module (or all modules) against coarse's
11-point bug checklist. Use this when you want a thorough audit of one file
before a release, after a big refactor, or when you suspect a specific module
has drift.

This is the counterpart to `/architecture-review` — that one looks at how
modules fit together, this one looks at one module's internal quality.

## Arguments

`$ARGUMENTS`:
- `/module-review --module src/coarse/synthesis.py` — single module (default use)
- `/module-review --all` — walk every module in dependency order, ask before each
- `/module-review --changed` — only modules touched on this branch vs. `dev`
- `/module-review --review-only` — produce a report, no fixes

## The 11-point bug checklist

Every module is reviewed against these. Each violation is a finding with
severity CRITICAL / HIGH / MEDIUM / LOW.

1. **Model IDs only in `models.py`.** Any `"provider/name"` literal outside
   `src/coarse/models.py` is a violation of CLAUDE.md's hard rule.
2. **LLM calls go through `LLMClient`.** No direct `litellm.completion(...)`
   outside `src/coarse/llm.py`.
3. **Structured output uses `instructor` + Pydantic.** No raw JSON parsing
   of LLM responses outside `llm.py`.
4. **Prompts live in `prompts.py`.** Scattered prompt strings in agents or
   pipeline code is a violation.
5. **No `print()` in library code.** Library modules (everything the
   pipeline imports) must use `logging`. `print()` is only allowed in
   CLI entry-point modules that stream output directly to the user:
   `cli.py`, `cli_review.py`, `cli_attach.py`, and `headless_review.py`.
   Anywhere else is a violation.
6. **Every `.py` in `src/coarse/` has a matching `tests/test_{name}.py`.**
   Missing test file is a HIGH finding. Back-compat re-export shims
   (e.g. `claude_code_client.py`) still need a dedicated test that pins
   the forwarded symbols via `is`-identity.
7. **Context managers for resources.** `ThreadPoolExecutor`, file handles,
   `requests.Session` — all must use `with` statements.
8. **Cost tracking uses `LLMClient.cumulative_cost`.** No manual per-call
   cost arithmetic outside `llm.py`.
9. **API keys through `resolve_api_key()`.** Library modules that make
   LLM calls must go through `resolve_api_key()` — no bare
   `os.getenv("*_API_KEY")` / `os.environ[...]` reads in anything the
   pipeline imports. CLI entry modules (`cli.py`, `cli_review.py`,
   `headless_review.py`) may read or write `OPENROUTER_API_KEY` directly
   when bootstrapping subprocess children (env passthrough) or
   discovering a key before `config.py` is imported (the lightweight
   no-dep key lookup in `headless_review._find_openrouter_key`).
10. **OCR / extraction paths handle empty or garbled output.** `extraction.py`
    and `extraction_qa.py` must degrade gracefully, never raise on empty.
11. **Verbatim quotes pass `quote_verify.py`.** Every `DetailedComment`
    that reaches synthesis must have been run through
    `quote_verify.verify_quotes()`. The canonical call site is
    `review_stages._verify_with_fallback`, which wraps every agent
    stage that produces comments (section, proof_verify, editorial,
    crossref, critique). Individual agents **do not** call
    `verify_quotes` themselves — that's the pipeline wrapper's job. A
    new agent added outside the `review_stages` wrapper, or a new
    pipeline path that bypasses `_verify_with_fallback`, must run
    `verify_quotes` itself before returning or is a HIGH finding.

## Process

### Step 1: Select modules

If `$ARGUMENTS` contains `--module <path>`, target that one file.

If `--changed`:
```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && git diff dev...HEAD --name-only -- 'src/coarse/*.py'
```

If `--all`, list every `.py` under `src/coarse/` sorted by fan-in ascending
(review the most foundational modules first so later reviews can rely on
them being clean):
```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && find src/coarse -name '*.py' -not -name '__init__.py' -not -name '__main__.py'
```

Present the list to the user and confirm before proceeding if more than 3
modules are queued.

### Step 2: Per-module review loop

For each selected module, do this sequence. Stop the whole loop if the user
flags any step.

#### 2a. Read the module and its test

```
Read src/coarse/<module>.py
Read tests/test_<module>.py   # HIGH finding if missing
```

#### 2b. Run the 11-point checklist inline

Go through the checklist in order. For each item, state one of:
- `[OK]` — no violation found
- `[FINDING: <severity>] <file>:<line> <description>`

Don't delegate this to a subagent — you're the reviewer. The checklist is
concrete enough that you can apply it directly.

#### 2c. Run one specialized code-review agent for the subjective pass

Launch a single Agent (subagent_type: code-quality-reviewer) with:

```
Review <file>.py for:
  - Dead code (functions/classes never called, unused private helpers)
  - Duplicated logic that already exists elsewhere in the package
  - Overly complex functions (>80 lines without clear sub-sections)
  - Unclear variable names, confusing control flow
  - Missing type hints on public functions
  - Error messages that leak implementation details or API response bodies

Context: coarse's development rules from CLAUDE.md — simplicity first,
surgical changes, minimum code, no speculative abstractions.
```

#### 2d. Run module-specific tests

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && uv run pytest tests/test_<module>.py -v 2>&1 | tail -20
```

If any existing test fails, stop and report — something's broken before you
touched it.

#### 2e. Produce the plan

For each finding, decide one of:

| Decision | When |
|---|---|
| **AUTO-FIX** | Mechanical, safe, scoped to the file (e.g., `print` → `logger.info`, missing type hint, unused import, missing `with` on a file handle) |
| **PROPOSE** | Needs thought (e.g., deduplicating logic, splitting a function). Present to user, wait. |
| **ESCALATE** | Touches `types.py` / `models.py` / `pipeline.py` / `agents/base.py`, or breaks a public API. User decides. |
| **DEFER** | Real finding but out of scope for this review (e.g., pre-existing tech debt unrelated to the module's job). Note it, don't fix. |

#### 2f. Apply AUTO-FIXes

Apply every auto-fix in the module. After applying:

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && uv run pytest tests/test_<module>.py -v && uv run ruff check src/coarse/<module>.py && python3 scripts/security_scanner.py --scope model-ids
```

All three must pass. If any fails, revert the fix that broke it.

#### 2g. Report for this module

```
MODULE: src/coarse/<module>.py
  Tests:         <N passing / N total>
  Checklist:     <N OK>  <N findings>
  Agent review:  <N additional findings>

  Auto-fixed:    <list with file:line>
  Proposed:      <list with file:line + reasoning>
  Escalated:     <list — requires user decision>
  Deferred:      <list — noted for future>
```

Then either continue to the next module (if `--all`) or stop.

### Step 3: Final summary

After all queued modules are done (or the loop stops), present:

```
MODULE REVIEW — <branch>
Reviewed: <N> modules
Total findings: <N>
Auto-fixed: <N>
Still open: <N> (list with severities)

Next suggested action: <one sentence>
```

## Important notes

- **Don't touch files outside the module being reviewed** unless the finding
  is a cross-module auto-fix (e.g., `print()` in a helper that's called from
  the module under review). State the cross-file edit explicitly before making
  it.
- **Don't refactor pre-existing tech debt** the checklist turns up unless
  it's in scope for this module's review. Note it in `Deferred` and move on.
- **The 11-point checklist is the source of truth.** If you think a rule is
  wrong, update the checklist in this file in a separate PR — don't just
  skip it.
- **Commit after each module.** Conventional commit message with scope
  matching the module name: `fix(synthesis): apply module-review auto-fixes`.
