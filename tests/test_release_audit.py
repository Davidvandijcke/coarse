"""CI-time drift guard for the dev -> main release audit.

``scripts/release_audit.py`` is the operator-facing pre-release helper.
Its repo-local check is cheap and deterministic, so we also run it
inside pytest on every commit to catch the case where someone adds a
new ``process.env.PREVIEW_BASIC_AUTH_PASSWORD`` or
``process.env.VERCEL_AUTOMATION_BYPASS_SECRET`` read without gating it
behind a ``VERCEL_ENV === "preview"`` check. Without this test, such
a regression would silently ship and only be caught during the next
manual release audit.
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


def test_release_audit_clean_on_dev() -> None:
    """Every preview-only env var read in web/src must be VERCEL_ENV-guarded."""
    module = _load_module()
    violations = module.audit_repo_guards()
    assert not violations, (
        "release_audit found unguarded reads of preview-only env vars. "
        "Every `process.env.PREVIEW_BASIC_AUTH_PASSWORD`, "
        "`process.env.PREVIEW_BASIC_AUTH_USERNAME`, or "
        "`process.env.VERCEL_AUTOMATION_BYPASS_SECRET` in web/src must "
        'be within 10 lines of a `VERCEL_ENV === "preview"` (or the '
        "`warnIfPreviewVarsLeakedIntoProduction` helper) so production "
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
