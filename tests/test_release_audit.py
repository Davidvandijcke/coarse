"""CI-time drift guard for the dev -> main release audit.

``scripts/release_audit.py`` is the operator-facing pre-release helper.
Its repo-local check is cheap and deterministic, so we also run it
inside pytest on every commit to catch the case where someone adds a
new ``process.env.PREVIEW_BASIC_AUTH_PASSWORD`` or
``process.env.VERCEL_AUTOMATION_BYPASS_SECRET`` read without an
environment guard. Vercel deliberately injects the latter system
variable into every deployment; the guard ensures only preview code
can consume it. Without this test, a regression would silently ship
and only be caught during the next manual release audit.
"""

from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "release_audit.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("release_audit", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _audit_snippet(source: str) -> list[str]:
    """Run the repository audit against one synthetic TypeScript source."""
    module = _load_module()
    original_repo_root = module.REPO_ROOT
    original_web_src = module.WEB_SRC
    try:
        with tempfile.TemporaryDirectory() as td:
            fake_repo = Path(td)
            fake_web = fake_repo / "web" / "src" / "app"
            fake_web.mkdir(parents=True)
            (fake_web / "sample.ts").write_text(source, encoding="utf-8")
            module.REPO_ROOT = fake_repo
            module.WEB_SRC = fake_repo / "web" / "src"
            return module.audit_repo_guards()
    finally:
        module.REPO_ROOT = original_repo_root
        module.WEB_SRC = original_web_src


def test_release_audit_clean_on_dev() -> None:
    """Every preview-gated env var read in web/src must be VERCEL_ENV-guarded."""
    module = _load_module()
    violations = module.audit_repo_guards()
    assert not violations, (
        "release_audit found unguarded reads of preview-gated env vars. "
        "Every `process.env.PREVIEW_BASIC_AUTH_PASSWORD`, "
        "`process.env.PREVIEW_BASIC_AUTH_USERNAME`, or "
        "`process.env.VERCEL_AUTOMATION_BYPASS_SECRET` in web/src must "
        "be inside the appropriate explicit `VERCEL_ENV` equality block so production "
        "code paths cannot activate preview-only behavior.\n\nViolations:\n  - "
        + "\n  - ".join(violations)
    )


def test_release_audit_detects_injected_unguarded_read() -> None:
    """Positive control: if we inject an unguarded read the detector must flag it."""
    module = _load_module()
    original_repo_root = module.REPO_ROOT
    original_web_src = module.WEB_SRC
    try:
        with tempfile.TemporaryDirectory() as td:
            fake_repo = Path(td)
            fake_web = fake_repo / "web" / "src" / "app"
            fake_web.mkdir(parents=True)
            (fake_web / "bad.ts").write_text(
                "export function bad() {\n  return process.env.PREVIEW_BASIC_AUTH_PASSWORD;\n}\n",
                encoding="utf-8",
            )
            module.REPO_ROOT = fake_repo
            module.WEB_SRC = fake_repo / "web" / "src"
            violations = module.audit_repo_guards()
    finally:
        module.REPO_ROOT = original_repo_root
        module.WEB_SRC = original_web_src
    assert violations, "detector must flag an unguarded process.env read"
    assert any("bad.ts" in v for v in violations)
    assert any("PREVIEW_BASIC_AUTH_PASSWORD" in v for v in violations)


def test_release_audit_accepts_string_literal_mentions() -> None:
    """Negative control: var names inside warning strings are not violations."""
    module = _load_module()
    original_repo_root = module.REPO_ROOT
    original_web_src = module.WEB_SRC
    try:
        with tempfile.TemporaryDirectory() as td:
            fake_repo = Path(td)
            fake_web = fake_repo / "web" / "src" / "app"
            fake_web.mkdir(parents=True)
            (fake_web / "ok.ts").write_text(
                'export const warning = "set VERCEL_AUTOMATION_BYPASS_SECRET on preview";\n',
                encoding="utf-8",
            )
            module.REPO_ROOT = fake_repo
            module.WEB_SRC = fake_repo / "web" / "src"
            violations = module.audit_repo_guards()
    finally:
        module.REPO_ROOT = original_repo_root
        module.WEB_SRC = original_web_src
    assert not violations, (
        "String-literal mentions of the var name are not process.env reads "
        "and must not be flagged: " + "\n".join(violations)
    )


