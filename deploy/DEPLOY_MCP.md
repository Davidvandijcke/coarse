# Deploying the coarse MCP server

The MCP server (`deploy/mcp_server.py`) is a FastMCP-based HTTP service
that lets Claude.ai custom connectors, Claude Code, Gemini CLI, and the
ChatGPT Apps SDK drive a paper review using the host's own LLM
subscription. The host model does the review reasoning; this server
only handles extraction, structured prompts, quote verification, and
final rendering.

See `docs/mcp-install.md` for the end-user install snippets that point
clients at a deployed server.

## Security model — zero ambient credentials

**The MCP server holds no Supabase service key, no Modal secrets, and
no persistent per-user auth.** Giving it any of those would grant a
publicly-reachable server (Modal URL + any installed MCP connector)
unchecked read/write access to every paper and review in the database,
which is unacceptable for a process that has no request-level auth on
its HTTP surface.

Instead, every state-changing operation on the web→MCP round-trip is
gated by a short-lived **capability** that the Next.js backend mints
per-paper, per-review, and hands to the host LLM via a clipboard
prompt on coarse.vercel.app:

- **Ingestion capability** — `/api/mcp-handoff` mints a 15-minute
  Supabase Storage signed download URL scoped to one PDF. The MCP
  server fetches the PDF via `upload_paper_url` with that URL and
  never touches Supabase.
- **Finalization capability** — the same `/api/mcp-handoff` call
  mints a 60-minute single-use `finalize_token` stored in the
  `mcp_handoff_tokens` table. When the host calls `finalize_review`
  with `finalize_token` + `callback_url`, the MCP server POSTs the
  rendered review to `https://coarse.vercel.app/api/mcp-finalize`,
  which validates + consumes the token and upserts the reviews row
  using the real service key that only the Next.js backend holds.

The worst-case of a compromised tunnel URL or MCP server is: download
one paper for 15 minutes, write exactly one review row for 60
minutes, then lose access. No cross-user data, no schema writes, no
credential exfiltration — the server never had them in the first
place.

## Architecture

```
 Client (Claude.ai / ChatGPT / Claude Code / Gemini CLI)
      │
      │  1. streamable-http MCP tool calls with capabilities pasted
      │     from coarse.vercel.app (signed URL + finalize_token)
      ▼
 ┌──────────────────────────────────┐
 │  Modal function `coarse-mcp`     │
 │  @modal.asgi_app() → FastMCP     │   NO SECRETS
 │                                  │
 │  Tools (7):                      │
 │   upload_paper_url(signed_url,   │
 │                    or_key)       │
 │   upload_paper_bytes(...)        │
 │   upload_paper_path(...)         │   local-only
 │   get_paper_section              │
 │   get_review_prompt              │
 │   verify_quotes                  │
 │   finalize_review(..., token,    │
 │                   callback_url)  │
 └───────────┬───────────────┬──────┘
             │               │
             │ 2. GET        │ 3. POST rendered review
             │   signed URL  │    with finalize_token
             ▼               ▼
 ┌──────────────────┐   ┌────────────────────────────────┐
 │ Supabase Storage │   │ coarse.vercel.app /api/mcp-    │
 │  papers/<uuid>   │   │   finalize  (Next.js)          │
 │  (15-min URL)    │   │                                │
 └──────────────────┘   │  Validates token, upserts      │
                        │  reviews row using SERVICE KEY │
                        │  that lives only here.         │
                        └────────────┬───────────────────┘
                                     │
                                     ▼
                              Supabase (reviews,
                               mcp_handoff_tokens)
```

The MCP Modal function is a *separate* Modal app on its own HTTP
endpoint. It is NOT the same process as `modal_worker.py`, does not
share the worker's `coarse-supabase` secret, and does not share any
Modal secret at all — `modal deploy deploy/mcp_server.py` publishes
it with an empty `secrets=[]`.

## Prerequisites

1. Modal CLI installed and authenticated: `uv run modal token new`.
2. No new Modal secrets required — the MCP function ships without any.
3. Two Supabase migrations applied (in the Supabase SQL editor):

   ```text
   deploy/migrate_mcp_handoff.sql
   ```

   This creates the `mcp_handoff_tokens` table plus the
   `cleanup_mcp_handoff_tokens()` helper. The web backend uses it to
   issue and consume finalize capabilities.

4. In Vercel env vars for the web frontend:
   - `NEXT_PUBLIC_SUPABASE_URL` and `SUPABASE_SERVICE_KEY` — already
     set for the OpenRouter flow; reused by `/api/mcp-handoff` and
     `/api/mcp-finalize`.
   - `NEXT_PUBLIC_SITE_URL` — the public origin the MCP server will
     POST to (`https://coarse.vercel.app` in prod, `http://localhost:3000`
     in local dev). If unset, the handoff route infers from the
     request's `host` header.

## Deploy

```bash
cd /path/to/coarse
uv run modal deploy deploy/mcp_server.py
```

Modal prints the HTTPS URL of the deployed ASGI app. That URL plus the
FastMCP HTTP mount (`/mcp/`) is what end users paste into their
chat-host connector config. For example:

```
https://your-org--coarse-mcp-asgi.modal.run/mcp/
```

