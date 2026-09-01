"""Supply-chain invariants for executable GitHub Actions workflows."""

from __future__ import annotations

import re
from pathlib import Path

import yaml
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = REPO_ROOT / ".github" / "workflows"
FULL_COMMIT_SHA_RE = re.compile(r"[0-9a-f]{40}")


def _workflow_paths() -> list[Path]:
    """GitHub accepts both workflow filename extensions; enforce both."""
    return sorted({*WORKFLOW_DIR.glob("*.yml"), *WORKFLOW_DIR.glob("*.yaml")})


def _uses_entries(node: Node | None) -> list[tuple[ScalarNode, Node]]:
    """Return every decoded YAML mapping entry whose key is exactly ``uses``.

    Traversing PyYAML's composed node tree preserves duplicate mapping keys and
    resolves quoted escapes and aliases. That makes this check match YAML
    semantics instead of relying on the source spelling of a security-critical
    key.
    """
    if node is None:
        return []
    entries: list[tuple[ScalarNode, Node]] = []
    if isinstance(node, MappingNode):
        for key, value in node.value:
            if isinstance(key, ScalarNode) and key.value == "uses":
                entries.append((key, value))
            entries.extend(_uses_entries(value))
    elif isinstance(node, SequenceNode):
        for item in node.value:
            entries.extend(_uses_entries(item))
    return entries


def _actions_in(source: str) -> list[str | None]:
    """Decode action references from a synthetic workflow fragment."""
    return [
        value.value.strip() if isinstance(value, ScalarNode) else None
        for _, value in _uses_entries(yaml.compose(source))
    ]


def test_third_party_actions_are_pinned_to_full_commit_shas() -> None:
    """Mutable tags must not control CI, deploy, scanning, or PyPI jobs."""
    violations: list[str] = []
    for path in _workflow_paths():
        source = path.read_text()
        try:
            root = yaml.compose(source)
        except yaml.YAMLError as error:
            violations.append(
                f"{path.relative_to(REPO_ROOT)}: invalid YAML cannot be audited: {error}"
            )
            continue
        for key, value in _uses_entries(root):
            line_number = key.start_mark.line + 1
            if not isinstance(value, ScalarNode):
                violations.append(
                    f"{path.relative_to(REPO_ROOT)}:{line_number}: "
                    "uses must have a scalar action reference"
                )
                continue
            action = value.value.strip()
            if action.startswith("./"):
                continue
            _, separator, revision = action.rpartition("@")
            if not separator or not FULL_COMMIT_SHA_RE.fullmatch(revision):
                violations.append(f"{path.relative_to(REPO_ROOT)}:{line_number}: {action}")
    assert not violations, (
        "Pin every third-party GitHub Action to an immutable 40-character "
        "commit SHA (keep a version comment for maintainers):\n  - " + "\n  - ".join(violations)
    )


def test_node20_force_flag_is_retired() -> None:
    """Current action majors run on Node 24 without GitHub's migration shim."""
    stale: list[str] = []
    for path in _workflow_paths():
        if "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24" in path.read_text():
            stale.append(str(path.relative_to(REPO_ROOT)))
    assert not stale, "remove the obsolete Node 20 force flag from: " + ", ".join(stale)


def test_python_dependency_audit_is_lock_aware_and_blocking() -> None:
    """The security job must audit the project lock, not the runner environment."""
    source = (WORKFLOW_DIR / "security.yml").read_text()

    assert "continue-on-error: true" not in source
    assert "uv export --quiet --frozen --all-extras --no-dev --no-emit-project" in source
    assert "uvx pip-audit --strict --no-deps --disable-pip" in source
    assert '--requirement "$RUNNER_TEMP/coarse-audit-requirements.txt"' in source


def test_action_parser_covers_yaml_flow_mappings() -> None:
    """A flow-style step must not evade immutable-ref enforcement."""
    assert _actions_in("- { name: Unsafe, uses: attacker/action@main }") == ["attacker/action@main"]


def test_action_parser_covers_quoted_and_duplicate_flow_keys() -> None:
    """Quoted keys and later duplicate keys must not hide a mutable action."""
    assert _actions_in('- "uses": "attacker/action@main"') == ["attacker/action@main"]
    assert _actions_in("- { uses: ./local-action, 'uses': attacker/action@main }") == [
        "./local-action",
        "attacker/action@main",
    ]


def test_action_parser_covers_multiline_yaml_values() -> None:
    """A line break after ``uses:`` must not hide the selected action."""
    assert _actions_in("steps:\n  - uses:\n      attacker/action@main\n") == [
        "attacker/action@main"
    ]


def test_noncanonical_action_keys_fail_closed() -> None:
    """Explicit, escaped, and aliased YAML keys must decode to ``uses``."""
    sources = (
        "steps:\n  - ? uses\n    : attacker/action@main\n",
        '- "\\x75ses": attacker/action@main\n',
        '- "\\u0075ses": attacker/action@main\n',
        '- "\\U00000075ses": attacker/action@main\n',
        "action_key: &action_key uses\nsteps:\n  - *action_key: attacker/action@main\n",
    )
    for source in sources:
        assert "attacker/action@main" in _actions_in(source)


def test_commented_multiline_action_value_fails_closed() -> None:
    """An inline comment before a multiline value must not hide an action."""
    source = "steps:\n  - uses: # chosen action\n      attacker/action@main\n"
    assert _actions_in(source) == ["attacker/action@main"]