def test_release_audit_accepts_guarded_read() -> None:
    """Negative control: a guarded process.env read must NOT be flagged."""
    module = _load_module()
    original_repo_root = module.REPO_ROOT
    original_web_src = module.WEB_SRC
    try:
        with tempfile.TemporaryDirectory() as td:
            fake_repo = Path(td)
            fake_web = fake_repo / "web" / "src" / "app"
            fake_web.mkdir(parents=True)
            (fake_web / "good.ts").write_text(
                'if (process.env.VERCEL_ENV === "preview") {\n'
                "  const secret = process.env.VERCEL_AUTOMATION_BYPASS_SECRET;\n"
                "  void secret;\n"
                "}\n",
                encoding="utf-8",
            )
            module.REPO_ROOT = fake_repo
            module.WEB_SRC = fake_repo / "web" / "src"
            violations = module.audit_repo_guards()
    finally:
        module.REPO_ROOT = original_repo_root
        module.WEB_SRC = original_web_src
    assert not violations, "guarded read must not be flagged: " + "\n".join(violations)


def test_release_audit_detects_unguarded_system_bypass_read() -> None:
    """The system bypass may exist in prod, but application use must stay preview-only."""
    module = _load_module()
    original_repo_root = module.REPO_ROOT
    original_web_src = module.WEB_SRC
    try:
        with tempfile.TemporaryDirectory() as td:
            fake_repo = Path(td)
            fake_web = fake_repo / "web" / "src" / "app"
            fake_web.mkdir(parents=True)
            (fake_web / "bad.ts").write_text(
                "export const secret = process.env.VERCEL_AUTOMATION_BYPASS_SECRET;\n",
                encoding="utf-8",
            )
            module.REPO_ROOT = fake_repo
            module.WEB_SRC = fake_repo / "web" / "src"
            violations = module.audit_repo_guards()
    finally:
        module.REPO_ROOT = original_repo_root
        module.WEB_SRC = original_web_src
    assert any("VERCEL_AUTOMATION_BYPASS_SECRET" in v for v in violations)


def test_release_audit_rejects_production_guard_for_system_bypass() -> None:
    """A production branch is valid for leak reporting, never bypass consumption."""
    module = _load_module()
    original_repo_root = module.REPO_ROOT
    original_web_src = module.WEB_SRC
    try:
        with tempfile.TemporaryDirectory() as td:
            fake_repo = Path(td)
            fake_web = fake_repo / "web" / "src" / "app"
            fake_web.mkdir(parents=True)
            (fake_web / "bad.ts").write_text(
                'if (process.env.VERCEL_ENV === "production") {\n'
                "  const secret = process.env.VERCEL_AUTOMATION_BYPASS_SECRET;\n"
                "  void secret;\n"
                "}\n",
                encoding="utf-8",
            )
            module.REPO_ROOT = fake_repo
            module.WEB_SRC = fake_repo / "web" / "src"
            violations = module.audit_repo_guards()
    finally:
        module.REPO_ROOT = original_repo_root
        module.WEB_SRC = original_web_src
    assert any("VERCEL_AUTOMATION_BYPASS_SECRET" in v for v in violations)


def test_release_audit_rejects_comment_only_guard() -> None:
    """A nearby comment must not satisfy the control-flow invariant."""
    violations = _audit_snippet(
        '// if (process.env.VERCEL_ENV === "preview") {\n'
        "const secret = process.env.VERCEL_AUTOMATION_BYPASS_SECRET;\n"
    )
    assert any("VERCEL_AUTOMATION_BYPASS_SECRET" in violation for violation in violations)


def test_release_audit_rejects_closed_or_unrelated_preview_branch() -> None:
    """Only lexical containment counts; proximity to a closed branch is unsafe."""
    violations = _audit_snippet(
        'if (process.env.VERCEL_ENV === "preview") {\n'
        "  console.log('preview');\n"
        "}\n"
        "const secret = process.env.VERCEL_AUTOMATION_BYPASS_SECRET;\n"
    )
    assert any("VERCEL_AUTOMATION_BYPASS_SECRET" in violation for violation in violations)


