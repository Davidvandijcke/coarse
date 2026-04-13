from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT = _REPO_ROOT / "scripts" / "run_remote_mcp_dev.py"


def _load_script():
    spec = importlib.util.spec_from_file_location("coarse_remote_mcp_dev", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def remote_dev():
    return _load_script()


def test_is_public_host_accepts_tunnel_domains(remote_dev):
    assert remote_dev.is_public_host("abc.trycloudflare.com") is True
    assert remote_dev.is_public_host("your-org--coarse-mcp-asgi.modal.run") is True


def test_is_public_host_rejects_local_only_hosts(remote_dev):
    assert remote_dev.is_public_host("localhost") is False
    assert remote_dev.is_public_host("127.0.0.1") is False
    assert remote_dev.is_public_host("10.0.0.8") is False
    assert remote_dev.is_public_host("workstation.local") is False


def test_normalize_site_url_strips_trailing_slash(remote_dev):
    assert (
        remote_dev.normalize_site_url("https://abc.trycloudflare.com/")
        == "https://abc.trycloudflare.com"
    )


def test_normalize_site_url_rejects_subpaths(remote_dev):
    with pytest.raises(remote_dev.ConfigError, match="site origin only"):
        remote_dev.normalize_site_url("https://abc.trycloudflare.com/review/123")


def test_normalize_site_url_rejects_localhost(remote_dev):
    with pytest.raises(remote_dev.ConfigError, match="public host"):
        remote_dev.normalize_site_url("http://localhost:3000")


def test_normalize_mcp_url_appends_mcp_path(remote_dev):
    assert (
        remote_dev.normalize_mcp_url("https://your-org--coarse-mcp-asgi.modal.run")
        == "https://your-org--coarse-mcp-asgi.modal.run/mcp/"
    )


def test_normalize_mcp_url_preserves_mcp_path(remote_dev):
    assert (
        remote_dev.normalize_mcp_url("https://your-org--coarse-mcp-asgi.modal.run/mcp")
        == "https://your-org--coarse-mcp-asgi.modal.run/mcp/"
    )


def test_normalize_mcp_url_rejects_other_paths(remote_dev):
    with pytest.raises(remote_dev.ConfigError, match="server root or the /mcp path"):
        remote_dev.normalize_mcp_url("https://example.com/not-mcp")


def test_build_web_env_sets_expected_overrides(remote_dev):
    env = remote_dev.build_web_env("https://abc.trycloudflare.com", "https://foo.modal.run/mcp/")
    assert env == {
        "NEXT_PUBLIC_SITE_URL": "https://abc.trycloudflare.com",
        "NEXT_PUBLIC_MCP_SERVER_URL": "https://foo.modal.run/mcp/",
    }


def test_wait_for_public_site_fails_fast_when_dev_server_exits(remote_dev):
    class _DeadProcess:
        returncode = 1

        @staticmethod
        def poll():
            return 1

    with pytest.raises(RuntimeError, match="exited before the public site came up"):
        remote_dev.wait_for_public_site(
            "https://abc.trycloudflare.com",
            timeout_seconds=0.1,
            interval_seconds=0.01,
            process=_DeadProcess(),
        )
