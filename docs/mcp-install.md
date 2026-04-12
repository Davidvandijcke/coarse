# Install the coarse MCP connector

`coarse` can run as an MCP (Model Context Protocol) server, which means
you can drive a paper review from inside Claude.ai, Claude Code, Gemini
CLI, or the ChatGPT Apps SDK — using your existing subscription for the
expensive review reasoning. You still bring a small OpenRouter key to
fund PDF extraction (~$0.05–0.15 per paper), but the 15–25 review stages
run on whichever model your host is configured with.

**Public endpoint:** `https://coarse.vercel.app/mcp/`

(If that URL isn't live yet, run the server locally — see the bottom of
this page. The install snippets below work the same way against a
localhost URL.)

## Claude.ai (Pro / Max / Team / Enterprise)

1. Settings → Connectors → **Add custom connector**.
2. **Name**: `coarse`
3. **URL**: `https://coarse.vercel.app/mcp/`
4. Save. Refresh the Claude.ai tab.
5. In any new conversation, ask: *"Review this paper with coarse:
   https://arxiv.org/pdf/2301.00001.pdf — here's my OpenRouter key:
   sk-or-v1-..."*

Claude will call `upload_paper_url`, walk through `get_paper_section`
and `get_review_prompt`, run each stage against the model you have
selected, and hand back a `finalize_review` URL you can share.

## Claude Code (Max subscription)

```bash
# Inside any project directory
claude mcp add --transport http coarse https://coarse.vercel.app/mcp/
```

Or add it to `~/.claude.json` manually:

```jsonc
{
  "mcpServers": {
    "coarse": {
      "transport": "http",
      "url": "https://coarse.vercel.app/mcp/"
    }
  }
}
```

Then from inside Claude Code:

> `/mcp` to confirm the `coarse` server is healthy, then ask Claude Code
> to "review ~/papers/draft.pdf" — it will read the PDF, call
> `upload_paper_bytes` with a base64 payload + your OpenRouter key, and
> iterate through the review stages using your Claude Max quota.

## Gemini CLI (personal Google account — AI Pro / AI Ultra quotas)

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "coarse": {
      "httpUrl": "https://coarse.vercel.app/mcp/"
    }
  }
}
```

Restart Gemini CLI. The tools appear under the `coarse` namespace.
Run `gemini` and ask for a paper review — Gemini CLI uses your
logged-in Google account's quota for the review reasoning.

## ChatGPT (Plus / Pro / Business — developer mode)

ChatGPT's MCP connector flow is only available when **Developer mode**
is enabled:

1. Settings → **Connectors** → toggle on "Developer mode".
2. **Add custom server** → URL: `https://coarse.vercel.app/mcp/`.
3. Approve the tools.
4. Start a new chat and ask for a paper review.

Public listing in the ChatGPT Apps directory requires a separate
submission (logo, privacy URL, screenshots). That's tracked in issue
`#N` and doesn't block the Developer-mode flow.

## Running against a local server

If you're developing or the public URL isn't live:

```bash
cd /path/to/coarse
uv sync --extra dev
uv run python deploy/mcp_server.py --transport http --port 8765
```

Then substitute `http://127.0.0.1:8765/mcp/` for
`https://coarse.vercel.app/mcp/` in any of the snippets above. The
local server uses an in-memory paper store, so state is lost when the
process exits — which is fine for a single review session.

## What the host LLM does (and what it doesn't)

The MCP server runs *only* these deterministic steps:

| Tool | What it does |
|---|---|
| `upload_paper_url` / `upload_paper_bytes` / `upload_paper_path` | Mistral OCR + structure parsing, paid by your OpenRouter key |
| `get_paper_section` | Returns one section's text from stored state |
| `get_review_prompt` | Returns the coarse prompt strings for a stage |
| `verify_quotes` | Fuzzy-matches quotes against the paper text |
| `finalize_review` | Renders the review markdown; in callback mode POSTs it back to coarse.vercel.app's `/api/mcp-finalize` |

Everything else — the overview pass, per-section commentary, crossref
dedup, critique polish — happens in the host LLM's conversation loop,
using whichever model you picked in Claude.ai / Claude Code / Gemini /
ChatGPT. That's why the review runs on your subscription and costs you
nothing extra beyond the ~10-cent extraction.

## Security — why the MCP server has zero Supabase credentials

The MCP server you install is publicly reachable and has no per-user
auth on its HTTP surface. Giving it a Supabase service key would let
anyone who reaches it (or your tunnel URL) read and write every paper
and review in the database. So it has no key. At all.

Instead, when you upload a paper on coarse.vercel.app and click
"Review with my subscription", the web frontend's `/api/mcp-handoff`
route mints two short-lived capabilities and drops them into your
clipboard handoff prompt:

- A **15-minute Supabase Storage signed download URL**, scoped to the
  one PDF you just uploaded. The chat host calls `upload_paper_url`
  with that URL; the MCP server dereferences it exactly once and
  discards it.
- A **60-minute single-use finalize token** that authorizes exactly
  one write of the finished review back to your reviews row. The MCP
  server's `finalize_review` tool POSTs the rendered markdown to
  `https://coarse.vercel.app/api/mcp-finalize` with the token; the
  Next.js backend validates and consumes the token server-side, then
  upserts the row using its own Supabase service key (which never
  leaves the Next.js process).

If your clipboard prompt leaks, an attacker can download your paper
for 15 minutes and overwrite your review once — both capabilities
auto-expire. They can't touch anyone else's data, can't read the
reviews table, can't persist anything beyond one row.

## Troubleshooting

- **"OPENROUTER_API_KEY required" when calling `upload_paper_url`**:
  pass your key as the `openrouter_key` tool argument, not via env.
  The server scopes it to that one call and restores the environment
  afterwards.
- **"paper_id not found"**: each client session is independent. If
  you've restarted the local server or the Modal container rolled
  over, re-run `upload_paper_url` — the paper_id changes.
- **Quotes get dropped at `verify_quotes`**: that means the host LLM
  hallucinated a quote. Re-run `get_review_prompt` for the affected
  section and nudge the host to quote verbatim from the section text.
