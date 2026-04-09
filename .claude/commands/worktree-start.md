# Start Worktree for coarse

Create a dedicated git worktree for a new feature or fix. Argument: GitHub issue number or description.

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

### 3. Ensure main is clean

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && git status && git pull origin main
```

### 4. Create worktree

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && git worktree add /private/tmp/coarse-<short-description> -b <branch-name>
```

### 5. Set up environment

```bash
cd /private/tmp/coarse-<short-description> && uv sync --extra dev
```

### 6. Output reminder

Print:
```
Worktree ready at: /private/tmp/coarse-<description>
Branch: <branch-name>
Issue: #<number>

Remember:
- Use full paths for Edit/Write: /private/tmp/coarse-<description>/...
- Run `uv run pytest tests/ -v` before committing
- Update CHANGELOG.md with your changes
- Use /pre-pr before creating the pull request
```
