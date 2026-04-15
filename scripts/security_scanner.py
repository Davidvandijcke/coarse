#!/usr/bin/env python3
"""Security scanner for the coarse repo.

Scans for:
  1. Known leaked secret fingerprints (CRITICAL if found outside env files)
  2. Generic provider key patterns (OpenAI/Anthropic/Google/OpenRouter/etc.)
  3. Insecure .env file permissions (should be 0o600)
  4. Hardcoded model-ID string literals outside src/coarse/models.py
  5. Real secrets masquerading as placeholders in .env.example

Zero external deps: stdlib only. Runs in under a second on coarse.
Runnable from CI, pre-commit, and the /security-review slash command.

Exit codes:
    0  clean (or only MEDIUM/LOW/INFO findings)
    1  scanner error
    2  CRITICAL (always) or HIGH (only with --strict) findings present

Suppression: add a trailing `# security: ignore` comment on any line to
suppress findings on that line. Whole files can be exempted by adding their
repo-relative path to SELF_EXEMPT_PATHS below.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Paths where real secrets are allowed to live (all gitignored env files).
ALLOWED_SECRET_PATHS = {
    ".env",
    ".env.local",
    "web/.env",
    "web/.env.local",
    "web/.env.development.local",
    "web/.env.production.local",
}

# Directories never walked.
SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".ruff_cache",
    ".pytest_cache",
    ".mypy_cache",
    ".next",
    ".vercel",
    ".modal",
    ".coarse",
    "reviews",
    "data",
    ".extraction_cache",
    # Claude Code ephemeral worktrees created by /worktree-start. Each
    # worktree has its own .claude/settings.local.json that records
    # every bash command the agent approved, including occasional
    # `export OPENROUTER_API_KEY=sk-or-v1-...` lines. The whole
    # `.claude/worktrees/` tree is gitignored (see .gitignore line
    # `.claude/*` + explicit allowlist), so secrets in those files
    # cannot reach git — but the scanner was walking them anyway and
    # blocking unrelated commits. Skip at the directory-name level so
    # any `worktrees/` subtree in the repo is ignored.
    "worktrees",
}

# Extensions worth opening.
TEXT_EXTS = {
    ".py",
    ".pyi",
    ".sh",
    ".bash",
    ".zsh",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".json",
    ".jsonc",
    ".yaml",
    ".yml",
    ".toml",
    ".md",
    ".mdx",
    ".txt",
    ".rst",
    ".html",
    ".css",
    ".scss",
    ".ini",
    ".cfg",
    ".conf",
}

# Extensionless or dotfile names to also scan.
TEXT_BASENAMES = {
    "Makefile",
    "Dockerfile",
    ".gitignore",
    ".env",
    ".env.example",
    ".env.local",
    ".env.production",
    ".env.production.local",
    ".env.development",
    ".env.development.local",
}

MAX_FILE_SIZE = 500_000

# Paths where the scanner's own signatures live, so the scanner doesn't flag
# itself. Paths here are repo-relative posix strings.
SELF_EXEMPT_PATHS = {
    "scripts/security_scanner.py",
    "tests/test_security.py",
}

# Inline suppression marker.
IGNORE_MARKER = "security: ignore"

# ---------------------------------------------------------------------------
# Signatures
# ---------------------------------------------------------------------------

# Known leaked fingerprints, stored as SHA-256 hashes so the scanner itself
# never ships the plaintext secret. If a token in a scanned line hashes to
# one of these values it is flagged CRITICAL regardless of context (unless
# the file is in ALLOWED_SECRET_PATHS).
#
# To register a new leaked key, compute its hash locally:
#   python3 -c 'import hashlib, sys; print(hashlib.sha256(sys.argv[1].encode()).hexdigest())' "$KEY"
# then add the hash below. NEVER paste the plaintext key into this file.
LEAKED_FINGERPRINT_HASHES: dict[str, str] = {
    # Scrubbed from .claude/settings.local.json on 2026-04-10.
    "42bd174bc504f8f76c9bad6b330b69f4c2a714fc16ece57b25777d0801ba97db": "Supabase service-role key",
    "b656462688773c2f4a33370e556088dcb3fa4dcd97b5ef2274af8e2239e2526c": "OpenRouter API key",
}

# Tokenizer used to extract candidate secret strings for hash matching.
# Matches runs of identifier-like chars (letters, digits, underscore, hyphen,
# period) of length >= 20 — long enough to cover every real provider key
# format while skipping common words.
_TOKEN_RE = re.compile(r"[A-Za-z0-9_.\-]{20,}")


def _fingerprint_hits(line: str) -> list[str]:
    """Return labels of any leaked fingerprint whose hash matches a token
    in this line. Empty list if nothing matches."""
    hits: list[str] = []
    for token in _TOKEN_RE.findall(line):
        h = hashlib.sha256(token.encode("utf-8")).hexdigest()
        label = LEAKED_FINGERPRINT_HASHES.get(h)
        if label:
            hits.append(label)
    return hits


# Generic provider key patterns. Matches outside ALLOWED_SECRET_PATHS are HIGH
# unless a placeholder marker is present on the same line.
PROVIDER_PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    ("OpenAI key", re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{32,}"), "OPENAI_API_KEY"),
    ("OpenRouter key", re.compile(r"sk-or-v1-[a-f0-9]{40,}"), "OPENROUTER_API_KEY"),
    ("Anthropic key", re.compile(r"sk-ant-[A-Za-z0-9_-]{40,}"), "ANTHROPIC_API_KEY"),
    ("Google AI key", re.compile(r"AIza[A-Za-z0-9_-]{35}"), "GEMINI_API_KEY"),
    ("Perplexity key", re.compile(r"pplx-[A-Za-z0-9]{32,}"), "PERPLEXITY_API_KEY"),
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"), "GITHUB_TOKEN"),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS_ACCESS_KEY_ID"),
    ("Supabase secret", re.compile(r"\bsb_secret_[A-Za-z0-9_]{20,}"), "SUPABASE_SERVICE_ROLE_KEY"),
    ("Stripe key", re.compile(r"\bsk_(?:test|live)_[A-Za-z0-9]{24,}"), "STRIPE_SECRET_KEY"),
    (
        "Private key block",
        re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----"),
        "PRIVATE_KEY",
    ),
    (
        "URL-embedded credentials",
        re.compile(r"[a-zA-Z][a-zA-Z0-9+.-]*://[^\s:/@]+:[^\s@/]{4,}@"),
        "URL_CREDS",
    ),
]

# Lowercased substrings that downgrade a provider-key match to a placeholder.
PLACEHOLDER_MARKERS = (
    "xxxxxxxx",
    "your_key",
    "your-key",
    "your_api_key",
    "your-api-key",
    "example",
    "placeholder",
    "changeme",
    "replace_me",
    "<your",
    "dummy",
    "sk-or-v1-aaaa",
    "sk-or-v1-0000",
    "sk-or-v1-xxxx",
    "sk-ant-xxxx",
    "sk-proj-xxxx",
    "aizax",
    "pplx-xxxx",
    "fake",
    "test_key",
    "test-key",
)

# Any "<provider>/<id>" string literal in src/coarse/ outside models.py is a
# violation of the "model IDs live in models.py only" rule from CLAUDE.md.
# Excludes `<provider>/auto` which is a routing hint used by resolve_api_key.
MODEL_ID_PATTERN = re.compile(
    r'["\'](?:openai|anthropic|google|gemini|perplexity|mistral|qwen|openrouter|'
    r"deepseek|moonshotai|kimi|groq|together|xai|cohere)/"
    r'(?!auto["\'])[A-Za-z0-9._-]+["\']'
)

# ---------------------------------------------------------------------------
# Finding
# ---------------------------------------------------------------------------


@dataclass
class Finding:
    severity: str
    kind: str
    path: str
    line: int
    message: str
    excerpt: str = ""

    def fmt(self) -> str:
        loc = f"{self.path}:{self.line}" if self.line else self.path
        head = f"[{self.severity}] {self.kind}  {loc}"
        body = f"  {self.message}"
        tail = f"\n  > {self.excerpt}" if self.excerpt else ""
        return f"{head}\n{body}{tail}"


SEVERITY_RANK = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}

# ---------------------------------------------------------------------------
# Walk helpers
# ---------------------------------------------------------------------------


def _should_scan(path: Path) -> bool:
    if path.name in TEXT_BASENAMES:
        return True
    return path.suffix in TEXT_EXTS


def _iter_files(root: Path):
    """Yield every scannable file under root, including .claude/ and .github/."""
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = Path(dirpath).relative_to(root)
        # prune unwanted directories but keep .claude/ and .github/ (dot dirs)
        pruned = []
        for d in dirnames:
            if d in SKIP_DIRS:
                continue
            if d.startswith(".") and d not in {".claude", ".github"}:
                continue
            pruned.append(d)
        dirnames[:] = pruned
        for name in filenames:
            p = Path(dirpath) / name
            if not _should_scan(p):
                continue
            try:
                if p.stat().st_size > MAX_FILE_SIZE:
                    continue
            except OSError:
                continue
            yield p, rel_dir / name


def _read_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []


def _excerpt(line: str, maxlen: int = 140) -> str:
    s = line.strip()
    return s if len(s) <= maxlen else s[:maxlen] + "…"


def _is_allowed_secret_path(rel: Path) -> bool:
    rel_s = rel.as_posix()
    return rel_s in ALLOWED_SECRET_PATHS


# ---------------------------------------------------------------------------
# Scanners
# ---------------------------------------------------------------------------


def scan_secrets(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for abs_path, rel in _iter_files(root):
        rel_s = rel.as_posix()
        if rel_s in SELF_EXEMPT_PATHS:
            continue
        allowed = _is_allowed_secret_path(rel)
        for i, line in enumerate(_read_lines(abs_path), start=1):
            if IGNORE_MARKER in line:
                continue
            if not allowed:
                for label in _fingerprint_hits(line):
                    findings.append(
                        Finding(
                            severity="CRITICAL",
                            kind="leaked-fingerprint",
                            path=rel_s,
                            line=i,
                            message=f"Known leaked {label} present outside allowed env files",
                            excerpt=_excerpt(line),
                        )
                    )
            if allowed:
                continue
            lower = line.lower()
            if any(ph in lower for ph in PLACEHOLDER_MARKERS):
                continue
            for label, rx, envname in PROVIDER_PATTERNS:
                if not rx.search(line):
                    continue
                findings.append(
                    Finding(
                        severity="HIGH",
                        kind="secret-pattern",
                        path=rel_s,
                        line=i,
                        message=f"{label} literal — move to {envname} env var",
                        excerpt=_excerpt(line),
                    )
                )
                break
    return findings


def scan_env_permissions(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for rel_s in ALLOWED_SECRET_PATHS:
        p = root / rel_s
        if not p.exists() or not p.is_file():
            continue
        mode = p.stat().st_mode & 0o777
        if mode & 0o077:
            findings.append(
                Finding(
                    severity="HIGH",
                    kind="env-perm",
                    path=rel_s,
                    line=0,
                    message=f"mode {oct(mode)} is group/other-readable; run: chmod 600 {rel_s}",
                )
            )
    return findings


def _docstring_line_numbers(source: str) -> set[int]:
    """Return the set of line numbers that fall inside a docstring.

    Uses the ast module so only genuine module/class/function docstrings count,
    and string *values* (dict keys, function arguments) are not treated as
    docstrings. Falls back to an empty set if the file cannot be parsed.
    """
    import ast

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    inside: set[int] = set()

    def _maybe_add(node: ast.AST) -> None:
        body = getattr(node, "body", None)
        if not body:
            return
        first = body[0]
        if (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            start = first.lineno
            end = getattr(first, "end_lineno", start) or start
            for ln in range(start, end + 1):
                inside.add(ln)

    _maybe_add(tree)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            _maybe_add(node)
    return inside


def scan_model_id_literals(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    src = root / "src" / "coarse"
    if not src.exists():
        return findings
    for path in sorted(src.rglob("*.py")):
        rel = path.relative_to(root)
        if rel.as_posix() == "src/coarse/models.py":
            continue
        source = path.read_text(encoding="utf-8", errors="replace")
        docstring_lines = _docstring_line_numbers(source)
        for i, line in enumerate(source.splitlines(), start=1):
            if i in docstring_lines:
                continue
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            if IGNORE_MARKER in line:
                continue
            if MODEL_ID_PATTERN.search(line):
                findings.append(
                    Finding(
                        severity="MEDIUM",
                        kind="hardcoded-model-id",
                        path=rel.as_posix(),
                        line=i,
                        message="Model ID literal outside src/coarse/models.py",
                        excerpt=_excerpt(line),
                    )
                )
    return findings


def scan_env_example(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    example = root / ".env.example"
    if not example.exists():
        return findings
    rel = example.relative_to(root).as_posix()
    for i, line in enumerate(_read_lines(example), start=1):
        if IGNORE_MARKER in line:
            continue
        for label in _fingerprint_hits(line):
            findings.append(
                Finding(
                    severity="CRITICAL",
                    kind="env-example-leaked",
                    path=rel,
                    line=i,
                    message=f"Real {label} in .env.example — replace with placeholder",
                    excerpt=_excerpt(line),
                )
            )
        lower = line.lower()
        if any(ph in lower for ph in PLACEHOLDER_MARKERS):
            continue
        for label, rx, _ in PROVIDER_PATTERNS:
            if rx.search(line):
                findings.append(
                    Finding(
                        severity="HIGH",
                        kind="env-example-real-secret",
                        path=rel,
                        line=i,
                        message=(
                            f"{label} in .env.example looks real (no placeholder marker on line)"
                        ),
                        excerpt=_excerpt(line),
                    )
                )
                break
    return findings


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def print_human(findings: list[Finding]) -> None:
    if not findings:
        print("security: clean")
        return
    findings.sort(key=lambda f: (SEVERITY_RANK.get(f.severity, 9), f.path, f.line))
    for f in findings:
        print(f.fmt())
        print()
    counts = {
        sev: sum(1 for f in findings if f.severity == sev)
        for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW")
    }
    summary = " ".join(f"{k}={v}" for k, v in counts.items())
    print(f"security: {len(findings)} finding(s)  [{summary}]")


def print_json(findings: list[Finding]) -> None:
    payload = {
        "findings": [asdict(f) for f in findings],
        "counts": {
            sev: sum(1 for f in findings if f.severity == sev)
            for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")
        },
    }
    print(json.dumps(payload, indent=2))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

ALL_SCOPES = ("secrets", "perms", "model-ids", "env-example")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Zero-dep security scanner for coarse",
    )
    ap.add_argument(
        "--root", type=Path, default=REPO_ROOT, help="Repo root to scan (default: auto-detect)."
    )
    ap.add_argument("--json", action="store_true", help="Emit JSON for CI.")
    ap.add_argument(
        "--strict",
        action="store_true",
        help="Exit 2 on HIGH findings (default: only CRITICAL blocks).",
    )
    ap.add_argument(
        "--scope",
        default=",".join(ALL_SCOPES),
        help=f"Comma-separated scopes: {','.join(ALL_SCOPES)}",
    )
    args = ap.parse_args(argv)

    scopes = {s.strip() for s in args.scope.split(",") if s.strip()}
    unknown = scopes - set(ALL_SCOPES)
    if unknown:
        print(f"unknown scope(s): {sorted(unknown)}", file=sys.stderr)
        return 1

    findings: list[Finding] = []
    try:
        if "secrets" in scopes:
            findings.extend(scan_secrets(args.root))
        if "env-example" in scopes:
            findings.extend(scan_env_example(args.root))
        if "perms" in scopes:
            findings.extend(scan_env_permissions(args.root))
        if "model-ids" in scopes:
            findings.extend(scan_model_id_literals(args.root))
    except Exception as exc:  # noqa: BLE001
        print(f"scanner error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print_json(findings)
    else:
        print_human(findings)

    blocking_sevs = {"CRITICAL", "HIGH"} if args.strict else {"CRITICAL"}
    blocking = any(f.severity in blocking_sevs for f in findings)
    return 2 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