Since the function has no secrets and no persistent state, `modal
deploy` is safe to re-run at will — there's nothing to migrate.

## Local smoke test

```bash
# 1. Install MCP extra + dev deps (one time)
uv sync --extra dev

# 2. Run the server locally. Finalize_review falls back to in-memory
# persistence when no finalize_token/callback_url is supplied.
uv run python deploy/mcp_server.py --transport http --port 8765

# 3. In another shell, point the MCP Inspector at it
npx @modelcontextprotocol/inspector
# → Transport: Streamable HTTP → URL: http://127.0.0.1:8765/mcp → Connect
```

For an end-to-end test that exercises every stage, use the reference
client:

```bash
export OPENROUTER_API_KEY=sk-or-v1-...
uv run python deploy/mcp_test_client.py \
    https://arxiv.org/pdf/2301.00001.pdf \
    --sections 3 \
    --output /tmp/test-review.md
```

This drives the full 7-tool pipeline against the local server using
one OpenRouter key for both extraction and the host-simulated review
reasoning. It uses the in-memory `finalize_review` path (no
callback), so nothing persists to Supabase. Good for regression
testing without touching production.

For the full web→MCP handoff flow (including /api/mcp-handoff +
/api/mcp-finalize), run:

```bash
cd web && npm run dev      # Next.js on localhost:3000 with your .env.local
uv run python deploy/mcp_server.py --transport http --port 8765
```

Then upload a paper at `http://localhost:3000`, click "Review with my
subscription → Claude Code" (or any other provider), paste the
clipboard prompt into your host, and watch the MCP server POST the
rendered review back to `http://localhost:3000/api/mcp-finalize`.

## Local web + remote MCP (recommended pre-prod test)

This is the first topology that exercises the real boundary conditions:

- the **web app stays local** so you can iterate quickly on the UI and
  handoff routes
- the **MCP server runs remotely** (Modal or equivalent), so callback
  URLs, host-origin derivation, and signed-URL reachability are tested
  the way production will use them

### 1. Deploy or identify the remote MCP URL

```bash
cd /path/to/coarse
uv run modal deploy deploy/mcp_server.py
```

Use the resulting public MCP URL, for example:

```text
https://your-org--coarse-mcp-asgi.modal.run/mcp/
```

### 2. Expose the local Next.js app through a public tunnel

Any public HTTPS tunnel works. Examples:

```bash
cloudflared tunnel --url http://127.0.0.1:3000
# or
ngrok http 3000
```

Copy the public HTTPS site origin, for example:

```text
https://example-subdomain.trycloudflare.com
```

This matters because `/api/mcp-handoff` and `/api/cli-handoff` derive the
callback / handoff origin from `NEXT_PUBLIC_SITE_URL` first. A remote MCP
worker cannot call back to `http://localhost:3000`.

### 3. Start local web dev with the remote-MCP helper

```bash
cd /path/to/coarse
uv run python scripts/run_remote_mcp_dev.py \
  --site-url https://example-subdomain.trycloudflare.com \
  --mcp-url https://your-org--coarse-mcp-asgi.modal.run/mcp/
```

The helper:

- validates that both URLs are public and HTTPS
- probes the remote MCP endpoint before booting the web app
- sets:
  - `NEXT_PUBLIC_SITE_URL=<public tunnel URL>`
  - `NEXT_PUBLIC_MCP_SERVER_URL=<remote MCP URL>`
- starts `npm run dev` in `web/`
- waits for the public tunnel URL to reach the local app

If you only want the preflight checks / env preview:

```bash
uv run python scripts/run_remote_mcp_dev.py \
  --site-url https://example-subdomain.trycloudflare.com \
  --mcp-url https://your-org--coarse-mcp-asgi.modal.run/mcp/ \
  --check-only
```

### 4. Run the end-to-end handoff

1. Open the local site at `http://localhost:3000`
2. Upload a paper
3. Click "Review with my subscription"
4. Paste the generated prompt into Codex / Claude Code / Gemini CLI
5. Confirm the remote MCP server POSTs the finished review back to the
   **public** tunnel URL's `/api/mcp-finalize`
6. Confirm the review appears in the local web UI

Failure modes worth testing here:

- stale / expired handoff token
- stale signed download URL
- bad `NEXT_PUBLIC_SITE_URL` (localhost or wrong tunnel)
- wrong `NEXT_PUBLIC_MCP_SERVER_URL`
- remote MCP cannot reach `/api/mcp-finalize`

## Post-deploy verification

1. Hit `https://<modal-url>/mcp` with the MCP Inspector and confirm
   all 7 tools show up.
2. Run the full web→MCP round-trip from a production browser: upload
   a paper, click "Review with Claude.ai", verify the clipboard
   prompt contains `signed_download_url` + `finalize_token` +
   `callback_url`, paste into Claude.ai, verify the rendered review
   lands in the reviews table at `reviews.id = paper_id`.
3. Check `select count(*) from mcp_handoff_tokens where
   consumed_at is not null` — should equal the number of successful
   round-trips.
4. Check `select * from reviews where model = 'mcp-host' order by
   completed_at desc limit 5` to confirm writes attributing to the
   MCP path.
