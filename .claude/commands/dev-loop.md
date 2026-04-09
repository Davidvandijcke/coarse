# Development Loop

Supervise the autonomous development pipeline for coarse. You are the intelligent supervisor — you review each component spec before greenlighting implementation, catch design mistakes early, and only escalate to the user for major decisions.

## Arguments

`$ARGUMENTS` is passed as extra flags. Examples:
- `/dev-loop` — build all pending components with your supervision
- `/dev-loop --component types` — build one specific component
- `/dev-loop --dry-run` — preview the build order
- `/dev-loop --all` — fully autonomous (no supervision gates)
- `/dev-loop --plan-only` — spec one component and stop

## How it works

The script `scripts/dev_runner.py` does the mechanical work (running `claude -p` sessions for spec design, implementation, code review, PR creation, and merging). YOU are the supervisor who reviews each spec before implementation begins.

**Protocol:**
1. Script runs `--plan-only` → produces a component spec → exits with code 2
2. You read the spec JSON, evaluate it against CLAUDE.md and the reference review, and decide: approve, flag to user, or adjust
3. If approved, you run `--resume` → script continues with implementation → review → merge
4. Repeat for the next component

## Process

### Step 0: Setup check

Verify the project is ready:
```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && git status && head -5 docs/DEV_BACKLOG.md
```

### Step 1: Preview

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && env -u CLAUDECODE python3 scripts/dev_runner.py --dry-run --all $ARGUMENTS
```

Show the user the build order. If `$ARGUMENTS` contains `--dry-run`, stop here.

### Step 2: The supervision loop

If `$ARGUMENTS` contains `--all`, skip this loop — run fully autonomous:
```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && env -u CLAUDECODE python3 scripts/dev_runner.py --all $ARGUMENTS 2>&1
```

Otherwise, for each component, repeat this cycle:

#### 2a. Run spec phase

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && env -u CLAUDECODE python3 scripts/dev_runner.py --plan-only --skip-approval $ARGUMENTS 2>&1
```

Check the exit code:
- Exit 0 → component was trivial or already done. Move to next.
- Exit 2 → spec is ready for your review.
- Exit 1 → error. Read `.coarse/last_raw_output.txt` for debugging.

#### 2b. Review the spec

Read the state file and spec:
```bash
cat "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse/.coarse/dev_state.json"
```
Then read the spec JSON file pointed to by `spec_file`.

**Evaluate the spec against these criteria:**

1. **Does the public API make sense?** Check function signatures, parameter types, return types. Compare against what CLAUDE.md describes.
2. **Is it minimal?** No over-engineering, no speculative features, no unnecessary abstractions.
3. **Does it match the reference review format?** For agents/synthesis/prompts, verify the spec will produce output matching `data/refine_examples/r3d/feedback-...md`.
4. **Are the tests comprehensive?** Should cover happy path, edge cases, error handling.
5. **Are dependencies correct?** Does it import from the right already-built modules?
6. **Any concerns the spec raises?** Read the "concerns" field — are they blockers?

**Your decision:**
- **APPROVE**: Spec looks correct and well-scoped. Proceed to implementation.
- **FLAG**: Something is wrong or risky. Stop the loop and tell the user. Show them the spec and your concerns. Let them decide.
- **ADJUST**: Minor issues you can fix by modifying the spec JSON before resuming. Edit the spec file, then resume.

#### 2c. Implement (if approved)

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && env -u CLAUDECODE python3 scripts/dev_runner.py --resume $ARGUMENTS 2>&1
```

This runs: implement in worktree → create PR → review PR → merge → update backlog.

Monitor the output. If implementation fails:
1. Read the error output
2. Check if the worktree exists: `ls /private/tmp/coarse-*/`
3. Decide: retry, fix manually, or flag to user

#### 2d. Verify and continue

After merge, verify the component landed:
```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && git log --oneline -3 && cat docs/DEV_BACKLOG.md | grep -E "^\|"
```

Then loop back to 2a for the next component.

### Step 3: Report

When all components are done, report to the user:
- Components built successfully (with PR numbers)
- Any components that needed manual intervention
- Total cost estimate (from spec _meta fields)
- Next steps (usually: run the pipeline end-to-end on the reference paper)

List all specs for reference:
```bash
ls -la "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse/.coarse/specs/" 2>/dev/null
```

## Supervisor judgment calls

**When to APPROVE without hesitation:**
- Types, config, extraction — these are mechanical, low-risk
- Agents that follow the established base class pattern
- Tests that cover the public API

**When to look more carefully:**
- Prompts (prompts.py) — these directly determine review quality. Compare against the reference review's style, depth, and format. Bad prompts = bad product.
- Synthesis — must exactly reproduce refine.ink format. Diff against the reference.
- Pipeline orchestration — must wire everything correctly, handle errors gracefully.
- CLI — user-facing, must handle edge cases (no API key, bad PDF, etc.)

**When to FLAG to user:**
- Spec proposes adding a dependency not in pyproject.toml
- Spec changes the public API of an already-built component
- Implementation repeatedly fails (>2 attempts)
- Cost estimate for a single component exceeds $5

## Important notes

- You MUST prefix all script commands with `cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" &&`
- You MUST use `env -u CLAUDECODE` for all script invocations — the script spawns nested `claude -p` sessions.
- Each `claude -p` phase has a 15-minute timeout.
- If the script fails, read `.coarse/last_raw_output.txt` or `.coarse/last_raw_result.txt`.
- The `--plan-only` / `--resume` protocol communicates via `.coarse/dev_state.json`.
- Component #1 (Project setup) is already done — mark it before starting.