def test_release_audit_detects_bracket_and_destructured_reads() -> None:
    """Alternate process.env syntax must not bypass the protected-var scan."""
    violations = _audit_snippet(
        'const bracket = process.env["VERCEL_AUTOMATION_BYPASS_SECRET"];\n'
        "const { PREVIEW_BASIC_AUTH_PASSWORD: password } = process.env;\n"
    )
    assert any("VERCEL_AUTOMATION_BYPASS_SECRET" in violation for violation in violations)
    assert any("PREVIEW_BASIC_AUTH_PASSWORD" in violation for violation in violations)


def test_release_audit_detects_optional_chain_and_bracketed_env_object() -> None:
    """Common property-access variants must not evade the protected-var scan."""
    violations = _audit_snippet(
        "const optional = process.env?.VERCEL_AUTOMATION_BYPASS_SECRET;\n"
        "const bracketed = process['env'].PREVIEW_BASIC_AUTH_PASSWORD;\n"
    )
    assert any("VERCEL_AUTOMATION_BYPASS_SECRET" in violation for violation in violations)
    assert any("PREVIEW_BASIC_AUTH_PASSWORD" in violation for violation in violations)


def test_release_audit_rejects_computed_reads_and_process_env_aliases() -> None:
    """Indirection is rejected because a text audit cannot prove the selected key."""
    violations = _audit_snippet(
        "const key = getKey();\n"
        "const computed = process.env[key];\n"
        "const environment = process.env;\n"
    )
    assert any("bracket/computed process.env access" in violation for violation in violations)
    assert any("process.env alias" in violation for violation in violations)


def test_release_audit_rejects_parenthesized_spread_typed_and_process_aliases() -> None:
    """Protected identifiers reached through alternate aliases must fail closed."""
    violations = _audit_snippet(
        "const parenthesized = (process.env).VERCEL_AUTOMATION_BYPASS_SECRET;\n"
        "const spread = { ...process.env };\n"
        "const spreadSecret = spread.PREVIEW_BASIC_AUTH_PASSWORD;\n"
        "const typed: NodeJS.ProcessEnv = process.env;\n"
        "const typedSecret = typed.PREVIEW_BASIC_AUTH_USERNAME;\n"
        "const { env } = process;\n"
        "const processAliasSecret = env.VERCEL_AUTOMATION_BYPASS_SECRET;\n"
    )
    assert any("VERCEL_AUTOMATION_BYPASS_SECRET" in violation for violation in violations)
    assert any("PREVIEW_BASIC_AUTH_PASSWORD" in violation for violation in violations)
    assert any("PREVIEW_BASIC_AUTH_USERNAME" in violation for violation in violations)


def test_release_audit_rejects_node_process_import_and_indirect_bracket_key() -> None:
    """Importing or destructuring a process alias must not hide protected keys."""
    violations = _audit_snippet(
        'import { env } from "node:process";\n'
        'const imported = env["VERCEL_AUTOMATION_BYPASS_SECRET"];\n'
        "const { env: processEnvironment } = process;\n"
        'const destructured = processEnvironment["PREVIEW_BASIC_AUTH_PASSWORD"];\n'
    )
    assert any("process environment alias" in violation for violation in violations)
    assert any("VERCEL_AUTOMATION_BYPASS_SECRET" in violation for violation in violations)
    assert any("PREVIEW_BASIC_AUTH_PASSWORD" in violation for violation in violations)


def test_release_audit_rejects_every_process_module_import_shape() -> None:
    """Default, namespace, dynamic, and CommonJS aliases must all fail closed."""
    snippets = (
        'import proc from "node:process";\nconst value = proc.env[key];\n',
        'import * as proc from "process";\nconst value = proc.env[key];\n',
        'const proc = await import("node:process");\nconst value = proc.env[key];\n',
        'const proc = require("process");\nconst value = proc.env[key];\n',
    )
    for source in snippets:
        violations = _audit_snippet(source)
        assert any("process environment alias" in violation for violation in violations), (
            source,
            violations,
        )


