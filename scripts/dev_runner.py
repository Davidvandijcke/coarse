#!/usr/bin/env python3
"""Autonomous development pipeline for coarse.

Parses docs/DEV_BACKLOG.md, picks the next pending component, and runs
a 5-phase pipeline: spec → supervisor gate → implement → review → merge.

Each phase is a separate `claude -p` invocation with appropriate tool
restrictions. The script orchestrates the phases and manages git state.

Usage:
    python scripts/dev_runner.py --all                    # build ALL components (autonomous)
    python scripts/dev_runner.py --plan-only              # spec phase only, then pause (exit 2)
    python scripts/dev_runner.py --resume                 # continue from implement after approval
    python scripts/dev_runner.py                          # next component only (full pipeline)
    python scripts/dev_runner.py --component types        # specific component by name
    python scripts/dev_runner.py --dry-run                # preview only

Exit codes:
    0 = success
    1 = error
    2 = spec ready, waiting for supervisor approval (--plan-only)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKLOG_PATH = REPO_ROOT / "docs" / "DEV_BACKLOG.md"
STATE_DIR = REPO_ROOT / ".coarse"
STATE_FILE = STATE_DIR / "dev_state.json"
SPECS_DIR = REPO_ROOT / ".coarse" / "specs"
DEFAULT_MODEL = "sonnet"
PHASE_TIMEOUT = 900  # 15 minutes per phase

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_NEEDS_APPROVAL = 2


class PipelineError(Exception):
    """Non-fatal error in a single component's pipeline."""


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class ComponentEntry:
    """A row from the backlog table."""

    number: int
    name: str
    status: str  # "pending", "done", "in_progress"
    files: str
    deps: str
    description: str
    dep_numbers: list[int] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Backlog parsing
# ---------------------------------------------------------------------------

ROW_RE = re.compile(
    r"^\|\s*(\d+)\s*\|"       # component number
    r"\s*(.*?)\s*\|"           # component name
    r"\s*(.*?)\s*\|"           # status
    r"\s*(.*?)\s*\|"           # files
    r"\s*(.*?)\s*\|"           # deps
    r"\s*(.*?)\s*\|",          # description
)


def parse_backlog(path: Path) -> list[ComponentEntry]:
    """Parse DEV_BACKLOG.md and return all component entries."""
    text = path.read_text()
    entries: list[ComponentEntry] = []

    for line in text.splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue

        num, name, status, files, deps, desc = (g.strip() for g in m.groups())

        # Skip header row
        try:
            num_int = int(num)
        except ValueError:
            continue

        # Parse dependency numbers
        dep_numbers = []
        if deps and deps != "—" and deps != "-":
            for d in re.findall(r"\d+", deps):
                dep_numbers.append(int(d))

        entries.append(ComponentEntry(
            number=num_int,
            name=name,
            status=status.lower().strip(),
            files=files,
            deps=deps,
            description=desc,
            dep_numbers=dep_numbers,
        ))

    return entries


def get_next_component(
    entries: list[ComponentEntry],
    override: str | None = None,
) -> ComponentEntry | None:
    """Get the next buildable component (deps satisfied, status=pending)."""
    if override:
        for e in entries:
            if e.name.lower() == override.lower() or str(e.number) == override:
                return e
        return None

    done_numbers = {e.number for e in entries if e.status == "done"}

    for e in sorted(entries, key=lambda x: x.number):
        if e.status != "pending":
            continue
        # Check all deps are done
        if all(d in done_numbers for d in e.dep_numbers):
            return e

    return None


# ---------------------------------------------------------------------------
# Backlog updates
# ---------------------------------------------------------------------------


