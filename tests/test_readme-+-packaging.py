"""Tests for README.md, CHANGELOG.md, and package build artifacts."""
from __future__ import annotations

import subprocess
import sys
import venv
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
README = REPO_ROOT / "README.md"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
PYPROJECT = REPO_ROOT / "pyproject.toml"


# ---------------------------------------------------------------------------
# test_readme_exists_and_nonempty
# ---------------------------------------------------------------------------


def test_readme_exists_and_nonempty():
    """README.md exists at repo root and has content (>500 chars)."""
    assert README.exists(), "README.md does not exist"
    content = README.read_text(encoding="utf-8")
    assert len(content) > 500, f"README.md is too short ({len(content)} chars)"


# ---------------------------------------------------------------------------
# test_readme_install_commands_present
# ---------------------------------------------------------------------------


def test_readme_install_commands_present():
    """README.md contains install commands under the `coarse-ink` PyPI name."""
    content = README.read_text(encoding="utf-8")
    assert "pip install coarse-ink" in content
    assert "uvx coarse-ink" in content


# ---------------------------------------------------------------------------
# test_readme_cli_commands_documented
# ---------------------------------------------------------------------------


def test_readme_cli_commands_documented():
    """README.md mentions both `coarse setup` and `coarse review` commands."""
    content = README.read_text(encoding="utf-8")
    assert "coarse setup" in content
    assert "coarse review" in content


# ---------------------------------------------------------------------------
# test_readme_api_keys_documented
# ---------------------------------------------------------------------------


def test_readme_api_keys_documented():
    """README.md mentions OPENAI_API_KEY and ANTHROPIC_API_KEY."""
    content = README.read_text(encoding="utf-8")
    assert "OPENAI_API_KEY" in content
    assert "ANTHROPIC_API_KEY" in content


# ---------------------------------------------------------------------------
# test_readme_python_api_documented
# ---------------------------------------------------------------------------


def test_readme_python_api_documented():
    """README.md shows `from coarse import review_paper` usage example."""
    content = README.read_text(encoding="utf-8")
    assert "from coarse import review_paper" in content


# ---------------------------------------------------------------------------
# test_readme_version_matches_pyproject
# ---------------------------------------------------------------------------


def test_readme_version_matches_pyproject():
    """Version in README.md matches version in pyproject.toml."""
    import tomllib

    readme_content = README.read_text(encoding="utf-8")
    with open(PYPROJECT, "rb") as f:
        pyproject = tomllib.load(f)
    version = pyproject["project"]["version"]
    assert version in readme_content, (
        f"pyproject.toml version '{version}' not found in README.md"
    )


# ---------------------------------------------------------------------------
# test_changelog_exists
# ---------------------------------------------------------------------------


def test_changelog_exists():
    """CHANGELOG.md exists and documents v0.1.0."""
    assert CHANGELOG.exists(), "CHANGELOG.md does not exist"
    content = CHANGELOG.read_text(encoding="utf-8")
    assert "0.1.0" in content, "CHANGELOG.md does not mention v0.1.0"


# ---------------------------------------------------------------------------
# test_package_builds
# ---------------------------------------------------------------------------


def test_package_builds(tmp_path):
    """Run `uv build` in project root; verify dist/ contains .whl and .tar.gz."""
    result = subprocess.run(
        ["uv", "build", "--out-dir", str(tmp_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"uv build failed:\n{result.stderr}"

    artifacts = list(tmp_path.iterdir())
    whl_files = [f for f in artifacts if f.suffix == ".whl"]
    sdist_files = [f for f in artifacts if f.name.endswith(".tar.gz")]

    assert len(whl_files) >= 1, f"No .whl found in {tmp_path}"
    assert len(sdist_files) >= 1, f"No .tar.gz found in {tmp_path}"


# ---------------------------------------------------------------------------
# test_package_installs_in_fresh_venv
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_package_installs_in_fresh_venv(tmp_path):
    """Install the built wheel into a fresh venv; verify `coarse --help` exits 0."""
    # Build wheel
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    result = subprocess.run(
        ["uv", "build", "--out-dir", str(dist_dir)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"uv build failed:\n{result.stderr}"

    whl_files = list(dist_dir.glob("*.whl"))
    assert whl_files, "No wheel found after build"
    wheel = whl_files[0]

    # Create fresh venv
    venv_dir = tmp_path / "venv"
    venv.create(str(venv_dir), with_pip=True, clear=True)

    if sys.platform == "win32":
        python = venv_dir / "Scripts" / "python.exe"
        coarse_bin = venv_dir / "Scripts" / "coarse.exe"
    else:
        python = venv_dir / "bin" / "python"
        coarse_bin = venv_dir / "bin" / "coarse"

    # Install wheel
    install_result = subprocess.run(
        [str(python), "-m", "pip", "install", str(wheel), "--quiet"],
        capture_output=True,
        text=True,
    )
    assert install_result.returncode == 0, (
        f"pip install failed:\n{install_result.stderr}"
    )

    # Run coarse --help
    help_result = subprocess.run(
        [str(coarse_bin), "--help"],
        capture_output=True,
        text=True,
    )
    assert help_result.returncode == 0, (
        f"`coarse --help` exited {help_result.returncode}:\n{help_result.stderr}"
    )
    output = help_result.stdout.lower()
    assert "review" in output or "coarse" in output, (
        f"Unexpected --help output:\n{help_result.stdout}"
    )


# ---------------------------------------------------------------------------
# test_uvx_entry_point
# ---------------------------------------------------------------------------


def test_uvx_entry_point():
    """pyproject.toml [project.scripts] registers both `coarse` and `coarse-ink`.

    Both point at `coarse.cli:app`. The `coarse-ink` entry is what makes
    `uvx coarse-ink ...` resolve directly (matching the PyPI distribution
    name); the `coarse` entry preserves the short command on PATH for
    users who `uv tool install coarse-ink`.
    """
    import tomllib

    with open(PYPROJECT, "rb") as f:
        pyproject = tomllib.load(f)

    scripts = pyproject.get("project", {}).get("scripts", {})
    assert "coarse" in scripts, "No 'coarse' entry in [project.scripts]"
    assert scripts["coarse"] == "coarse.cli:app", (
        f"Expected 'coarse.cli:app', got '{scripts['coarse']}'"
    )
    assert "coarse-ink" in scripts, "No 'coarse-ink' entry in [project.scripts]"
    assert scripts["coarse-ink"] == "coarse.cli:app", (
        f"Expected 'coarse.cli:app', got '{scripts['coarse-ink']}'"
    )
