"""Regression checks for coarse's package boundaries."""

from __future__ import annotations

import ast
from collections.abc import Iterator
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = REPO_ROOT / "src" / "coarse"
DEPLOY_ROOT = REPO_ROOT / "deploy"
AGENT_DENY = {"pipeline", "cli", "synthesis", "extraction", "extraction_qa"}
# `headless_review` is a CLI-adjacent entrypoint used by the coarse-review
# command and the web handoff flow. It needs to monkey-patch
# `coarse.pipeline.LLMClient` to swap in the headless client factory before
# `review_paper()` runs, and there's no clean way to do that without
# importing `coarse.pipeline` directly. Treat it like cli.py for the
# purposes of this whitelist.
PIPELINE_ALLOW = {"cli", "cli_review", "headless_review", "__init__", "__main__"}
TYPES_ALLOW = {"models"}
PROMPTS_ALLOW = {"models", "types"}
MAX_SOURCE_LINES = 800
# `llm` carries the full structured-output + cost-tracking + auth stack
# (litellm wrapper, instructor integration, Kimi JSON/MD_JSON fallback,
# OpenRouter privacy + api_key injection, prompt-caching detection, cost
# estimation helpers). Splitting it cleanly requires a design pass that is
# out of scope for this check — the known-oversized list exists for exactly
# this "tracked for future refactor" state.
# Modules that are allowlisted above ``MAX_SOURCE_LINES``. The value is
# a per-module ceiling — larger than ``MAX_SOURCE_LINES`` (800) but not
# unbounded. The ceiling is the allowlist's teeth: without it,
# allowlisted modules can grow indefinitely under cover of "already
# flagged, will refactor later." With the ceiling, any growth past the
# recorded line count requires an explicit bump in this dict PLUS a
# commit explaining why. The numbers are set to ~10% over current size
# so incidental adds are fine and real bloat fails the test.
#
# `extraction` used to be in this dict back when it was 900+ lines.
# After the refactor in #88 / #102 it dropped to ~291 lines, well
# under the cap — removed from the allowlist so any regression is
# caught immediately.
KNOWN_OVERSIZED: dict[str, int] = {
    # prompts.py currently holds every LLM prompt template for the
    # pipeline — splitting it is a real refactor (per-agent files,
    # shared boundary-notice helpers) and is deferred to post-v1.3.0.
    "prompts": 2700,
    # llm.py wraps litellm + instructor + retry + cost tracking.
    # Splitting it requires an API redesign, also deferred.
    "llm": 1000,
}


def _module_name(path: Path) -> str:
    return path.relative_to(SRC_ROOT).with_suffix("").as_posix().replace("/", ".")


def _imported_targets(current_module: str, node: ast.AST) -> set[str]:
    targets: set[str] = set()
    if isinstance(node, ast.Import):
        for alias in node.names:
            if alias.name.startswith("coarse."):
                targets.add(alias.name.removeprefix("coarse."))
    elif isinstance(node, ast.ImportFrom):
        if node.level:
            base = current_module.split(".")[: -node.level]
            if node.module:
                targets.add(".".join([*base, node.module]))
            else:
                for alias in node.names:
                    if alias.name != "*":
                        targets.add(".".join([*base, alias.name]))
        elif node.module == "coarse":
            for alias in node.names:
                if alias.name != "*":
                    targets.add(alias.name)
        elif node.module and node.module.startswith("coarse."):
            base = node.module.removeprefix("coarse.")
            targets.add(base)
            for alias in node.names:
                if alias.name != "*":
                    targets.add(f"{base}.{alias.name}")
    return {target for target in targets if target}


def _build_import_graph() -> dict[str, set[str]]:
    graph: dict[str, set[str]] = {}
    for path in sorted(SRC_ROOT.rglob("*.py")):
        module = _module_name(path)
        imports: set[str] = set()
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            imports.update(_imported_targets(module, node))
        graph[module] = imports
    return graph


def _build_deploy_import_graph() -> dict[str, set[str]]:
    graph: dict[str, set[str]] = {}
    for path in sorted(DEPLOY_ROOT.rglob("*.py")):
        module = path.relative_to(DEPLOY_ROOT).with_suffix("").as_posix().replace("/", ".")
        imports: set[str] = set()
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            imports.update(_imported_targets(module, node))
        graph[module] = imports
    return graph


