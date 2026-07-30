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

1. **Repo-local**: every protected environment-variable read is
   lexically contained by an explicit ``VERCEL_ENV`` block. The check
   recognizes direct dot-property ``process.env`` access and rejects
   bracket/computed access or aliases it cannot prove safe. This keeps the
   system-managed bypass secret from activating preview behavior on
   production by accident.

2. **Manual checklist**: prints the Vercel / Modal / Supabase
   verification steps the operator still needs to run by hand
   (since this script has no credentials for those services).

Exit codes:
    0 — repo-local checks passed, manual checklist printed
    1 — repo-local guard violation (preview-gated var referenced
        outside an explicit ``VERCEL_ENV === "preview"`` block)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_SRC = REPO_ROOT / "web" / "src"

PREVIEW_GATED_VARS = (
    "PREVIEW_BASIC_AUTH_PASSWORD",
    "PREVIEW_BASIC_AUTH_USERNAME",
    "VERCEL_AUTOMATION_BYPASS_SECRET",
)

# The system bypass secret may only be consumed inside an exact preview
# equality block. Preview Basic Auth vars additionally appear in the
# production-only leak detector, so those two vars may also sit inside an
# exact production equality block. We deliberately reject aliases and
# early-return/proximity patterns: a conservative false positive is safer
# than accepting a comment, a closed branch, or an unrelated nearby check.
ENV_GUARD_PATTERN = re.compile(
    r"if\s*\(\s*process\.env\.VERCEL_ENV\s*===\s*"
    r"(?P<quote>[\"'])(?P<environment>preview|production)(?P=quote)\s*\)\s*\{",
    re.MULTILINE,
)
PROCESS_ENV_BASE = r"process\s*(?:(?:\?\s*)?\.\s*env|\[\s*[\"']env[\"']\s*\])(?![\w$])"
DOT_READ_PATTERN = re.compile(
    PROCESS_ENV_BASE
    + r"\s*(?:\?\s*)?\.\s*(?P<variable>"
    + "|".join(re.escape(var) for var in PREVIEW_GATED_VARS)
    + r")\b"
)
BRACKET_READ_PATTERN = re.compile(
    PROCESS_ENV_BASE
    + r"\s*\[\s*(?P<quote>[\"'])(?P<variable>"
    + "|".join(re.escape(var) for var in PREVIEW_GATED_VARS)
    + r")(?P=quote)\s*\]"
)
# Bracket access is forbidden outright. Even a literal-looking key can be
# turned into an expression (``"PREFIX_" + suffix``), and process["env"]
# creates another alias surface. The web tree currently needs neither form.
BRACKET_ENV_KEY_PATTERN = re.compile(r"process\s*(?:\?\s*)?\.\s*env(?![\w$])\s*\[")
BRACKET_ENV_OBJECT_PATTERN = re.compile(r"process\s*\[\s*[\"']env[\"']\s*\]")
# Only a direct static property may follow the global process.env object.
# Passing, spreading, parenthesizing, destructuring, or assigning the whole
# object creates an alias the text audit cannot follow.
BARE_PROCESS_ENV_PATTERN = re.compile(PROCESS_ENV_BASE + r"(?!\s*(?:\?\s*)?\.\s*[A-Za-z_$])")
# Any import/require of the process module creates an alias surface that this
# lightweight source audit cannot safely follow (named, default, namespace,
# dynamic, and CommonJS imports all expose ``env``). The web tree does not need
# this module, so fail closed instead of trying to enumerate local alias names.
PROCESS_MODULE_REFERENCE_PATTERN = re.compile(
    r"(?:\bfrom\s*|\bimport\s*\(|\brequire\s*\()"
    r"[\"'](?:node:)?process[\"']",
    re.MULTILINE,
)
PROCESS_OBJECT_ENV_ALIAS_PATTERN = re.compile(
    r"\{[^}]*\benv\b[^}]*\}\s*=\s*process\b",
    re.MULTILINE,
)
PROTECTED_KEY_BRACKET_PATTERN = re.compile(
    r"\[\s*[\"'](?P<variable>" + "|".join(re.escape(var) for var in PREVIEW_GATED_VARS) + r")[\"']"
)
ENV_ALIAS_PATTERN = re.compile(
    r"\b(?:const|let|var)\s+[A-Za-z_$][\w$]*\s*=\s*" + PROCESS_ENV_BASE + r"(?!\s*[?.\[])"
)
DESTRUCTURE_PATTERN = re.compile(
    r"\{(?P<body>[^{}]{0,1000})\}\s*=\s*" + PROCESS_ENV_BASE,
    re.MULTILINE,
)


