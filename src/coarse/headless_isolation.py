"""Isolation policy for subscription-backed headless review CLIs.

The review pipeline needs text generation, not a coding agent.  This module
keeps the subprocess environment, capability gates, and host-specific policy
data separate from the response parsing and retry transport.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Host markers belong to the outer coding-agent session and must never flow
# into a sibling review process.
_HOST_ENV_VARS = (
    "CLAUDECODE",
    "CLAUDE_CODE_ENTRYPOINT",
    "CLAUDE_CODE_EXECPATH",
    "CLAUDE_CODE_SSE_PORT",
    "CLAUDE_CODE_SESSION_ID",
    "CODEX_SESSION_ID",
    "CODEX_INTERNAL",
    "GEMINI_SESSION_ID",
    "GEMINI_CLI_INTERNAL",
)

# These keys redirect a subscription CLI to metered API billing.
SUBSCRIPTION_BILLING_KEYS = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "OPENAI_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
)

_SECRET_ENV_MARKERS = (
    "API_KEY",
    "TOKEN",
    "SECRET",
    "PASSWORD",
    "CREDENTIAL",
    "PRIVATE_KEY",
    "ACCESS_KEY",
    "DATABASE_URL",
    "CONNECTION_STRING",
)


def clean_subprocess_env() -> dict[str, str]:
    """Return a UTF-8 child environment without ambient sessions or secrets."""
    env = dict(os.environ)
    for var in (*_HOST_ENV_VARS, *SUBSCRIPTION_BILLING_KEYS):
        env.pop(var, None)
    for var in tuple(env):
        upper = var.upper()
        if any(marker in upper for marker in _SECRET_ENV_MARKERS):
            env.pop(var, None)
    if os.name != "nt":
        default_utf8 = "en_US.UTF-8" if sys.platform == "darwin" else "C.UTF-8"
        env["LANG"] = env.get("LANG") or default_utf8
        env["LC_ALL"] = env.get("LC_ALL") or default_utf8
    return env


_VERSION_RE = re.compile(r"\b(\d+)\.(\d+)\.(\d+)\b")


def parse_cli_version(text: str) -> tuple[int, int, int] | None:
    """Extract a three-part CLI version from ordinary ``--version`` output."""
    match = _VERSION_RE.search(text)
    if match is None:
        return None
    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch)


def probe_cli_version(bin_name: str) -> str:
    """Return combined ``--version`` output, or an empty string on failure."""
    try:
        result = subprocess.run(
            [bin_name, "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            check=False,
            env=clean_subprocess_env(),
        )
        return (result.stdout or "") + (result.stderr or "")
    except (subprocess.SubprocessError, OSError):
        return ""


CLAUDE_REQUIRED_ISOLATION_FLAGS = frozenset(
    {
        "--safe-mode",
        "--disable-slash-commands",
        "--strict-mcp-config",
        "--mcp-config",
        "--tools",
        "--permission-mode",
        "--no-session-persistence",
    }
)

CODEX_MIN_ISOLATION_VERSION = (0, 149, 0)
CODEX_REQUIRED_ISOLATION_FLAGS = frozenset(
    {
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--strict-config",
    }
)

# Permission profiles do not compose with legacy ``--sandbox``.  This profile
# denies the filesystem by default, permits only the ephemeral workspace plus
# the minimum executable/runtime paths, and carves the global temp roots back
# out so a malicious prompt cannot read a sibling temporary directory.
CODEX_REVIEW_PERMISSION_PROFILE = (
    "permissions.coarse-review={"
    "description='Text-only Coarse review',"
    "filesystem={"
    "':root'='deny',"
    "':minimal'='read',"
    "':tmpdir'='deny',"
    "':slash_tmp'='deny',"
    "':workspace_roots'={'.'='read'}"
    "},"
    "network={enabled=false}"
    "}"
)

CODEX_REVIEW_CONFIG_OVERRIDES = (
    "default_permissions='coarse-review'",
    CODEX_REVIEW_PERMISSION_PROFILE,
    "approval_policy='never'",
    "mcp_servers={}",
    "features.shell_tool=false",
    "features.unified_exec=false",
    "features.skill_mcp_dependency_install=false",
    "agents.enabled=false",
    "web_search='disabled'",
    "project_doc_max_bytes=0",
    "memories.generate_memories=false",
    "memories.use_memories=false",
)

GEMINI_MIN_ISOLATION_VERSION = (0, 37, 2)

# ``tools.core`` is an allowlist; an explicitly present empty list exposes no
# built-in file, shell, search, planning, or memory tools.  The isolated home
# contains no extensions, hooks, skills, policies, project memory, or MCP
# definitions, and the administrative toggles provide defense in depth.
GEMINI_REVIEW_SETTINGS = {
    "admin": {
        "extensions": {"enabled": False},
        "mcp": {"enabled": False},
        "skills": {"enabled": False},
    },
    "experimental": {"enableAgents": False},
    "general": {
        "defaultApprovalMode": "plan",
        "plan": {"enabled": True, "modelRouting": False},
    },
    "mcpServers": {},
    "security": {
        "auth": {"selectedType": "oauth-personal"},
        "folderTrust": {"enabled": False},
    },
    "tools": {"core": []},
}


def prepare_gemini_workspace_env(workspace: str) -> dict[str, str]:
    """Build an idempotent Gemini home containing only subscription OAuth."""
    env = clean_subprocess_env()
    isolated_home = Path(workspace) / "gemini-home"
    isolated_config = isolated_home / ".gemini"
    isolated_config.mkdir(parents=True, exist_ok=True)

    source = Path.home() / ".gemini"
    for name in ("oauth_creds.json", "google_accounts.json"):
        source_file = source / name
        if source_file.is_file():
            destination = isolated_config / name
            shutil.copyfile(source_file, destination)
            destination.chmod(0o600)

    settings_file = isolated_config / "settings.json"
    settings_file.write_text(json.dumps(GEMINI_REVIEW_SETTINGS, sort_keys=True), encoding="utf-8")
    settings_file.chmod(0o600)
    env["GEMINI_CLI_HOME"] = str(isolated_home)
    return env
