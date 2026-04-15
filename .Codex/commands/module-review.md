# Module Review for coarse (Codex)

Focused code review of one module or a recent set of modules against coarse's
11-point bug checklist. Use this when you want a tight module-level audit
before a release, after a refactor, or when a file looks risky.

This is the module-level counterpart to `/architecture-review`.

## Arguments

`$ARGUMENTS`:
- `/module-review --module src/coarse/synthesis.py` — review one module
- `/module-review --changed` — review recently changed coarse modules
- `/module-review --all` — review every `src/coarse/*.py` module in dependency order
- `/module-review --review-only` — report findings only, do not edit

## The 11-point bug checklist

Every module is reviewed against these rules. Record each result as either:
- `[OK]`
- `[FINDING: <severity>] <file>:<line> <description>`

1. **Model IDs only in `models.py`.** Any `"provider/name"` literal outside
   `src/coarse/models.py` is a violation.
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
6. **Every `.py` in `src/coarse/` has a matching `tests/test_{name}.py`.**
   Missing test file is a HIGH finding. Back-compat re-export shims
   (e.g. `claude_code_client.py`) still need a dedicated test that pins
   the forwarded symbols via `is`-identity.
7. **Context managers for resources.** `ThreadPoolExecutor`, file handles, and
   sessions must use `with`.
8. **Cost tracking uses `LLMClient.cost_usd` / `add_cost()`.** No manual
   per-call cost arithmetic outside `llm.py`.
9. **API keys through `resolve_api_key()`.** Library modules that make
   LLM calls must go through `resolve_api_key()` — no bare
   `os.getenv("*_API_KEY")` / `os.environ[...]` reads in anything the
   pipeline imports. CLI entry modules (`cli.py`, `cli_review.py`,
   `headless_review.py`) may read or write `OPENROUTER_API_KEY`
   directly when bootstrapping subprocess children (env passthrough)
   or discovering a key before `config.py` is imported (the lightweight
   no-dep key lookup in `headless_review._find_openrouter_key`).
10. **OCR / extraction paths handle empty or garbled output.** Extraction code
    must degrade gracefully on empty content.
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

### 1. Select modules

If `$ARGUMENTS` contains `--module <path>`, target that file.

If `$ARGUMENTS` contains `--changed`, prefer these sources in order:

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && \
git diff --name-only origin/dev...HEAD -- 'src/coarse/*.py' 'src/coarse/**/*.py'
```

If that is empty because the current branch is `dev`, fall back to a recent
window:

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && \
git diff --name-only HEAD~20..HEAD -- 'src/coarse/*.py' 'src/coarse/**/*.py'
```

If `$ARGUMENTS` contains `--all`, enumerate:

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && \
find src/coarse -name '*.py' -not -name '__init__.py' -not -name '__main__.py' | sort
```

When more than 3 modules are queued, show the queue to the user and confirm
before proceeding. Prefer the recently changed modules that are central to the
pipeline first: `pipeline.py`, `extraction.py`, `prompts.py`, `structure.py`,
`llm.py`, then changed agents.

### 2. Per-module review loop

For each module:

#### 2a. Read the module and its tests

Read:
- `src/coarse/<module>.py`
- the matching test file(s) under `tests/`

Do not assume the test is always named `tests/test_<module>.py` in this repo.
Resolve tests in this order:

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && \
basename="<module-basename-without-.py>" && \
rg --files tests | rg "test_(${basename}|${basename//_/-}|${basename//-/_})([-_].+)?\\.py$"
```

Examples:
- `section.py` → `tests/test_section.py`
- `structure.py` → `tests/test_structure.py`
- `cost.py` → `tests/test_cost.py`

If no plausible test file exists, record a HIGH finding and continue.

#### 2b. Apply the 11-point checklist inline

Review the file directly. Do not delegate the checklist.

#### 2c. Run a subjective review pass

Do an additional code-review pass for:
- Dead code
- Duplicated logic already present elsewhere in the package
- Overly complex functions
- Confusing control flow or poor names
- Missing type hints on public functions
- Error messages that leak provider internals or raw API payloads

This subjective pass is still done locally by Codex. Do not hand it off to a
subagent.

#### 2d. Run module-specific tests

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && \
uv run pytest <resolved-test-paths> -v
```

If no matching test file exists, note that explicitly instead of fabricating one.

#### 2e. Classify findings

For each finding choose one:
- **AUTO-FIX**: mechanical, safe, scoped
- **PROPOSE**: needs design judgment
- **ESCALATE**: touches `types.py`, `models.py`, `pipeline.py`, `agents/base.py`,
  or changes a public API
- **DEFER**: valid but out of scope for this review

#### 2f. Apply auto-fixes unless `--review-only`

Before editing, move to a dedicated worktree under `/private/tmp/` and use
full paths for every edit.

After each auto-fix, verify with:

```bash
cd /private/tmp/coarse-<slug> && \
uv run pytest <resolved-test-paths> -v && \
uv run ruff check src/coarse/<module>.py && \
python3 scripts/security_scanner.py --scope model-ids
```

If a fix breaks verification, revert that fix only.

#### 2g. Report the module

Use this shape:

```text
MODULE: src/coarse/<module>.py
  Tests:         <status>
  Checklist:     <N OK>  <N findings>
  Subjective:    <N additional findings>

  Auto-fixed:    <list or none>
  Proposed:      <list or none>
  Escalated:     <list or none>
  Deferred:      <list or none>
```

### 3. Final summary

After the queue is done:

```text
MODULE REVIEW — <branch>
Reviewed: <N> modules
Total findings: <N>
Auto-fixed: <N>
Still open: <N> (list with severities)

Next suggested action: <one sentence>
```

## Important notes

- Keep the review focused on the target module; do not broaden scope unless a
  finding requires a clearly related cross-file fix.
- Treat the 11-point checklist as the source of truth.
- If you make edits, commit per module with a conventional commit scoped to the
  module, for example: `fix(extraction): apply module-review auto-fixes`.
