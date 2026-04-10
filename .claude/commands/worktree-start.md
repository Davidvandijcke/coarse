# Start Worktree for coarse

Create a dedicated git worktree for a new feature or fix. Argument: GitHub
issue number or description. Worktrees live under `/private/tmp/` and branch
off `dev`, per CONTRIBUTING.md.

## Steps

### 1. Resolve the issue

If given a number, verify it exists:
```bash
gh issue view $ARGUMENTS
```
If no issue exists, create one:
```bash
gh issue create --title "<description>" --body "Created for worktree development"
```

### 2. Derive branch name

From the issue title, create a branch name:
- `feat/<issue-number>-<short-description>` for features
- `fix/<issue-number>-<short-description>` for bugs
- `docs/<issue-number>-<short-description>` for documentation
- `chore/<issue-number>-<short-description>` for tooling/CI

### 3. Ensure dev is clean and up to date

Feature branches live on `dev`, not `main` (see CONTRIBUTING.md).

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && git fetch origin dev && git status
```

### 4. Create worktree off dev

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && git worktree add /private/tmp/coarse-<issue-number>-<short-description> -b <branch-name> origin/dev
```

### 5. Set up environment

```bash
cd /private/tmp/coarse-<issue-number>-<short-description> && uv sync --extra dev
```

### 6. Output reminder

Print:
```
Worktree ready at: /private/tmp/coarse-<issue-number>-<description>
Branch: <branch-name> (tracking origin/dev)
Issue: #<number>

Remember:
- Use full paths for Edit/Write: /private/tmp/coarse-<issue-number>-<description>/...
- The shell cwd resets between Bash calls — prefix file-modifying commands with
  `cd /private/tmp/coarse-<issue-number>-<description> &&`
- Run `uv run pytest tests/ -v` before committing
- Update CHANGELOG.md under ## Unreleased with your changes
- Use /pre-pr before creating the pull request (Step 0 is a security gate)
- PR base branch is `dev`, not `main`: `gh pr create --base dev`
```