def update_backlog_status(name: str, new_status: str) -> None:
    """Update a component's status in DEV_BACKLOG.md."""
    text = BACKLOG_PATH.read_text()
    escaped = re.escape(name)
    # Match the status cell for this component name
    pattern = re.compile(
        rf"(\|\s*\d+\s*\|\s*{escaped}\s*\|\s*)(pending|done|in_progress)(\s*\|)",
        re.IGNORECASE,
    )
    m = pattern.search(text)
    if m:
        text = text[:m.start(2)] + new_status + text[m.end(2):]
        BACKLOG_PATH.write_text(text)


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def git(*args: str, cwd: Path | None = None, check: bool = True) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        cwd=str(cwd or REPO_ROOT),
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def current_branch(cwd: Path | None = None) -> str:
    return git("branch", "--show-current", cwd=cwd)


def create_worktree(component: ComponentEntry) -> tuple[Path, str]:
    """Create a git worktree for this component. Returns (path, branch_name)."""
    safe_name = component.name.lower().replace(" ", "-")
    worktree_path = Path(f"/private/tmp/coarse-{safe_name}")
    branch_name = f"feat/{component.number}-{safe_name}"

    if worktree_path.exists():
        git("worktree", "remove", str(worktree_path), check=False)

    git("worktree", "add", str(worktree_path), "-b", branch_name)
    print(f"  Worktree: {worktree_path} (branch: {branch_name})")

    # Install deps
    subprocess.run(
        ["uv", "sync", "--all-extras"],
        cwd=str(worktree_path),
        capture_output=True,
        text=True,
    )
    return worktree_path, branch_name


# ---------------------------------------------------------------------------
# claude -p helpers
# ---------------------------------------------------------------------------


def _claude_env() -> dict[str, str]:
    """Return env with CLAUDECODE removed to allow nested invocation."""
    env = os.environ.copy()
    env.pop("CLAUDECODE", None)
    return env


def run_claude(
    prompt: str,
    *,
    allowed_tools: str,
    model: str,
    system_append: str = "",
    cwd: Path | None = None,
    timeout: int = PHASE_TIMEOUT,
) -> dict:
    """Invoke claude -p and return the parsed JSON envelope."""
    cmd = [
        "claude",
        "-p",
        prompt,
        "--allowed-tools",
        allowed_tools,
        "--output-format",
        "json",
        "--model",
        model,
    ]
    if system_append:
        cmd.extend(["--append-system-prompt", system_append])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=_claude_env(),
        cwd=str(cwd or REPO_ROOT),
        timeout=timeout,
    )

    if result.returncode != 0:
        msg = f"claude exited {result.returncode}"
        if result.stderr:
            msg += f": {result.stderr[:500]}"
        raise PipelineError(msg)

    stdout = result.stdout.strip()
    if not stdout:
        raise PipelineError("claude produced no output")

    try:
        envelope = json.loads(stdout)
    except json.JSONDecodeError:
        try:
            arr = json.loads(stdout)
            if isinstance(arr, list):
                envelope = arr[-1] if arr else {}
            else:
                raise
        except (json.JSONDecodeError, TypeError):
            raw_path = STATE_DIR / "last_raw_output.txt"
            STATE_DIR.mkdir(parents=True, exist_ok=True)
            raw_path.write_text(stdout)
            raise PipelineError(f"Could not parse claude JSON. Raw saved to {raw_path}")

    return envelope


def extract_result_text(envelope: dict) -> str:
    """Get the result text from the claude JSON envelope."""
    return envelope.get("result", "")