def _is_source_file(path: Path) -> bool:
    return path.suffix in {".ts", ".tsx", ".js", ".mjs", ".cjs"}


def _lexical_masks(source: str) -> tuple[list[bool], list[bool]]:
    """Return masks for non-comment text and structural JavaScript code.

    The first mask excludes comments but intentionally retains string/template
    contents. That makes the detector conservative: a string containing a
    literal ``process.env.SECRET`` is reported instead of silently masking a
    template interpolation. The second mask also excludes quoted contents and
    is used only for brace matching, so braces in messages cannot forge a
    containing guard block.
    """

    non_comment = [True] * len(source)
    structural = [False] * len(source)
    state = "code"
    quote = ""
    regex_character_class = False
    index = 0
    while index < len(source):
        char = source[index]
        next_char = source[index + 1] if index + 1 < len(source) else ""
        if state == "code":
            if char == "/" and next_char == "/":
                non_comment[index] = non_comment[index + 1] = False
                state = "line_comment"
                index += 2
                continue
            if char == "/" and next_char == "*":
                non_comment[index] = non_comment[index + 1] = False
                state = "block_comment"
                index += 2
                continue
            if char == "/":
                previous = index - 1
                while previous >= 0 and source[previous].isspace():
                    previous -= 1
                # JavaScript regex literals are context-sensitive. All guard
                # spoofing shapes begin an expression (most commonly after
                # ``=``); treating those as non-structural prevents a regex's
                # text and braces from forging a control-flow block.
                if previous < 0 or source[previous] in "=(:,![{;?":
                    state = "regex"
                    regex_character_class = False
                    index += 1
                    continue
            if char in {"'", '"', "`"}:
                quote = char
                state = "string"
                index += 1
                continue
            structural[index] = True
            index += 1
            continue
        if state == "line_comment":
            non_comment[index] = False
            if char == "\n":
                state = "code"
                structural[index] = True
            index += 1
            continue
        if state == "block_comment":
            non_comment[index] = False
            if char == "*" and next_char == "/":
                non_comment[index + 1] = False
                index += 2
                state = "code"
                continue
            index += 1
            continue
        if state == "regex":
            if char == "\\":
                index += 2
                continue
            if char == "[":
                regex_character_class = True
            elif char == "]":
                regex_character_class = False
            elif char == "/" and not regex_character_class:
                state = "code"
            index += 1
            continue
        # Quoted string or template literal. Escaped delimiters do not end it.
        if char == "\\":
            index += 2
            continue
        if char == quote:
            state = "code"
        index += 1
    return non_comment, structural


def _matching_brace(source: str, structural: list[bool], opening: int) -> int | None:
    depth = 0
    for index in range(opening, len(source)):
        if not structural[index]:
            continue
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    return None


def _guard_ranges(source: str, structural: list[bool]) -> list[tuple[int, int, str]]:
    ranges: list[tuple[int, int, str]] = []
    for match in ENV_GUARD_PATTERN.finditer(source):
        previous = match.start() - 1
        while previous >= 0 and source[previous].isspace():
            previous -= 1
        # A real statement-level ``if`` starts the file or follows a block /
        # statement boundary. This rejects guard-shaped text in regex literals
        # even in contexts where the lightweight lexer cannot infer that a
        # slash after ``yield``, ``return``, or a condition begins a regex.
        if previous >= 0 and source[previous] not in "{;}":
            continue
        opening = source.find("{", match.start(), match.end())
        if opening < 0 or not structural[match.start()] or not structural[opening]:
            continue
        closing = _matching_brace(source, structural, opening)
        if closing is not None:
            ranges.append((opening, closing, match.group("environment")))
    return ranges


