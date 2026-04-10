"""Tests for scripts/security_scanner.py.

The scanner is stdlib-only, so these tests import it via importlib directly
from the scripts directory without adding it to the package.

IMPORTANT: this file must never contain a real API key or a real leaked
fingerprint. Fingerprint tests use a synthetic fake value whose hash is
injected into LEAKED_FINGERPRINT_HASHES via monkeypatch for the test's
lifetime. Pattern tests use strings shaped like provider keys but
constructed from clearly-synthetic alphabets.
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
import sys
from pathlib import Path

import pytest

SCANNER_PATH = Path(__file__).resolve().parent.parent / "scripts" / "security_scanner.py"

_spec = importlib.util.spec_from_file_location("security_scanner", SCANNER_PATH)
assert _spec and _spec.loader
scanner = importlib.util.module_from_spec(_spec)
sys.modules["security_scanner"] = scanner  # required before dataclass defs
_spec.loader.exec_module(scanner)

# Synthetic fingerprint used by fingerprint tests. It is NOT a real key; its
# only purpose is to match the `sb_secret_` provider pattern so we can
# exercise the "known leaked" code path. Tests register its hash into the
# scanner via monkeypatch.
FAKE_FINGERPRINT = "sb_secret_TEST_FIXTURE_NOT_A_REAL_KEY_0000000000000000"
FAKE_FINGERPRINT_HASH = hashlib.sha256(FAKE_FINGERPRINT.encode()).hexdigest()
FAKE_FINGERPRINT_LABEL = "TEST fixture key"


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """Minimal fake repo layout the scanner expects."""
    (tmp_path / "src" / "coarse").mkdir(parents=True)
    (tmp_path / "src" / "coarse" / "models.py").write_text(
        'DEFAULT_MODEL = "openai/gpt-5"\n'
    )
    (tmp_path / "scripts").mkdir()
    (tmp_path / "tests").mkdir()
    return tmp_path


@pytest.fixture
def register_fake_fingerprint(monkeypatch: pytest.MonkeyPatch):
    """Add FAKE_FINGERPRINT_HASH to the scanner's fingerprint table."""
    monkeypatch.setitem(
        scanner.LEAKED_FINGERPRINT_HASHES,
        FAKE_FINGERPRINT_HASH,
        FAKE_FINGERPRINT_LABEL,
    )


def run(repo: Path, *extra: str) -> tuple[int, list[scanner.Finding]]:
    """Invoke the scanner against repo and return (exit_code, findings)."""
    old_root = scanner.REPO_ROOT
    scanner.REPO_ROOT = repo
    try:
        findings: list[scanner.Finding] = []
        findings.extend(scanner.scan_secrets(repo))
        findings.extend(scanner.scan_env_example(repo))
        findings.extend(scanner.scan_env_permissions(repo))
        findings.extend(scanner.scan_model_id_literals(repo))
    finally:
        scanner.REPO_ROOT = old_root
    strict = "--strict" in extra
    blocking_sevs = {"CRITICAL", "HIGH"} if strict else {"CRITICAL"}
    code = 2 if any(f.severity in blocking_sevs for f in findings) else 0
    return code, findings


def test_clean_repo(repo: Path) -> None:
    code, findings = run(repo)
    assert code == 0
    assert findings == []


def test_leaked_fingerprint_is_critical(
    repo: Path, register_fake_fingerprint: None
) -> None:
    (repo / "scripts" / "deploy.sh").write_text(
        f'curl -H "apikey: {FAKE_FINGERPRINT}"\n'
    )
    code, findings = run(repo)
    assert code == 2
    kinds = {f.kind for f in findings}
    assert "leaked-fingerprint" in kinds
    assert any(f.severity == "CRITICAL" for f in findings)


def test_fingerprint_allowed_in_env_file(
    repo: Path, register_fake_fingerprint: None
) -> None:
    (repo / ".env").write_text(
        f"SUPABASE_SERVICE_ROLE_KEY={FAKE_FINGERPRINT}\n"
    )
    os.chmod(repo / ".env", 0o600)
    code, findings = run(repo)
    assert not any(f.kind == "leaked-fingerprint" for f in findings)
    assert code == 0


