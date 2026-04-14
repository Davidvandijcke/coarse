#!/usr/bin/env python3
"""Pre-release audit for the dev -> main cutover.

Prints a checklist of environment-scoped settings that need to be
verified before cutting a production release. No action is taken —
this script only reads from the local repo and optionally from the
Vercel / Modal CLIs (if they are installed and authenticated) so it
is safe to run repeatedly.

Usage:
    python3 scripts/release_audit.py          # checklist + local checks
    make release-audit                        # same, via Makefile

What this script verifies:

1. **Repo-local**: every preview-specific config path is guarded by
   an explicit ``VERCEL_ENV`` / ``NODE_ENV`` check. Greps the web
   source tree for ``PREVIEW_BASIC_AUTH_PASSWORD`` and
   ``VERCEL_AUTOMATION_BYPASS_SECRET`` and confirms every hit is
   accompanied by a ``VERCEL_ENV === "preview"`` guard within a
   small window (so no code path activates these on production by
   accident).

2. **Manual checklist**: prints the Vercel / Modal / Supabase
   verification steps the operator still needs to run by hand
   (since this script has no credentials for those services).

Exit codes:
    0 — repo-local checks passed, manual checklist printed
    1 — repo-local guard violation (preview-only var referenced
        without a ``VERCEL_ENV === "preview"`` check nearby)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_SRC = REPO_ROOT / "web" / "src"

PREVIEW_ONLY_VARS = (
    "PREVIEW_BASIC_AUTH_PASSWORD",
    "PREVIEW_BASIC_AUTH_USERNAME",
    "VERCEL_AUTOMATION_BYPASS_SECRET",
)

# Lines that reference a preview-only var are allowed if any of these
# guard patterns appears within ``GUARD_WINDOW`` lines around the hit.
GUARD_PATTERNS = (
    re.compile(r'VERCEL_ENV\s*[!=]==?\s*["\']preview["\']'),
    re.compile(r'VERCEL_ENV\s*[!=]==?\s*["\']production["\']'),
    # A release-audit warning function counts as a guard — its whole
    # job is to notice these vars leaking into production.
    re.compile(r"warnIfPreviewVarsLeakedIntoProduction"),
    # Documentation files are allowed to reference the vars freely.
)
GUARD_WINDOW = 10


def _is_source_file(path: Path) -> bool:
    return path.suffix in {".ts", ".tsx", ".js", ".mjs", ".cjs"}


def _check_guard(lines: list[str], hit_idx: int) -> bool:
    lo = max(0, hit_idx - GUARD_WINDOW)
    hi = min(len(lines), hit_idx + GUARD_WINDOW + 1)
    window = "\n".join(lines[lo:hi])
    return any(pat.search(window) for pat in GUARD_PATTERNS)


def audit_repo_guards() -> list[str]:
    """Return a list of unguarded preview-var references, or empty list.

    Only real ``process.env.<VAR>`` reads count as references. String
    literals that happen to mention the variable name (warning text,
    error messages, doc comments) are not references and are skipped —
    otherwise every line that explains a guard would itself be flagged.
    """
    violations: list[str] = []
    if not WEB_SRC.exists():
        return [f"web/src not found at {WEB_SRC}"]
    real_read_patterns = [
        (var, re.compile(rf"process\.env\.{re.escape(var)}\b")) for var in PREVIEW_ONLY_VARS
    ]
    for path in sorted(WEB_SRC.rglob("*")):
        if not path.is_file() or not _is_source_file(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        lines = text.splitlines()
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            for var, pat in real_read_patterns:
                if not pat.search(line):
                    continue
                if _check_guard(lines, idx):
                    continue
                rel = path.relative_to(REPO_ROOT)
                violations.append(
                    f"{rel}:{idx + 1}: process.env.{var} read without a "
                    f"VERCEL_ENV guard within {GUARD_WINDOW} lines"
                )
    return violations


CHECKLIST = """
=====================================================================
  coarse — dev -> main release audit checklist
=====================================================================

  Run this script before tagging vX.Y.Z. It verifies the repo side is
  clean automatically and then prints the manual steps you still need
  to run against Vercel, Modal, and Supabase.

  The preview gate, bypass secret, preview Supabase URL, and preview
  Modal environment are all *environment-scoped* — production code
  paths check `VERCEL_ENV === "preview"` before activating anything
  preview-specific, so in theory a `dev -> main` merge needs no code
  change. In practice, the dashboard side can drift. Verify all of
  the below before you tag.

