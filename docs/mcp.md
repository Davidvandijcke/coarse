# Coarse MCP Server

The `coarse-mcp` console script runs an [MCP](https://modelcontextprotocol.io) server that exposes `coarse chat` as a set of tools. Use it from any MCP client (Claude Code, Claude Desktop, Cursor, etc.) to hold a multi-turn conversation with the coarse reviewer over a paper and a prior review.

## Tools exposed

| Tool | Purpose |
| --- | --- |
| `start_chat(paper_path, review_path, model?)` | Open a session; returns a `session_id`. |
| `ask(session_id, question)` | Send one turn; returns the reviewer's reply. |
| `list_sessions()` | List active sessions with paper, review, model, turn count. |
| `end_session(session_id)` | Drop a session from memory. |

## Setup (Claude Code, project-scoped)

1. Install `coarse` from the local checkout (or PyPI when published):

   ```bash
   uv tool install --from /Users/you/coarse coarse-ink
   ```

2. Add a `.mcp.json` at your project root:

   ```json
   {
     "mcpServers": {
       "coarse-chat": {
         "command": "uv",
         "args": ["run", "--directory", "/Users/you/coarse", "coarse-mcp"]
       }
     }
   }
   ```

3. Confirm the launcher's environment carries `OPENROUTER_API_KEY` (or the equivalent for whichever provider your default model uses). MCP servers inherit env from the process that launches them, so if you start Claude Code from a shell that has the key exported, the server gets it. If your key lives only in `~/.zshrc`, launch Claude Code from an interactive zsh shell.

4. Restart Claude Code. Run `/mcp` to verify `coarse-chat` is connected.

## Usage example

```
You: Use coarse-chat to start a session over /tmp/paper.md and /tmp/review.md.
Claude: [calls start_chat] Session abc123... started.
You: Ask the reviewer which fix they recommend for §6.3.
Claude: [calls ask] The reviewer recommends option (b) because ...
```

## Limitations (v1)

- Sessions live only in memory. Restarting the MCP server (or Claude Code) drops them.
- Concurrent `ask` calls on the same session can interleave history; use one client at a time per session.
- No streaming. Long replies arrive as a single string when the model finishes.
- Each `ask` resends the full history, so token costs grow over a long conversation. `list_sessions` reports the turn count to help you judge when to start fresh.
