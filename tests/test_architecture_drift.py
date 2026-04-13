"""Regression checks for coarse's package boundaries."""

from __future__ import annotations

import ast
from collections.abc import Iterator
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parent.parent / "src" / "coarse"
AGENT_DENY = {"pipeline", "cli", "synthesis", "extraction", "extraction_qa"}
PIPELINE_ALLOW = {"cli", "__init__", "__main__"}
TYPES_ALLOW = {"models"}
PROMPTS_ALLOW = {"models", "types"}


def _module_name(path: Path) -> str:
    return path.relative_to(SRC_ROOT).with_suffix("").as_posix().replace("/", ".")


def _build_import_graph() -> dict[str, set[str]]:
    graph: dict[str, set[str]] = {}
    for path in sorted(SRC_ROOT.rglob("*.py")):
        imports: set[str] = set()
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module
                and node.module.startswith("coarse")
            ):
                imports.add(node.module.removeprefix("coarse.").split(".")[0] or "")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("coarse."):
                        imports.add(alias.name.removeprefix("coarse.").split(".")[0])
        graph[_module_name(path)] = {name for name in imports if name}
    return graph


def _resolve_module(graph: dict[str, set[str]], name: str) -> str | None:
    if name in graph:
        return name
    for module in graph:
        if module == name or module.endswith(f".{name}"):
            return module
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


def test_import_graph_has_no_cycles():
    graph = _build_import_graph()

    assert _find_cycles(graph) == []


def test_models_types_and_prompts_stay_within_allowed_layers():
    graph = _build_import_graph()

    assert graph["models"] == set()
    assert graph["types"] <= TYPES_ALLOW
    assert graph["prompts"] <= PROMPTS_ALLOW


def test_agents_do_not_import_orchestration_modules():
    graph = _build_import_graph()

    offenders = {
        module: sorted(imports & AGENT_DENY)
        for module, imports in graph.items()
        if module.startswith("agents.") and imports & AGENT_DENY
    }

    assert offenders == {}


def test_pipeline_importers_stay_whitelisted():
    graph = _build_import_graph()

    offenders = []
    for module, imports in graph.items():
        if "pipeline" not in imports:
            continue
        module_name = module.split(".")[-1]
        if module_name in PIPELINE_ALLOW or module.startswith("deploy."):
            continue
        offenders.append(module)

    assert offenders == []