def parse_json_from_text(text: str) -> dict:
    """Parse JSON from claude's result text, stripping markdown fences."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", text)
    cleaned = re.sub(r"\n?\s*```\s*$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    m = re.search(r"\{[\s\S]*\}", cleaned)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass

    raw_path = STATE_DIR / "last_raw_result.txt"
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(text)
    raise PipelineError(f"Could not parse structured JSON. Raw saved to {raw_path}")


# ---------------------------------------------------------------------------
# Phase 1: Spec
# ---------------------------------------------------------------------------


def build_spec_prompt(component: ComponentEntry, entries: list[ComponentEntry]) -> str:
    """Build a prompt that asks Claude to spec out a component."""
    # Gather info about already-built deps
    done = [e for e in entries if e.status == "done"]
    done_summary = "\n".join(
        f"  - #{e.number} {e.name}: {e.files}" for e in done
    ) or "  (none yet)"

    return textwrap.dedent(f"""\
        You are designing component #{component.number} "{component.name}" for `coarse`,
        a free open-source AI academic paper reviewer.

        ## Component Info
        - **Number**: {component.number}
        - **Name**: {component.name}
        - **Files**: {component.files}
        - **Dependencies**: {component.deps}
        - **Description**: {component.description}

        ## Already Built
        {done_summary}

        ## Task
        1. Read CLAUDE.md to understand the project architecture and output format.
        2. Read the reference review at `data/refine_examples/r3d/feedback-regression-discontinuity-design-with-distribution--2026-03-03.md` to understand the target output.
        3. If any dependency files exist (listed above), read them to understand the interfaces.
        4. Read pyproject.toml to understand the package structure and dependencies.

        Design a detailed spec for this component. Include:
        - Public API (function/class signatures with types)
        - Internal implementation approach
        - Key design decisions
        - Test plan (what to test, edge cases)
        - Any concerns or open questions

        ## Output
        Return ONLY a JSON object (no markdown fences):
        {{{{
            "component": "{component.name}",
            "files": ["{component.files}"],
            "public_api": [
                {{{{
                    "name": "<function_or_class>",
                    "signature": "<full signature>",
                    "description": "<what it does>"
                }}}}
            ],
            "implementation_notes": "<paragraph describing approach>",
            "test_plan": [
                {{{{
                    "test_name": "<test function name>",
                    "description": "<what it verifies>"
                }}}}
            ],
            "concerns": ["<any open questions or risks>"],
            "estimated_lines": <int>
        }}}}
    """)


SPEC_SYSTEM = (
    "You are a senior software architect. Output ONLY valid JSON matching the schema. "
    "No markdown fences. No text outside the JSON. "
    "Read all relevant files before designing. Keep the design minimal and practical. "
    "Do not over-engineer."
)


def run_spec(
    component: ComponentEntry,
    entries: list[ComponentEntry],
    model: str,
) -> dict:
    """Phase 1: design the component spec (read-only)."""
    print(f"\n--- Phase 1: Spec ({component.name}) ---")
    prompt = build_spec_prompt(component, entries)
    envelope = run_claude(
        prompt,
        allowed_tools="Read,Grep,Glob",
        model=model,
        system_append=SPEC_SYSTEM,
    )
    result_text = extract_result_text(envelope)
    spec = parse_json_from_text(result_text)
    spec["_meta"] = {
        "phase": "spec",
        "model": model,
        "cost_usd": envelope.get("total_cost_usd"),
    }
    return spec


# ---------------------------------------------------------------------------
# Phase 2: Implement (in worktree)
# ---------------------------------------------------------------------------


def build_implement_prompt(
    component: ComponentEntry,
    spec: dict,
    branch_name: str,
    worktree_path: Path,
) -> str:
    spec_json = json.dumps(spec, indent=2, default=str)
    safe_name = component.name.lower().replace(" ", "-")

    return textwrap.dedent(f"""\
        You are implementing component #{component.number} "{component.name}" for `coarse`,
        a free open-source AI academic paper reviewer.

        You are in a git worktree at `{worktree_path}` on branch `{branch_name}`.

        ## Component Spec
        ```json
        {spec_json}
        ```

        ## Task
        1. Read CLAUDE.md for project rules and architecture.
        2. Read any existing source files in `src/coarse/` that this component depends on.
        3. Read the reference review at `data/refine_examples/r3d/feedback-regression-discontinuity-design-with-distribution--2026-03-03.md`
           if this component produces output (prompts, synthesis, agents).
        4. Implement the component according to the spec above.
        5. Write tests in `tests/test_{safe_name}.py`.
        6. Run `uv run pytest tests/ -v` and fix any failures.
        7. Run `uv run ruff check src/coarse/` and fix lint errors.

        ## Commit & PR
        After all tests pass:
        1. `git add` only the files you created/modified.
        2. Commit: `feat(coarse): add {component.name} (#{component.number})`
           Include `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`.
        3. Push: `git push -u origin {branch_name}`
        4. Create PR:
           ```
           gh pr create --title "feat(coarse): add {component.name} (#{component.number})" \\
             --body "## Summary\\nImplement {component.name}: {component.description}\\n\\n## Test plan\\n- [ ] All tests pass\\n\\nGenerated with Claude Code"
           ```

        ## Rules
        - Implement ONLY what the spec describes. No extras.
        - All paths must be absolute (using the worktree path) for Edit/Write.
        - Every Bash command must `cd {worktree_path} &&` first.
        - Match the coding style of any existing files.
        - Use `instructor` for structured LLM output, `litellm` for completions.
        - All prompt templates go in `prompts.py`, not in agent files.

        ## Output
        When done, return ONLY a JSON object:
        {{{{
            "pr_number": <int>,
            "pr_url": "<url>",
            "files_created": ["<path>", ...],
            "files_modified": ["<path>", ...],
            "tests_passed": true | false,
            "test_count": <int>
        }}}}
    """)


IMPLEMENT_SYSTEM = (
    "You are a senior Python developer. Follow the spec exactly. "
    "Write clean, minimal code. Write thorough tests. "
    "Run tests before committing. Output ONLY JSON at the end. "
    "IMPORTANT: use absolute worktree paths for all file operations."
)


def run_implement(
    component: ComponentEntry,
    spec: dict,
    model: str,
) -> tuple[dict, Path]:
    """Phase 2: implement in a worktree, create PR."""
    print(f"\n--- Phase 2: Implement ({component.name}) ---")
    worktree_path, branch_name = create_worktree(component)

    prompt = build_implement_prompt(component, spec, branch_name, worktree_path)
    envelope = run_claude(
        prompt,
        allowed_tools="Read,Grep,Glob,Edit,Write,Bash",
        model=model,
        system_append=IMPLEMENT_SYSTEM,
        cwd=worktree_path,
        timeout=PHASE_TIMEOUT,
    )
    result_text = extract_result_text(envelope)
    result = parse_json_from_text(result_text)
    result["_meta"] = {
        "phase": "implement",
        "model": model,
        "cost_usd": envelope.get("total_cost_usd"),
        "worktree": str(worktree_path),
        "branch": branch_name,
    }
    return result, worktree_path


# ---------------------------------------------------------------------------
# Phase 3: Review PR
# ---------------------------------------------------------------------------


def build_review_prompt(pr_number: int, component: ComponentEntry) -> str:
    return textwrap.dedent(f"""\
        You are reviewing PR #{pr_number} which implements component #{component.number}
        "{component.name}" for the `coarse` package.

        ## Steps
        1. Run `gh pr diff {pr_number}` to see the changes.
        2. Run `gh pr view {pr_number}` to see the PR description.
        3. Read the changed files to understand context.
        4. Read CLAUDE.md for project conventions.
        5. Check that:
           - Code matches the described spec
           - Tests cover the public API
           - No unnecessary complexity or over-engineering
           - Prompts (if any) are in prompts.py
           - Types (if any) match types.py conventions
           - No hardcoded model names outside config.py
           - Code is clean and minimal

        ## Bash Restrictions
        You may ONLY use Bash for: `gh pr diff`, `gh pr view`, `git log`, `git diff`,
        `uv run pytest`, `uv run ruff check`.

        ## Output
        Return ONLY a JSON object:
        {{{{
            "verdict": "approve" | "request_changes",
            "comments": ["<comment>", ...],
            "summary": "<1-2 sentence assessment>"
        }}}}
    """)


REVIEW_SYSTEM = (
    "You are a code reviewer. Be thorough but pragmatic. "
    "Output ONLY valid JSON. Approve if the code is correct, tested, and minimal. "
    "Request changes only for real bugs or missing tests, not style preferences."
)


def run_review(pr_number: int, component: ComponentEntry, model: str) -> dict:
    """Phase 3: review the PR."""
    print(f"\n--- Phase 3: Review PR #{pr_number} ({component.name}) ---")
    prompt = build_review_prompt(pr_number, component)
    envelope = run_claude(
        prompt,
        allowed_tools="Read,Grep,Glob,Bash",
        model=model,
        system_append=REVIEW_SYSTEM,
    )
    result_text = extract_result_text(envelope)
    review = parse_json_from_text(result_text)
    review["_meta"] = {
        "phase": "review",
        "model": model,
        "cost_usd": envelope.get("total_cost_usd"),
    }
    return review


# ---------------------------------------------------------------------------
# Phase 4: Merge
# ---------------------------------------------------------------------------


def merge_pr(pr_number: int, component: ComponentEntry, worktree_path: Path) -> None:
    """Merge PR and clean up."""
    print(f"\n--- Phase 4: Merge PR #{pr_number} ---")

    subprocess.run(
        ["gh", "pr", "merge", str(pr_number), "--squash"],
        cwd=str(REPO_ROOT),
        check=True,
    )
    print(f"  PR #{pr_number} merged.")

    git("pull", "origin", "main")
    print("  Pulled main.")

    git("worktree", "remove", str(worktree_path), check=False)
    print(f"  Removed worktree: {worktree_path}")

    update_backlog_status(component.name, "done")
    git("add", str(BACKLOG_PATH))
    git(
        "commit", "-m",
        f"chore: mark {component.name} as done in backlog",
        check=False,
    )
    print(f"  Backlog updated: {component.name} → done")


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------


def save_state(component: ComponentEntry, spec: dict) -> None:
    """Save pipeline state for --plan-only / --resume handoff."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    spec_path = SPECS_DIR / f"{component.number}_{component.name.lower().replace(' ', '_')}.json"
    SPECS_DIR.mkdir(parents=True, exist_ok=True)
    spec_path.write_text(json.dumps(spec, indent=2, default=str))

    STATE_FILE.write_text(json.dumps({
        "component_number": component.number,
        "component_name": component.name,
        "spec_file": str(spec_path),
    }, indent=2))