def _named_function_range(
    source: str, structural: list[bool], function_name: str
) -> tuple[int, int] | None:
    pattern = re.compile(
        rf"\bfunction\s+{re.escape(function_name)}\s*\([^)]*\)\s*"
        r"(?:\:\s*[^\{]+)?\{",
        re.MULTILINE,
    )
    match = pattern.search(source)
    if not match or not structural[match.start()]:
        return None
    previous = match.start() - 1
    while previous >= 0 and source[previous].isspace():
        previous -= 1
    if previous >= 0 and source[previous] not in "{;}":
        return None
    opening = source.find("{", match.start(), match.end())
    if opening < 0 or not structural[opening]:
        return None
    closing = _matching_brace(source, structural, opening)
    return (opening, closing) if closing is not None else None


def _is_guarded(
    position: int,
    variable: str,
    ranges: list[tuple[int, int, str]],
    *,
    allow_production_leak_check: bool = False,
) -> bool:
    allowed_environments = {"preview"}
    if variable.startswith("PREVIEW_BASIC_AUTH_") and allow_production_leak_check:
        allowed_environments.add("production")
    return any(
        opening < position < closing and environment in allowed_environments
        for opening, closing, environment in ranges
    )


def _protected_reads(source: str, non_comment: list[bool]) -> list[tuple[int, str]]:
    reads: set[tuple[int, str]] = set()
    for pattern in (DOT_READ_PATTERN, BRACKET_READ_PATTERN):
        for match in pattern.finditer(source):
            if non_comment[match.start()]:
                reads.add((match.start("variable"), match.group("variable")))
    for match in DESTRUCTURE_PATTERN.finditer(source):
        if not non_comment[match.start()]:
            continue
        body = match.group("body")
        body_start = match.start("body")
        for variable in PREVIEW_GATED_VARS:
            variable_match = re.search(rf"\b{re.escape(variable)}\b", body)
            if variable_match:
                reads.add((body_start + variable_match.start(), variable))
    return sorted(reads)


