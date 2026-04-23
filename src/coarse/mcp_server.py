"""MCP server exposing coarse.chat.ChatSession as tools.

Launched as a subprocess by an MCP client (e.g. Claude Code) per .mcp.json.
Holds a module-level registry of active ChatSession objects keyed by UUID.
Sessions are in-memory only and do not persist across server restarts.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("coarse-chat")


@mcp.tool()
def ping() -> str:
    """Health check. Returns the literal string 'pong'."""
    return "pong"


def main() -> None:
    """Entry point for the `coarse-mcp` console script."""
    mcp.run()