def load_state() -> dict:
    if not STATE_FILE.exists():
        raise PipelineError(f"No saved state at {STATE_FILE}. Run --plan-only first.")
    return json.loads(STATE_FILE.read_text())


def clear_state() -> None:
    if STATE_FILE.exists():
        STATE_FILE.unlink()


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


def print_spec_summary(spec: dict) -> None:
    """Print human-readable spec summary."""
    print(f"\n{'=' * 60}")
    print(f"Spec: {spec.get('component', '?')}")
    print(f"{'=' * 60}")
    for api in spec.get("public_api", []):
        print(f"  {api.get('name', '?')}: {api.get('signature', '?')}")
    print(f"\nTests planned: {len(spec.get('test_plan', []))}")
    for t in spec.get("test_plan", []):
        print(f"  - {t.get('test_name', '?')}: {t.get('description', '')[:80]}")
    concerns = spec.get("concerns", [])
    if concerns:
        print(f"\nConcerns:")
        for c in concerns:
            print(f"  ! {c}")
    est = spec.get("estimated_lines")
    if est:
        print(f"\nEstimated lines: {est}")
    meta = spec.get("_meta", {})
    cost = meta.get("cost_usd")
    if cost is not None:
        print(f"Cost: ${cost:.4f}")
    print(f"{'=' * 60}")


