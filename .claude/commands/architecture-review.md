# Architecture Review for coarse

Macro-level structural review of the `src/coarse/` package. Run when you've
just landed a big feature, added a new agent, or are about to reshape the
pipeline. This is the counterpart to `/module-review` — that one looks at a
single file, this one looks at how the package fits together.

coarse is small (~20 modules), so this command doesn't need a long-running
orchestrator script. It uses 1 quick Python AST scan + 3 parallel in-session
agents via the Agent tool.

## Arguments

`$ARGUMENTS`:
- `/architecture-review` — full review with the 3-agent panel (~$1.50)
- `/architecture-review --scan-only` — import graph + layer check, no LLM
- `/architecture-review --scope coupling,data-flow` — restrict which agents run

## Package layer rules

These rules are enforced by the static scan in Step 1. Each is either HIGH
(structural) or MEDIUM (smell).

**Structural (HIGH):**
1. **`models.py` has zero internal dependencies.** It must not `from coarse ...` anything. It is the single source of truth for model IDs.
2. **No import cycles.** Anywhere.
3. **`agents/*.py` must not import from** `pipeline.py`, `cli.py`, `synthesis.py`, `extraction.py`, `extraction_qa.py`. They run before the orchestrator and must not close that loop.
4. **`pipeline.py` is the orchestrator.** Only `cli.py`, `__init__.py`, `__main__.py`, and `deploy/*.py` may import from it.

**Smell (MEDIUM — the LLM agent judges whether to act):**
5. **No file larger than 800 lines** in `src/coarse/`. Over that → flag for Agent C (simplification) to decide whether to split.
6. **`types.py` may import from `models.py` only.** Other imports are a smell worth explaining.
7. **`prompts.py` may import from `types.py` and `models.py` only** (for type hints on prompt-builder functions).

## Process

### Step 1: Static AST scan

Run this inline — a ~50-line Python block that parses every `.py` under
`src/coarse/` and builds the import graph. Write it as a heredoc and pipe to
python3; no new script file needed. Report:

- **Cycles**: list any strongly connected component with > 1 node
- **Layer violations**: flag any edge that breaks rules 1-6 above
- **Oversized files**: files over 800 lines
- **Coupling hotspots**: the 3 modules with the most in-edges (fan-in)

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && python3 <<'PY'
import ast
from pathlib import Path

root = Path("src/coarse")
AGENT_DENY = {"pipeline", "cli", "synthesis", "extraction", "extraction_qa"}
PIPELINE_CALLERS = {"cli", "__init__", "__main__"}  # plus deploy/*.py
TYPES_ALLOW = {"models"}
PROMPTS_ALLOW = {"models", "types"}

graph: dict[str, set[str]] = {}
sizes: dict[str, int] = {}
for p in sorted(root.rglob("*.py")):
    mod = p.relative_to(root).with_suffix("").as_posix().replace("/", ".")
    src = p.read_text()
    sizes[mod] = src.count("\n")
    try:
        tree = ast.parse(src)
    except SyntaxError:
        continue
    imports: set[str] = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module and n.module.startswith("coarse"):
            imports.add(n.module.removeprefix("coarse.").split(".")[0] or "")
        elif isinstance(n, ast.Import):
            for a in n.names:
                if a.name.startswith("coarse."):
                    imports.add(a.name.removeprefix("coarse.").split(".")[0])
    graph[mod] = {i for i in imports if i}

structural: list[str] = []
smells: list[str] = []
for mod, imps in graph.items():
    name = mod.split(".")[-1]
    if name == "models" and imps:
        structural.append(f"HIGH: models.py imports {sorted(imps)} (must have zero internal deps)")
    if name == "types" and imps - TYPES_ALLOW:
        smells.append(f"MEDIUM: types.py imports {sorted(imps - TYPES_ALLOW)} (only models.py is allowed)")
    if name == "prompts" and imps - PROMPTS_ALLOW:
        smells.append(f"MEDIUM: prompts.py imports {sorted(imps - PROMPTS_ALLOW)} (only models.py, types.py allowed)")
    if mod.startswith("agents.") and imps & AGENT_DENY:
        structural.append(f"HIGH: {mod} imports {sorted(imps & AGENT_DENY)} (agents must not import orchestration)")

# cycles via iterative DFS
WHITE, GRAY, BLACK = 0, 1, 2
color = {m: WHITE for m in graph}
cycles: list[list[str]] = []
def resolve(name: str) -> str | None:
    if name in graph:
        return name
    for m in graph:
        if m == name or m.endswith("." + name):
            return m
    return None
def dfs(start: str) -> None:
    stack = [(start, iter(graph.get(start, ())))]
    path = [start]
    color[start] = GRAY
    while stack:
        node, it = stack[-1]
        try:
            nxt = next(it)
        except StopIteration:
            color[node] = BLACK
            stack.pop()
            path.pop()
            continue
        tgt = resolve(nxt)
        if not tgt:
            continue
        if color.get(tgt) == GRAY:
            i = path.index(tgt)
            cycles.append(path[i:] + [tgt])
        elif color.get(tgt) == WHITE:
            color[tgt] = GRAY
            path.append(tgt)
            stack.append((tgt, iter(graph.get(tgt, ()))))