def test_provider_pattern_is_high(repo: Path) -> None:
    (repo / "scripts" / "deploy.sh").write_text(
        'OPENAI="sk-proj-abcdefghijklmnopqrstuvwxyz0123456789ABCDEF"\n'
    )
    code, findings = run(repo)
    assert any(
        f.kind == "secret-pattern" and f.severity == "HIGH" for f in findings
    )
    assert code == 0
    strict_code, _ = run(repo, "--strict")
    assert strict_code == 2


def test_placeholder_marker_skipped(repo: Path) -> None:
    (repo / ".env.example").write_text(
        'OPENAI_API_KEY="sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"\n'
    )
    code, findings = run(repo)
    assert not any(f.kind == "secret-pattern" for f in findings)
    assert not any(f.kind == "env-example-real-secret" for f in findings)
    assert code == 0


def test_inline_ignore_marker(repo: Path) -> None:
    (repo / "scripts" / "deploy.sh").write_text(
        'KEY="sk-proj-realrealrealrealrealrealrealreal12"  # security: ignore\n'
    )
    code, findings = run(repo)
    assert not any(f.kind == "secret-pattern" for f in findings)
    assert code == 0


def test_env_permissions_too_open(repo: Path) -> None:
    env = repo / ".env"
    env.write_text("FOO=bar\n")
    os.chmod(env, 0o644)
    code, findings = run(repo)
    assert any(f.kind == "env-perm" and f.severity == "HIGH" for f in findings)
    assert code == 0


def test_env_permissions_tight(repo: Path) -> None:
    env = repo / ".env"
    env.write_text("FOO=bar\n")
    os.chmod(env, 0o600)
    _, findings = run(repo)
    assert not any(f.kind == "env-perm" for f in findings)


def test_docstring_model_id_skipped(repo: Path) -> None:
    (repo / "src" / "coarse" / "llm.py").write_text(
        '"""Example model IDs like \'openai/gpt-4o\' go here."""\n'
        'x = 1\n'
    )
    _, findings = run(repo)
    assert not any(f.kind == "hardcoded-model-id" for f in findings)


def test_real_model_id_literal_flagged(repo: Path) -> None:
    (repo / "src" / "coarse" / "llm.py").write_text(
        'COSTS = {\n'
        '    "openai/gpt-5.1": {"input": 1.0, "output": 5.0},\n'
        '}\n'
    )
    _, findings = run(repo)
    assert any(
        f.kind == "hardcoded-model-id" and f.severity == "MEDIUM"
        for f in findings
    )


def test_models_py_itself_not_flagged(repo: Path) -> None:
    _, findings = run(repo)
    assert not any(f.kind == "hardcoded-model-id" for f in findings)


def test_provider_auto_suffix_not_flagged(repo: Path) -> None:
    (repo / "src" / "coarse" / "llm.py").write_text(
        'api_key = resolve_api_key("openrouter/auto")\n'
    )
    _, findings = run(repo)
    assert not any(f.kind == "hardcoded-model-id" for f in findings)


def test_scanner_self_exempt(
    repo: Path, register_fake_fingerprint: None
) -> None:
    # Drop the fake fingerprint into the scanner path and verify it is
    # ignored there (SELF_EXEMPT).
    target = repo / "scripts" / "security_scanner.py"
    target.write_text(f'LEAKED = "{FAKE_FINGERPRINT}"\n')
    code, findings = run(repo)
    assert not any(f.kind == "leaked-fingerprint" for f in findings)
    assert code == 0


def test_json_output_roundtrip(
    repo: Path,
    capsys: pytest.CaptureFixture,
    register_fake_fingerprint: None,
) -> None:
    (repo / "scripts" / "deploy.sh").write_text(
        f'curl -H "apikey: {FAKE_FINGERPRINT}"\n'
    )
    rc = scanner.main(["--root", str(repo), "--json"])
    out = capsys.readouterr().out
    import json

    payload = json.loads(out)
    assert rc == 2
    assert payload["counts"]["CRITICAL"] >= 1
    assert payload["findings"]
