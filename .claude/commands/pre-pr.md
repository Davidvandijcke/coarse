# Pre-PR Checklist for coarse

Run this before creating a pull request. Security gate first, then parallel
review agents, then lint, tests, doc sync, and changelog.

Base branch is **`dev`**, not `main`. Release PRs from `dev` → `main` are
handled separately.

## Process

### Step 0: Security gate (BLOCKING)

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && python3 scripts/security_scanner.py
```

If the scanner reports any `CRITICAL` finding, **halt**. Print the finding,
tell the user the file and line, and propose a fix. Do not proceed to Step 1
until the finding is resolved.

`HIGH` and `MEDIUM` findings are reported but don't block (they surface in
the agent review later). To escalate `HIGH` to blocking for this run, use
`/pre-pr --strict`.

### Step 1: Identify what changed

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && git diff dev...HEAD --stat
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && git diff dev...HEAD
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && git log dev..HEAD --oneline
```

If the current branch is itself `dev` (we're preparing a release PR into
`main`), substitute `main` for `dev` in the commands above.

Use the diff output to identify all modified files. Pass this context to the
review agents in Step 2.

### Step 1.5: Doc-sync check

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && bash scripts/doc-sync-check.sh
```

If the script exits non-zero, fix the reported issues before proceeding:
- **Modules missing from CLAUDE.md**: add them to the package structure tree
- **Missing Unreleased section**: add `## Unreleased` near the top of `CHANGELOG.md`
- **Version mismatch**: align `pyproject.toml` and `src/coarse/__init__.py`
- **New model-ID literal**: move it to `src/coarse/models.py` and import the constant

Re-run `doc-sync-check.sh` until it exits 0.

### Step 2: Launch 5 parallel review agents

Launch ALL of these simultaneously using the Agent tool in one message. Pass
the full diff and file list to each so they have context.

**Agent 1: Architecture & Integration Review** (subagent_type: system-architect)
- Does the new code integrate cleanly with existing modules?
- Any hidden dependencies or circular imports?
- Follows coarse's patterns: `litellm` wrapper in `llm.py`, `instructor` structured output, prompts centralized in `prompts.py`?
- Any hardcoded model strings that should use `models.py` constants?
- Are module boundaries clean (`agents/` vs `pipeline.py` vs `synthesis.py`)?

**Agent 2: Code Quality & Style Review** (subagent_type: code-quality-reviewer)
- Variable/function names clear and consistent with the codebase?
- Duplicated logic between old and new code paths?
- Unused imports, variables, dead code introduced by the change?
- Error handling consistent with existing patterns?
- Is the code the minimum necessary to solve the problem (Karpathy principle)?

**Agent 3: Bug & Edge Case Review** (subagent_type: debugging-specialist)
- Unhandled None/empty values from LLM responses or PDF extraction?
- Resource cleanup handled (`ThreadPoolExecutor`, file handles)?
- LLM fallback paths correct (instructor parsing failures)?
- Any code path that could raise an unhandled exception?
- Cost tracking accumulations correct (cumulative vs. per-call)?

**Agent 4: Test Coverage Review** (subagent_type: test-engineer)
- Tests for every new code path?
- Edge cases covered (empty sections, missing API keys, malformed PDF, zero-token input)?
- Existing tests still cover the refactored code?
- Mock strategy matches existing patterns in `tests/`?
- Test data realistic?

**Agent 5: Security re-check on diff** (subagent_type: general-purpose)
- Run `python3 scripts/security_scanner.py --strict --json` and parse the output
- Cross-reference findings against the diff from Step 1 — do any NEW findings come from lines this branch introduced? (vs. pre-existing findings on `dev`)
- Check that no new `os.getenv("*_API_KEY")` call bypasses `resolve_api_key`
- Check that any new HTTP call uses HTTPS + has a timeout
- Check that any new prompt template separates system instructions from untrusted content

Report all findings back as: `[CRITICAL|HIGH|MEDIUM|LOW] file.py:line — description`.

### Step 3: Aggregate and prioritize

Collect all findings from the 5 agents plus Step 0 scanner output. Categorize:
- **Critical**: Bugs, data loss, security issues, crashes
- **High**: Missing tests, broken API contracts, hardcoded values, resource leaks, new security findings from Agent 5
- **Medium**: Style issues, missing docs, code duplication
- **Low**: Minor naming, comment quality

### Step 4: Fix Critical and High issues

Fix them directly. For Medium issues, fix if straightforward. For Low issues,
note them but skip unless trivial. If a Critical finding can't be auto-fixed
(e.g., requires a design decision), **stop and ask the user**.

### Step 5: Run lint

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && uv run ruff check src/ tests/
```

Fix errors in files you modified. Pre-existing errors in files you didn't
touch are out of scope — don't touch them (surgical changes rule).

### Step 6: Run tests

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && uv run pytest tests/ -v
```

All tests must pass. If any fail after fixes, fix them or revert the change
that broke them.

### Step 7: Version consistency

Verify `pyproject.toml` version matches `src/coarse/__init__.py` `__version__`.
On feature branches these should NOT change (version bumps happen only on
release PRs from `dev` to `main`).

### Step 8: Verify CHANGELOG.md

Check that `CHANGELOG.md` has an entry for this change under `## Unreleased`.
If not, add one. Format:

```markdown
### Added / Changed / Fixed
- **Short title** — One-sentence description (#PR)
```

### Step 9: Commit any fixes and doc changes

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && git add -A && git commit -m "chore: pre-pr review fixes and doc updates"
```

Skip this step if there's nothing new to commit.

### Step 10: Push and create PR

```bash
git push -u origin HEAD
```

Create the PR into `dev` with `gh pr create --base dev`. Include:
- Summary of changes (1-3 bullets)
- Test plan (what to verify manually, if anything)

### Step 11: Report

Output a summary table of review findings:
```
| Category | Found | Fixed | Remaining |
|----------|-------|-------|-----------|
| Critical | X     | X     | 0         |
| High     | X     | X     | 0         |
| Medium   | X     | X     | N         |
| Low      | X     | 0     | N         |
```

Then: security gate result (clean/findings), doc-sync result (OK/fixed),
what was checked, what was fixed, PR URL. List any remaining Medium/Low
items the developer should address manually.

## Important notes

- **Base branch is `dev`** for feature PRs. Only release PRs from `dev` to `main` use `main` as the base.
- **Step 0 is blocking** — a `CRITICAL` finding stops the pipeline. Use `--strict` to also block on `HIGH`.
- **Doc-sync is blocking** — fix or revert before continuing.
- **Don't touch unrelated files** during fix-up steps. The pre-PR review's job is to catch issues in the diff, not refactor the whole repo.