def print_component_header(component: ComponentEntry, remaining: int) -> None:
    print(f"\n{'#' * 60}")
    print(f"# Component {component.number}: {component.name}")
    print(f"# Files: {component.files}")
    print(f"# Deps: {component.deps}")
    print(f"# {component.description}")
    print(f"# ({remaining} remaining after this)")
    print(f"{'#' * 60}")


# ---------------------------------------------------------------------------
# Per-component pipeline
# ---------------------------------------------------------------------------


def process_component(
    component: ComponentEntry,
    entries: list[ComponentEntry],
    args: argparse.Namespace,
) -> bool:
    """Run the full build pipeline for one component.

    Returns True on success, False on skip/reject.
    """
    remaining = sum(1 for e in entries if e.status == "pending") - 1
    print_component_header(component, remaining)

    # Mark as in_progress
    update_backlog_status(component.name, "in_progress")

    # Phase 1: Spec
    spec = run_spec(component, entries, args.model)
    save_state(component, spec)
    print_spec_summary(spec)

    if args.plan_only:
        print(f"\n[plan-only] Spec saved. Review at: {SPECS_DIR}/")
        print(f"Run with --resume to continue implementation.")
        raise SystemExit(EXIT_NEEDS_APPROVAL)

    if not args.skip_approval:
        answer = input("\nApprove spec and proceed to implementation? [y/N] ").strip().lower()
        if answer != "y":
            update_backlog_status(component.name, "pending")
            print("Skipped by user.")
            return False

    # Phase 2: Implement
    impl_result, worktree_path = run_implement(component, spec, args.model)
    pr_number = impl_result.get("pr_number")

    if not pr_number:
        raise PipelineError(
            f"Phase 2 did not produce a PR. Result: {json.dumps(impl_result, indent=2)[:500]}"
        )

    tests_passed = impl_result.get("tests_passed", False)
    test_count = impl_result.get("test_count", 0)
    print(f"\n  PR #{pr_number}: {impl_result.get('pr_url', '?')}")
    print(f"  Tests: {'PASS' if tests_passed else 'FAIL'} ({test_count} tests)")

    if not tests_passed:
        print(f"  WARNING: Tests did not pass. Check PR #{pr_number}.")

    # Phase 3: Review
    review = run_review(pr_number, component, args.model)
    verdict = review.get("verdict", "request_changes")
    print(f"\n  Review verdict: {verdict}")
    print(f"  Summary: {review.get('summary', 'N/A')}")
    for comment in review.get("comments", []):
        print(f"    - {comment}")

    if verdict != "approve":
        print(f"\n  PR #{pr_number} needs changes. Skipping merge.")
        update_backlog_status(component.name, "pending")
        return False

    # Phase 4: Merge
    merge_pr(pr_number, component, worktree_path)
    clear_state()
    print(f"\n  Done! {component.name} built and merged.")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Autonomous development pipeline for coarse.")
    parser.add_argument("--all", action="store_true", help="Build ALL pending components")
    parser.add_argument("--component", help="Build a specific component (name or number)")
    parser.add_argument("--dry-run", action="store_true", help="Preview next component(s)")
    parser.add_argument("--plan-only", action="store_true", help="Run spec phase only, exit 2")
    parser.add_argument("--resume", action="store_true", help="Resume from implementation")
    parser.add_argument("--skip-approval", action="store_true", help="Skip spec approval gate")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Claude model (default: {DEFAULT_MODEL})")
    args = parser.parse_args()

    if not BACKLOG_PATH.exists():
        print(f"ERROR: Backlog not found at {BACKLOG_PATH}", file=sys.stderr)
        return EXIT_ERROR

    entries = parse_backlog(BACKLOG_PATH)
    if not entries:
        print("ERROR: No components found in backlog.", file=sys.stderr)
        return EXIT_ERROR

    # --all implies --skip-approval
    if args.all:
        args.skip_approval = True

    # --resume: load state and continue from Phase 2
    if args.resume:
        try:
            state = load_state()
        except PipelineError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return EXIT_ERROR

        comp_num = state["component_number"]
        component = None
        for e in entries:
            if e.number == comp_num:
                component = e
                break
        if component is None:
            print(f"ERROR: Component #{comp_num} not found.", file=sys.stderr)
            return EXIT_ERROR

        spec = json.loads(Path(state["spec_file"]).read_text())
        print(f"\nResuming: #{component.number} {component.name}")

        # Jump straight to implement
        try:
            impl_result, worktree_path = run_implement(component, spec, args.model)
            pr_number = impl_result.get("pr_number")
            if not pr_number:
                raise PipelineError("No PR number from implementation.")

            review = run_review(pr_number, component, args.model)
            if review.get("verdict") == "approve":
                merge_pr(pr_number, component, worktree_path)
                clear_state()
            else:
                print(f"PR #{pr_number} needs changes.")
                return EXIT_ERROR
        except PipelineError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return EXIT_ERROR
        return EXIT_OK

    # --dry-run
    if args.dry_run:
        print(f"\nBacklog ({len(entries)} components):")
        done = sum(1 for e in entries if e.status == "done")
        pending = sum(1 for e in entries if e.status == "pending")
        print(f"  Done: {done}, Pending: {pending}")

        nxt = get_next_component(entries, args.component)
        if nxt:
            print(f"\nNext buildable: #{nxt.number} {nxt.name}")
            print(f"  Files: {nxt.files}")
            print(f"  Deps: {nxt.deps}")
            print(f"  Description: {nxt.description}")
        else:
            print("\nNo buildable components (all done or blocked by deps).")

        if args.all:
            # Show full build order
            done_set = {e.number for e in entries if e.status == "done"}
            order = []
            remaining = [e for e in entries if e.status == "pending"]
            while remaining:
                buildable = [
                    e for e in remaining
                    if all(d in done_set for d in e.dep_numbers)
                ]
                if not buildable:
                    break
                for b in sorted(buildable, key=lambda x: x.number):
                    order.append(b)
                    done_set.add(b.number)
                    remaining.remove(b)

            print(f"\nBuild order ({len(order)} components):")
            for i, e in enumerate(order, 1):
                print(f"  {i}. #{e.number} {e.name} (deps: {e.deps})")

        return EXIT_OK

    # Single or --all
    succeeded: list[str] = []
    failed: list[tuple[str, str]] = []

    if args.all:
        iteration = 0
        while True:
            entries = parse_backlog(BACKLOG_PATH)  # re-parse after each merge
            component = get_next_component(entries)
            if component is None:
                break
            iteration += 1

            try:
                ok = process_component(component, entries, args)
                if ok:
                    succeeded.append(component.name)
                else:
                    failed.append((component.name, "rejected/skipped"))
            except PipelineError as exc:
                print(f"\nERROR: {component.name}: {exc}", file=sys.stderr)
                failed.append((component.name, str(exc)))
                update_backlog_status(component.name, "pending")
            except subprocess.TimeoutExpired:
                print(f"\nTIMEOUT: {component.name}", file=sys.stderr)
                failed.append((component.name, "timeout"))
                update_backlog_status(component.name, "pending")
            except KeyboardInterrupt:
                print(f"\nInterrupted after {len(succeeded)} components.")
                break
    else:
        component = get_next_component(entries, args.component)
        if component is None:
            if args.component:
                print(f"ERROR: Component '{args.component}' not found.", file=sys.stderr)
            else:
                print("All components done or blocked. Nothing to build.")
            return EXIT_OK if not args.component else EXIT_ERROR

        try:
            process_component(component, entries, args)
        except SystemExit as exc:
            return exc.code
        except PipelineError as exc:
            print(f"\nERROR: {exc}", file=sys.stderr)
            return EXIT_ERROR

    # Summary for --all
    if args.all:
        print(f"\n{'=' * 60}")
        print("BUILD SUMMARY")
        print(f"{'=' * 60}")
        print(f"Succeeded: {len(succeeded)}")
        for s in succeeded:
            print(f"  + {s}")
        if failed:
            print(f"Failed: {len(failed)}")
            for name, reason in failed:
                print(f"  x {name}: {reason[:80]}")
        print(f"{'=' * 60}")

    return EXIT_ERROR if failed else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