for m in list(graph):
    if color[m] == WHITE:
        dfs(m)

fan_in = {m: 0 for m in graph}
for imps in graph.values():
    for i in imps:
        tgt = resolve(i)
        if tgt:
            fan_in[tgt] += 1
top = sorted(fan_in.items(), key=lambda x: -x[1])[:3]
oversized = [f"{m} ({n} lines)" for m, n in sizes.items() if n > 800]

print(f"modules: {len(graph)}")
print(f"oversized (>800 lines): {oversized or 'none'}")
print(f"structural (HIGH): {structural or 'none'}")
print(f"smells (MEDIUM): {smells or 'none'}")
print(f"cycles: {cycles or 'none'}")
print(f"fan-in leaders: {top}")
PY
```

If `$ARGUMENTS` contains `--scan-only`, stop here and report the results.

### Step 2: Launch 3 parallel agents (Agent tool, one message)

All three share the static scan output as context. Budget ~$0.50 each.

**Agent A — Coupling & cohesion**
*(subagent_type: system-architect)*

Read `src/coarse/pipeline.py`, the `fan-in leaders` from Step 1, and any
flagged layer violations. Answer:
- Are any modules doing two unrelated jobs that should be split?
- Is any pair of modules so tightly coupled they should be merged?
- Are layer violations accidental (fix in place) or structural (needs rethink)?

Output: ranked proposals with file paths and estimated effort (small/medium/large).

**Agent B — Data flow & type boundaries**
*(subagent_type: system-architect)*

Read `src/coarse/types.py`, `pipeline.py`, and `synthesis.py`. Trace the path
of a single `PaperText` → `PaperStructure` → `Review`. Answer:
- Are there type gaps where a `dict[str, Any]` is being passed that should be
  a Pydantic model?
- Are any fields on `Review` / `DetailedComment` computed in more than one
  place (duplication)?
- Does every agent return a Pydantic model, or do any return raw strings that
  need parsing downstream?

Output: ranked violations with `file.py:line`.

**Agent C — Simplification**
*(subagent_type: refactoring-specialist)*

Read every file flagged as oversized (>800 lines) plus `pipeline.py`. Answer:
- Where is the 200-line function that could be 50?
- Where is the abstraction that only has one concrete subclass?
- Where is the dead code path that never runs?
- Where is the pre-emptive config flag that was never flipped?

Output: for each suggestion, the current line count vs. the proposed line
count, and a one-sentence justification.

### Step 3: Adversarial pass (inline, no new agent)

Take the three agent reports and challenge them yourself:

- For each proposal, ask: "does the current code actually have this problem,
  or is the agent pattern-matching on what it expects to see?"
- For each refactor: "does the new shape break anything the existing tests
  depend on?"
- For each split proposal: "will there be a meaningful API change that
  breaks callers in `deploy/` or `web/`?"

Cross-reference against CLAUDE.md's documented pipeline — if an agent
proposes changing the pipeline's phase order, that's an escalation to the
user, not an auto-approval.

### Step 4: Classify and present

Produce a ranked list:

```
ARCHITECTURE REVIEW — <branch>
Modules: <N>  Violations: <N>  Cycles: <N>  Oversized: <N>

Proposals:
  1. [HIGH  / small ] Split structure.py metadata LLM call into its own module
     Why: violates single-responsibility; 310 lines including unrelated LLM logic
     Files: src/coarse/structure.py → src/coarse/structure.py + src/coarse/structure_llm.py
     Adversarial check: no public API break, all tests scoped to structure.py

  2. [MEDIUM / medium] Remove unused `PaperMetadata.arxiv_id` field
     Why: never read anywhere in the codebase
     Files: src/coarse/types.py:47, src/coarse/structure.py (1 ref)
     Adversarial check: passes — confirmed zero readers via grep

  ...
```

**Always escalate to the user:**
- Anything that changes `types.py`, `models.py`, or `pipeline.py` phase order
- Anything that touches `agents/base.py` (ABC — affects every agent)
- Any proposal the adversarial step flagged
- Any proposal with effort = large

**Auto-apply (after telling the user what you're about to do):**
- Removing genuinely dead code you verified with grep
- Tightening a Pydantic field type (e.g., `str` → `Literal[...]`)
- Moving an obvious utility to a more natural home

### Step 5: Apply approved changes and verify

For each approved change:
1. Edit in place
2. Run `uv run pytest tests/ -v`
3. Run `python3 scripts/security_scanner.py`
4. If both pass, commit with a conventional-commits message scoped to `arch`

Stop and report if any change breaks tests.

## Important notes

- **Don't use subprocess parallelism.** Launch the 3 agents in-session via
  the Agent tool, one message with 3 tool uses. That's how coarse does
  parallelism — not `claude -p` subprocesses.
- **One pass per session.** Unlike hsf's multi-round loop, a single
  architecture review should produce a finite action list. If the review
  finds so much that it needs multiple rounds, that's a signal the user
  should prioritize manually.
- **Respect CLAUDE.md's "simplicity first" rule.** When in doubt between
  two proposals, favour the one that removes code rather than the one that
  reorganises it.
