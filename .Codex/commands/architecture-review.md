# Architecture Review for coarse (Codex)

Macro-level structural review of the `src/coarse/` package. Run when a large
feature lands, a new agent appears, or the pipeline has been reshaped. This is
the counterpart to `/module-review`: architecture review looks across modules,
not inside one file.

coarse is small enough that this command can stay in-session. Use one static
scan plus three parallel in-session agents when the caller does not ask for
`--scan-only`.

## Arguments

`$ARGUMENTS`:
- `/architecture-review` — full review with static scan + 3-agent panel
- `/architecture-review --scan-only` — import graph and layer checks only
- `/architecture-review --scope coupling,data-flow` — restrict which agent
  tracks to run

## Package layer rules

Treat these as the structural baseline.

**Structural (HIGH):**
1. `models.py` has zero internal dependencies.
2. No import cycles anywhere.
3. `agents/*.py` must not import `pipeline.py`, `cli.py`, `synthesis.py`,
   `extraction.py`, or `extraction_qa.py`.
4. `pipeline.py` is the orchestrator. Only `cli.py`, `__init__.py`,
   `__main__.py`, and `deploy/*.py` may import it.

**Smell (MEDIUM):**
5. No file larger than 800 lines in `src/coarse/`.
6. `types.py` may import from `models.py` only.
7. `prompts.py` may import from `types.py` and `models.py` only.

## Process

### 1. Run the static scan

Run an inline Python AST scan over `src/coarse/**/*.py`. Report:
- import cycles
- layer violations
- oversized files
- top fan-in modules

Use this exact shape:

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && python3 <<'PY'
import ast
from pathlib import Path

root = Path("src/coarse")
agent_deny = {"pipeline", "cli", "synthesis", "extraction", "extraction_qa"}
types_allow = {"models"}
prompts_allow = {"models", "types"}

graph: dict[str, set[str]] = {}
sizes: dict[str, int] = {}
for path in sorted(root.rglob("*.py")):
    module = path.relative_to(root).with_suffix("").as_posix().replace("/", ".")
    source = path.read_text()
    sizes[module] = source.count("\\n") + 1
    tree = ast.parse(source)
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("coarse"):
            imports.add(node.module.removeprefix("coarse.").split(".")[0] or "")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("coarse."):
                    imports.add(alias.name.removeprefix("coarse.").split(".")[0])
    graph[module] = {name for name in imports if name}

def resolve(name: str) -> str | None:
    if name in graph:
        return name
    for module in graph:
        if module == name or module.endswith("." + name):
            return module
    return None

structural: list[str] = []
smells: list[str] = []
for module, imports in graph.items():
    name = module.split(".")[-1]
    if name == "models" and imports:
        structural.append(f"HIGH: models.py imports {sorted(imports)}")
    if name == "types" and imports - types_allow:
        smells.append(f"MEDIUM: types.py imports {sorted(imports - types_allow)}")
    if name == "prompts" and imports - prompts_allow:
        smells.append(f"MEDIUM: prompts.py imports {sorted(imports - prompts_allow)}")
    if module.startswith("agents.") and imports & agent_deny:
        structural.append(f"HIGH: {module} imports {sorted(imports & agent_deny)}")

white, gray, black = 0, 1, 2
color = {module: white for module in graph}
cycles: list[list[str]] = []

def walk(start: str) -> None:
    stack = [(start, iter(graph.get(start, ())))]
    path = [start]
    color[start] = gray
    while stack:
        node, it = stack[-1]
        try:
            target_name = next(it)
        except StopIteration:
            color[node] = black
            stack.pop()
            path.pop()
            continue
        target = resolve(target_name)
        if not target:
            continue
        if color.get(target) == gray:
            index = path.index(target)
            cycles.append(path[index:] + [target])
        elif color.get(target) == white:
            color[target] = gray
            path.append(target)
            stack.append((target, iter(graph.get(target, ()))))

for module in list(graph):
    if color[module] == white:
        walk(module)

fan_in = {module: 0 for module in graph}
for imports in graph.values():
    for imported in imports:
        target = resolve(imported)
        if target:
            fan_in[target] += 1

oversized = [f"{module} ({lines} lines)" for module, lines in sizes.items() if lines > 800]
leaders = sorted(fan_in.items(), key=lambda item: -item[1])[:3]

print(f"modules: {len(graph)}")
print(f"oversized: {oversized or 'none'}")
print(f"structural: {structural or 'none'}")
print(f"smells: {smells or 'none'}")
print(f"cycles: {cycles or 'none'}")
print(f"fan-in leaders: {leaders}")
PY
```

If `$ARGUMENTS` contains `--scan-only`, stop here and report.

### 2. Launch 3 parallel agents

Spawn three in-session agents in one batch. Give them the static scan output
and the changed-file list when relevant.

Agent A, `explorer`:
- coupling and cohesion
- modules doing multiple unrelated jobs
- overly tight pairs that should merge or decouple

Agent B, `explorer`:
- data flow through `types.py`, `pipeline.py`, and `synthesis.py`
- duplicated field derivation
- raw dictionaries where Pydantic models should exist

Agent C, `explorer`:
- simplification opportunities in oversized files and `pipeline.py`
- dead branches
- one-off abstractions
- extractable 200-line functions

Each report should rank findings with file paths and small/medium/large effort.

### 3. Adversarial pass

Challenge the agent output yourself:
- Is the problem real in this codebase, or generic pattern-matching?
- Would the proposed split break existing tests or call sites?
- Does the proposal change `types.py`, `models.py`, `pipeline.py` phase order,
  or `agents/base.py`? If yes, escalate instead of auto-applying.

### 4. Report

Present the result in this form:

```text
ARCHITECTURE REVIEW — <branch>
Modules: <N>  Violations: <N>  Cycles: <N>  Oversized: <N>

Proposals:
  1. [HIGH / small] <title>
     Why: <one sentence>
     Files: <paths>
     Adversarial check: <pass/fail and why>
```

Always escalate:
- changes to `types.py`
- changes to `models.py`
- pipeline phase-order changes
- edits to `agents/base.py`
- any proposal marked large

Auto-apply only after telling the user what you are changing, and only for
obvious dead-code removals or utility moves that do not alter behavior.

### 5. Verify any approved edits

For each applied change:
1. edit in place
2. run `uv run pytest tests/ -v`
3. run `python3 scripts/security_scanner.py`
4. stop and report if either fails

## Important notes

- Prefer in-session parallel agents over subprocess orchestration.
- Keep the review finite. If the branch needs multiple architecture rounds,
  that is itself a finding.
- Favor proposals that remove code over proposals that add framework.