def test_release_audit_rejects_computed_string_expression_and_regex_guard_spoof() -> None:
    """Literal prefixes and regex text must not evade or forge the audit."""
    computed = _audit_snippet(
        'const secret = process.env["VERCEL_AUTOMATION_" + "BYPASS_SECRET"];\n'
    )
    assert any("bracket/computed process.env access" in violation for violation in computed)

    spoofed = _audit_snippet(
        'const marker = /if (process.env.VERCEL_ENV === "preview") {/;\n'
        "const secret = process.env.VERCEL_AUTOMATION_BYPASS_SECRET;\n"
    )
    assert any("VERCEL_AUTOMATION_BYPASS_SECRET" in violation for violation in spoofed)

    keyword_spoof = _audit_snippet(
        'function* demo() { yield /if (process.env.VERCEL_ENV === "preview") {x/;\n'
        "const secret = process.env.VERCEL_AUTOMATION_BYPASS_SECRET; }\n"
    )
    assert any("VERCEL_AUTOMATION_BYPASS_SECRET" in violation for violation in keyword_spoof)


def test_release_audit_accepts_production_leak_detector_for_basic_auth_only() -> None:
    """Production may inspect preview Basic Auth vars solely to report drift."""
    module = _load_module()
    original_repo_root = module.REPO_ROOT
    original_web_src = module.WEB_SRC
    try:
        with tempfile.TemporaryDirectory() as td:
            fake_repo = Path(td)
            fake_web = fake_repo / "web" / "src"
            fake_web.mkdir(parents=True)
            (fake_web / "middleware.ts").write_text(
                "function warnIfPreviewBasicAuthLeakedIntoProduction(): void {\n"
                '  if (process.env.VERCEL_ENV === "production") {\n'
                "    const leaked = process.env.PREVIEW_BASIC_AUTH_PASSWORD;\n"
                "    void leaked;\n"
                "  }\n"
                "}\n",
                encoding="utf-8",
            )
            module.REPO_ROOT = fake_repo
            module.WEB_SRC = fake_web
            violations = module.audit_repo_guards()
    finally:
        module.REPO_ROOT = original_repo_root
        module.WEB_SRC = original_web_src
    assert not violations, "production leak detector should be accepted: " + "\n".join(violations)


def test_release_audit_rejects_basic_auth_reads_in_other_production_code() -> None:
    """A production equality block is not a blanket exception for Basic Auth vars."""
    violations = _audit_snippet(
        'if (process.env.VERCEL_ENV === "production") {\n'
        "  const password = process.env.PREVIEW_BASIC_AUTH_PASSWORD;\n"
        "  void password;\n"
        "}\n"
    )
    assert any("PREVIEW_BASIC_AUTH_PASSWORD" in violation for violation in violations)


def test_vercel_system_bypass_is_not_reported_as_a_production_leak() -> None:
    """Vercel injects its automation bypass system variable into every deployment."""
    middleware = (REPO_ROOT / "web" / "src" / "middleware.ts").read_text(encoding="utf-8")
    assert 'leaked.push("VERCEL_AUTOMATION_BYPASS_SECRET")' not in middleware
    assert "Vercel injects" in middleware

    checklist = _load_module().CHECKLIST
    must_not_section = checklist.split("Production MUST NOT have:", 1)[1].split(
        "If either is set", 1
    )[0]
    assert "VERCEL_AUTOMATION_BYPASS_SECRET" not in must_not_section
    assert "Its presence at\n      production runtime is expected" in checklist
    assert "Sensitive Vercel variables are intentionally non-readable" in checklist


def test_release_checklist_branches_on_package_changes() -> None:
    """Web/ops cutovers must not accidentally create a PyPI release tag."""
    checklist = _load_module().CHECKLIST
    assert "git diff vX.Y.Z..main -- src/coarse/" in checklist
    assert "If non-empty: this is a package release" in checklist
    assert "If empty: this is web/deploy/ops-only" in checklist
    assert "Do NOT bump, tag, or publish" in checklist
