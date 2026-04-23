"""Tests for the coarse MCP server."""

from __future__ import annotations

from coarse.mcp_server import mcp, ping


def test_ping_returns_pong() -> None:
    assert ping() == "pong"


def test_server_name_is_coarse_chat() -> None:
    assert mcp.name == "coarse-chat"