def audit_repo_guards() -> list[str]:
    """Return a list of unguarded preview-var references, or empty list.

    Direct dot-property reads count as references. Plain string literals that
    only mention a variable name are ignored because they do not contain
    ``process.env``; comments are masked. Whole-object, bracket/computed, and
    alias access is rejected because the audit cannot prove which key it
    consumes.
    """
    violations: list[str] = []
    if not WEB_SRC.exists():
        return [f"web/src not found at {WEB_SRC}"]
    for path in sorted(WEB_SRC.rglob("*")):
        if not path.is_file() or not _is_source_file(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        non_comment, structural = _lexical_masks(text)
        ranges = _guard_ranges(text, structural)
        rel = path.relative_to(REPO_ROOT)
        leak_check_range = None
        if rel == Path("web/src/middleware.ts"):
            leak_check_range = _named_function_range(
                text, structural, "warnIfPreviewBasicAuthLeakedIntoProduction"
            )
        for pattern in (BRACKET_ENV_KEY_PATTERN, BRACKET_ENV_OBJECT_PATTERN):
            for match in pattern.finditer(text):
                if not non_comment[match.start()]:
                    continue
                line_number = text.count("\n", 0, match.start()) + 1
                violations.append(
                    f"{rel}:{line_number}: bracket/computed process.env access is forbidden"
                )
        for match in BARE_PROCESS_ENV_PATTERN.finditer(text):
            if non_comment[match.start()]:
                line_number = text.count("\n", 0, match.start()) + 1
                violations.append(
                    f"{rel}:{line_number}: whole process.env object access is forbidden"
                )
        for pattern in (PROCESS_MODULE_REFERENCE_PATTERN, PROCESS_OBJECT_ENV_ALIAS_PATTERN):
            for match in pattern.finditer(text):
                if non_comment[match.start()]:
                    line_number = text.count("\n", 0, match.start()) + 1
                    violations.append(
                        f"{rel}:{line_number}: process environment alias is forbidden"
                    )
        for match in PROTECTED_KEY_BRACKET_PATTERN.finditer(text):
            if non_comment[match.start()]:
                line_number = text.count("\n", 0, match.start()) + 1
                violations.append(
                    f"{rel}:{line_number}: indirect bracket key "
                    f"{match.group('variable')} is forbidden"
                )
        for match in ENV_ALIAS_PATTERN.finditer(text):
            if non_comment[match.start()]:
                line_number = text.count("\n", 0, match.start()) + 1
                violations.append(f"{rel}:{line_number}: process.env alias cannot be audited")
        protected_reads = _protected_reads(text, non_comment)
        protected_read_positions = {position for position, _ in protected_reads}
        for variable in PREVIEW_GATED_VARS:
            for match in re.finditer(rf"\b{re.escape(variable)}\b", text):
                position = match.start()
                if structural[position] and position not in protected_read_positions:
                    line_number = text.count("\n", 0, position) + 1
                    violations.append(
                        f"{rel}:{line_number}: indirect {variable} reference cannot be audited"
                    )
        for position, variable in protected_reads:
            allow_production_leak_check = bool(
                leak_check_range and leak_check_range[0] < position < leak_check_range[1]
            )
            if _is_guarded(
                position,
                variable,
                ranges,
                allow_production_leak_check=allow_production_leak_check,
            ):
                continue
            line_number = text.count("\n", 0, position) + 1
            violations.append(
                f"{rel}:{line_number}: process.env.{variable} read outside an "
                "explicit VERCEL_ENV equality block"
            )
    return violations


CHECKLIST = """
=====================================================================
  coarse — dev -> main release audit checklist
=====================================================================

  Run this script before a production cutover. It verifies the repo side
  automatically and then prints the manual steps you still need to run
  against Vercel, Modal, and Supabase. Tag only when package code changed.

  The preview gate, preview Supabase URL, and preview Modal environment
  are environment-scoped. Vercel's automation bypass secret is a
  platform-managed system variable present in every deployment when
  that feature is enabled; production safety comes from application
  reads being gated by `VERCEL_ENV === "preview"`. Verify all of the
  below before you tag.

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

      If either is set on Production, the middleware logs a loud
      [release-audit] console.error once per cold start. Watch Vercel
      runtime logs after the first production deploy and unset only
      the listed Basic Auth variables if that warning appears.

      `VERCEL_AUTOMATION_BYPASS_SECRET` is different: Vercel injects
      it as a system environment variable into all deployments when
      Protection Bypass for Automation is configured. Its presence at
      production runtime is expected and is NOT a leak. Do not disable
      the preview bypass to clear it; the repo-local guard above proves
      that application behavior remains preview-only.

      Sensitive Vercel variables are intentionally non-readable and
      may pull as blank. Validate their configured presence and runtime
      behavior; do not delete/recreate a secret solely because
      `vercel env pull` cannot return its value.

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

  [ ] Run `git diff vX.Y.Z..main -- src/coarse/` using the latest release tag.
      - If non-empty: this is a package release. Bump pyproject.toml and
        src/coarse/__init__.py, then move Unreleased to `## vX.Y.Z — DATE`.
      - If empty: this is web/deploy/ops-only. Do NOT bump, tag, or publish.
  [ ] Merge the release PR to main.
  [ ] Package release only: tag/push vX.Y.Z from main and watch the
      `Release` workflow. Web/deploy/ops-only cutovers stop after main deploys.
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
        print("\nFAIL: preview-gated variables referenced without a valid VERCEL_ENV block:")
        for v in violations:
            print(f"  - {v}")
        print(
            "\nEvery VERCEL_AUTOMATION_BYPASS_SECRET read must be inside "
            'a `VERCEL_ENV === "preview"` branch. Preview Basic Auth reads '
            "must be preview-gated or belong to the production-only leak "
            "detector. Fix the violations above and re-run this script.",
        )
        return 1
    print("OK: all references to preview-gated env vars are guarded.\n")
    print(CHECKLIST)
    return 0


if __name__ == "__main__":
    sys.exit(main())