--- Vercel (production environment) -------------------------------

  [ ] Vercel -> Project -> Settings -> Environment Variables ->
      Production should have:
         - NEXT_PUBLIC_SUPABASE_URL         = https://dgibkmnyiusglhdgzffk.supabase.co
         - NEXT_PUBLIC_SUPABASE_ANON_KEY    = <production anon key>
         - SUPABASE_SERVICE_KEY             = <production service key>
         - MODAL_FUNCTION_URL               = <production coarse-review webhook>
         - MODAL_WEBHOOK_SECRET             = <production secret>
         - RESEND_API_KEY                   = <production Resend key>
         - NEXT_PUBLIC_SITE_URL             = https://coarse.ink
         - NEXT_PUBLIC_TURNSTILE_SITE_KEY   = <production site key>
         - TURNSTILE_SECRET_KEY             = <production secret>

      (`MODAL_EXTRACT_URL` used to be required by the MCP path but
      was retired in v1.3.0. Safe to delete from Production if still
      present.)

  [ ] Vercel -> Project -> Settings -> Environment Variables ->
      Production MUST NOT have:
         - PREVIEW_BASIC_AUTH_USERNAME
         - PREVIEW_BASIC_AUTH_PASSWORD
         - VERCEL_AUTOMATION_BYPASS_SECRET    (Vercel writes this
           automatically into Preview when Protection Bypass for
           Automation is enabled; it should never appear on Production)

      If any of these are set on Production, the middleware logs a
      loud [release-audit] console.error on every cold start. Watch
      Vercel runtime logs after the first production deploy of the
      release — if that line appears, go unset the leaked var.

  [ ] Vercel -> Project -> Settings -> Deployment Protection ->
      Production Deployment: must be "Public" (unprotected). Only
      Preview should have any protection layer enabled.

--- Modal (production / default environment) ----------------------

  [ ] `modal app list` (or dashboard -> default environment):
         - coarse-review should be deployed from main
         - coarse-mcp    should NOT be present (retired in v1.3.0;
           run `modal app stop coarse-mcp` if still deployed)
         - No app should be in the `preview` environment alone

  [ ] `modal secret list`: production `coarse-supabase`,
      `coarse-webhook`, `coarse-resend` should all exist in the
      default environment and contain production values.

--- Supabase ------------------------------------------------------

  [ ] Production Supabase project `dgibkmnyiusglhdgzffk` is the one
      referenced from Vercel Production env vars (see above).

  [ ] `deploy/*.sql` migrations that were applied to preview during
      the dev cycle are also applied to production BEFORE the first
      post-release user traffic lands. Check against CHANGELOG
      `### Added` / `### Changed` entries for this release.

--- Final ---------------------------------------------------------

  [ ] Bump version in pyproject.toml and src/coarse/__init__.py.
  [ ] Move CHANGELOG.md `## Unreleased` -> `## vX.Y.Z — YYYY-MM-DD`.
  [ ] Merge the release PR to main.
  [ ] `git checkout main && git pull && git tag vX.Y.Z && git push origin vX.Y.Z`.
  [ ] Watch the `Release` workflow in GitHub Actions for the tag push.
  [ ] After deploy, watch Vercel runtime logs for any
      `[release-audit]` warnings — if you see one, fix the dashboard
      env var and redeploy.
  [ ] Smoke-test: hit https://coarse.ink/ in incognito and confirm
      no Basic Auth prompt, no preview banner, and the form submits.

=====================================================================
"""


def main() -> int:
    print("Running repo-local guard check...", flush=True)
    violations = audit_repo_guards()
    if violations:
        print("\nFAIL: preview-only variables referenced without a VERCEL_ENV guard:")
        for v in violations:
            print(f"  - {v}")
        print(
            "\nEvery reference to PREVIEW_BASIC_AUTH_PASSWORD / "
            "VERCEL_AUTOMATION_BYPASS_SECRET must be inside a "
            '`VERCEL_ENV === "preview"` branch so production code '
            "paths cannot activate them. Fix the violations above "
            "and re-run this script.",
        )
        return 1
    print("OK: all references to preview-only env vars are guarded.\n")
    print(CHECKLIST)
    return 0


if __name__ == "__main__":
    sys.exit(main())
