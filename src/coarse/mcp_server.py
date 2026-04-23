"""MCP server exposing coarse.chat.ChatSession as tools.

Launched as a subprocess by an MCP client (e.g. Claude Code) per .mcp.json.
Holds a module-level registry of active ChatSession objects keyed by UUID.
Sessions are in-memory only and do not persist across server restarts.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from coarse.chat import ChatSession

mcp = FastMCP("coarse-chat")

_sessions: dict[str, ChatSession] = {}


@mcp.tool()
def ping() -> str:
    """Health check. Returns the literal string 'pong'."""
    return "pong"


@mcp.tool()
def start_chat(paper_path: str, review_path: str, model: str | None = None) -> str:
    """Start a chat session with the coarse reviewer over a paper and a prior review.

    Args:
        paper_path: Absolute path to the paper file (PDF, MD, TXT, TeX, DOCX, HTML, EPUB).
        review_path: Absolute path to the markdown review previously produced by `coarse review`.
        model: Optional LiteLLM model string. Defaults to the user's coarse config default.

    Returns:
        A session id string. Use it with `ask` and `end_session`.
    """
    paper = Path(paper_path)
    review = Path(review_path)
    if not paper.exists():
        raise FileNotFoundError(f"paper not found: {paper}")
    if not review.exists():
        raise FileNotFoundError(f"review not found: {review}")

    session = ChatSession(paper_path=paper, review_path=review, model=model)
    session_id = uuid.uuid4().hex
    _sessions[session_id] = session
    return session_id


@mcp.tool()
def ask(session_id: str, question: str) -> str:
    """Send a question to a running chat session and return the reviewer's reply.

    The session may transparently consult Perplexity Sonar Pro for literature
    lookups (up to 3 hops per turn) before composing the final reply.

    Args:
        session_id: Id returned by `start_chat`.
        question: The user's question for this turn.

    Returns:
        The reviewer's reply as plain markdown text.
    """
    session = _sessions.get(session_id)
    if session is None:
        raise KeyError(f"unknown session: {session_id}")
    return session.ask(question)


def main() -> None:
    """Entry point for the `coarse-mcp` console script."""
    mcp.run()
