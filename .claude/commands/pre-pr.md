# Pre-PR Checklist for coarse

Run this before creating a pull request. Reviews code in parallel, fixes issues, ensures tests pass, docs are current, and changelog is updated.

## Steps

### Step 1: Identify what changed

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && git diff main...HEAD --stat
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && git diff main...HEAD
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && git log main..HEAD --oneline
```

Use the diff output to identify all modified files. This context is needed for the review agents.

### Step 2: Launch 5 parallel review agents

Launch ALL of these simultaneously using the Agent tool. Pass the full diff and file list to each agent so they have context.

**Agent 1: Architecture & Integration Review** (subagent_type: system-architect)
- Does the new code integrate cleanly with existing modules?
- Are there hidden dependencies or circular imports?
- Does it follow coarse's patterns: litellm wrapper in llm.py, instructor structured output, Docling extraction, prompts centralized in prompts.py?
- Are there hardcoded model strings that should use config.py defaults?
- Are module boundaries clean (agents/ vs pipeline.py vs synthesis.py)?

**Agent 2: Code Quality & Style Review** (subagent_type: code-quality-reviewer)
- Are variable/function names clear and consistent with the codebase?
- Is there duplicated logic between old and new code paths?
- Are there unused imports, variables, or dead code introduced by the change?
- Is error handling consistent with existing patterns?
- Is the code the minimum necessary to solve the problem (Karpathy principle: simplicity first)?

**Agent 3: Bug & Edge Case Review** (subagent_type: debugging-specialist)
- Are there unhandled None/empty values from LLM responses or PDF extraction?
- Is resource cleanup handled properly (ThreadPoolExecutor, file handles)?
- Are LLM fallback paths correct (e.g., when instructor parsing fails)?
- Could any code path raise an unhandled exception?
- Are cost tracking accumulations correct (cumulative vs per-call)?

**Agent 4: Test Coverage Review** (subagent_type: test-engineer)
- Are there tests for every new code path?
- Are edge cases covered (empty sections, missing API keys, malformed PDF, zero-token input)?
- Do existing tests still cover the refactored code?
- Does the mock strategy match existing patterns in tests/?
- Is test data realistic?

**Agent 5: Documentation & API Review** (subagent_type: technical-documentation-writer)
- Are docstrings updated for changed functions?
- Are new CLI flags documented in cli.py help text?
- Are there stale comments referencing old behavior?
- Is CLAUDE.md current (package structure, types, architecture)?
- Are prompt templates in prompts.py properly documented?

### Step 3: Aggregate and prioritize

Collect all findings from the 5 agents and categorize:
- **Critical**: Bugs, data loss, security issues, crashes
- **High**: Missing tests, broken API contracts, hardcoded values, resource leaks
- **Medium**: Style issues, missing docs, code duplication
- **Low**: Minor naming, comment quality

### Step 4: Fix Critical and High issues

Fix them directly. For Medium issues, fix if straightforward. For Low issues, note them but skip unless trivial.

### Step 5: Run lint

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && uv run ruff check src/ tests/
```
Fix any errors. Warnings are acceptable.

### Step 6: Run tests

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && uv run pytest tests/ -v
```
All tests must pass. If any fail after fixes, fix them.

### Step 7: Version consistency

Verify `pyproject.toml` version matches `src/coarse/__init__.py` `__version__`.

### Step 8: Verify CHANGELOG.md

Check that CHANGELOG.md has an entry for this change under `[Unreleased]` or the current version section. If not, add one. Format:

```markdown
### Added / Changed / Fixed
- **Short title** — One-sentence description (#PR)
```

### Step 9: Commit any fixes and doc changes

```bash
git add -A
git commit -m "chore: pre-pr review fixes and doc updates"
```

### Step 10: Push and create PR

```bash
git push -u origin HEAD
```

Create the PR with `gh pr create`. Include:
- Summary of changes (1-3 bullets)
- Test plan

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

Then: what was checked, what was fixed, PR URL. List any remaining Medium/Low items the developer should address manually.