def _resolve_module(graph: dict[str, set[str]], name: str) -> str | None:
    candidate = name
    while candidate:
        if candidate in graph:
            return candidate
        if "." not in candidate:
            break
        candidate = candidate.rsplit(".", 1)[0]
    return None


def _find_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    white, gray, black = 0, 1, 2
    colors = {module: white for module in graph}
    cycles: list[list[str]] = []

    def walk(start: str) -> None:
        stack: list[tuple[str, Iterator[str]]] = [(start, iter(graph.get(start, ())))]
        path = [start]
        colors[start] = gray

        while stack:
            node, children = stack[-1]
            try:
                child_name = next(children)
            except StopIteration:
                colors[node] = black
                stack.pop()
                path.pop()
                continue

            child = _resolve_module(graph, child_name)
            if not child:
                continue
            if colors[child] == gray:
                first = path.index(child)
                cycles.append(path[first:] + [child])
            elif colors[child] == white:
                colors[child] = gray
                path.append(child)
                stack.append((child, iter(graph.get(child, ()))))

    for module in list(graph):
        if colors[module] == white:
            walk(module)

    return cycles


def _resolved_imports(graph: dict[str, set[str]], imports: set[str]) -> set[str]:
    return {_resolve_module(graph, name) or name for name in imports}


def test_import_graph_has_no_cycles():
    graph = _build_import_graph()

    assert _find_cycles(graph) == []


def test_no_src_coarse_file_exceeds_800_lines():
    offenders = {
        _module_name(path): path.read_text().count("\n") + 1
        for path in sorted(SRC_ROOT.rglob("*.py"))
        if path.read_text().count("\n") + 1 > MAX_SOURCE_LINES
    }
    unexpected: dict[str, int] = {}
    for module, lines in offenders.items():
        if module not in KNOWN_OVERSIZED:
            unexpected[module] = lines
            continue
        # Allowlisted modules have an explicit per-module ceiling so
        # they cannot grow unchecked. Tripping this branch means the
        # allowlisted module grew past its recorded cap — bump the
        # entry in `KNOWN_OVERSIZED` with a commit explaining why, or
        # start the refactor this allowlist was deferring.
        cap = KNOWN_OVERSIZED[module]
        if lines > cap:
            unexpected[module] = lines

    assert unexpected == {}, (
        "Oversized modules (or allowlisted modules that grew past their "
        "recorded cap): " + ", ".join(f"{m}={n}" for m, n in sorted(unexpected.items()))
    )


def test_models_types_and_prompts_stay_within_allowed_layers():
    graph = _build_import_graph()

    assert _resolved_imports(graph, graph["models"]) == set()
    assert _resolved_imports(graph, graph["types"]) <= TYPES_ALLOW
    assert _resolved_imports(graph, graph["prompts"]) <= PROMPTS_ALLOW


def test_agents_do_not_import_orchestration_modules():
    graph = _build_import_graph()

    offenders = {
        module: sorted(
            target for target in imports if (_resolve_module(graph, target) or target) in AGENT_DENY
        )
        for module, imports in graph.items()
        if module.startswith("agents.")
        and any((_resolve_module(graph, target) or target) in AGENT_DENY for target in imports)
    }

    assert offenders == {}


def test_pipeline_importers_stay_whitelisted():
    graph = _build_import_graph()

    offenders: dict[str, list[str]] = {}
    for module, imports in graph.items():
        pipeline_imports = sorted(
            target for target in imports if _resolve_module(graph, target) == "pipeline"
        )
        if not pipeline_imports:
            continue
        if module in PIPELINE_ALLOW:
            continue
        offenders[module] = pipeline_imports

    assert offenders == {}


def test_deploy_modules_do_not_import_pipeline_directly():
    graph = _build_deploy_import_graph()

    offenders = {
        module: sorted(
            target for target in imports if target == "pipeline" or target.startswith("pipeline.")
        )
        for module, imports in graph.items()
        if any(target == "pipeline" or target.startswith("pipeline.") for target in imports)
    }

    assert offenders == {}
