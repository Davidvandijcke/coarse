# Deploying coarse

The web app runs on four free services:

| Service | Role | Free tier |
|---------|------|-----------|
| **Vercel** | Frontend + `/api/submit` | 100 GB bandwidth, 10s function timeout |
| **Supabase** | PostgreSQL + file storage | 500 MB DB, 1 GB storage, 50K MAU |
| **Modal** | Serverless Python worker | $30/month compute credits |
| **Resend** | Transactional email | 3k emails/month (≈1500 reviews) |

Users provide their own OpenRouter API key, which covers **everything**: review agents, literature search, and Mistral OCR for PDF extraction (all routed through OpenRouter's file-parser plugin). The operator pays only for Modal compute (~$0.08–0.10 per review) and Resend email.

---

## Prerequisites

- GitHub repo (public, for free GitHub Actions)
- Accounts on: [Supabase](https://supabase.com), [Modal](https://modal.com), [Vercel](https://vercel.com), [Resend](https://resend.com)
- A verified sending domain in Resend (e.g. `coarse.ink`) with SPF + DKIM published
- A shared secret for the Modal webhook (`python -c "import secrets; print(secrets.token_urlsafe(32))"`)

No LLM provider API keys are needed on the deployment side — users supply their own.

---

## 1. Supabase

1. Create a new project at [supabase.com](https://supabase.com)
2. Open the **SQL Editor** and paste the contents of `deploy/supabase_schema.sql`. Run it.
   - This creates the `reviews` table, enables RLS, creates the `papers` storage bucket, and enables Realtime.
3. Go to **Settings → API** and copy:
   - **Project URL** → `NEXT_PUBLIC_SUPABASE_URL`
   - **anon public key** → `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - **service_role secret key** → `SUPABASE_SERVICE_KEY`

The `reviews` table stores review metadata and results. PDFs are uploaded to the `papers` storage bucket and deleted immediately after processing.

**Access control**: The UUID primary key is unguessable (2^122 possible values) and serves as the access token. No login system needed. RLS allows anyone to read a review if they have the UUID; only the service key can write.

---

## 2. Modal

1. Install and authenticate:
   ```bash
   pip install modal
   modal setup
   ```

2. Create secrets in the [Modal dashboard](https://modal.com/secrets) — one secret group per service:

   | Secret name | Environment variables |
   |-------------|----------------------|
   | `coarse-supabase` | `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` |
   | `coarse-webhook` | `MODAL_WEBHOOK_SECRET` (generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"`) |
   | `coarse-resend` | `RESEND_API_KEY` (sending-access key scoped to `coarse.ink` — mint at [resend.com/api-keys](https://resend.com/api-keys)), `SITE_URL` (e.g. `https://coarse.ink`) |

   **No LLM provider secrets are mounted.** The user's OpenRouter key arrives with each review request and is set into the container's env for the duration of the run, then unset. See `modal_worker.py` for the pattern.

3. Deploy via CI, not manually. Production Modal deploys are handled by
   `.github/workflows/modal-deploy.yml` on every push to `main` that
   touches `src/coarse/**`, `deploy/modal_worker.py`,
   `deploy/mcp_server.py`, `pyproject.toml`, or the workflow file
   itself. Preview Modal deploys are handled by
   `.github/workflows/modal-preview-deploy.yml` on deploy-relevant
   pushes to `dev` (`src/coarse/**`, the two Modal entrypoints,
   `pyproject.toml`, or the preview workflow itself). You should almost
   never run `modal deploy` by hand.

   First-time production setup requires two GitHub Actions repo
   secrets: create a Modal token locally, then store `MODAL_TOKEN_ID`
   and `MODAL_TOKEN_SECRET` in **GitHub → Settings → Secrets and
   variables → Actions**.

   For preview CI, use a dedicated GitHub Environment named
   `preview-modal`, not plain repo secrets. Add
   `PREVIEW_MODAL_TOKEN_ID` and `PREVIEW_MODAL_TOKEN_SECRET` as
   **environment secrets** there, and protect that environment with
   whatever reviewers / branch rules you want for preview deploys.
   The safest setup is a dedicated Modal service user for preview CI;
   if Modal RBAC is enabled in the workspace, restrict that service
   user to the Modal `preview` environment only. If you do not have
   environment-restricted Modal credentials, treat preview CI as
   convenience automation, not a hard isolation boundary.

   After that, every merge to `main` that changes a deploy-relevant
   file will auto-redeploy production, and every deploy-relevant push
   to `dev` will auto-redeploy preview. Web-only or docs-only pushes to
   `dev` do not redeploy Modal preview unless you manually re-run the
   workflow. Manual re-runs:
   - `gh workflow run modal-deploy.yml --ref main`
   - `gh workflow run modal-preview-deploy.yml --ref dev`
   - or use the GitHub Actions tab

   **Emergency manual deploy** (only when `main` is broken and you
   need to ship a hotfix from a branch; use sparingly):
   ```bash
   COARSE_MODAL_DEPLOY_FORCE=1 modal deploy deploy/modal_worker.py
   ```
   Without the `COARSE_MODAL_DEPLOY_FORCE=1` env var, the import-time
   guard in `deploy/modal_worker.py::_enforce_deploy_branch()` and
   `deploy/mcp_server.py::_enforce_deploy_branch()` refuses to deploy
   from any branch other than `main`. This guard exists because on
   2026-04-13 a `modal deploy` from a `dev` checkout shipped
   resurrected cheap-tier stage routing plus an api-key race to
   production, breaking every review for hours.

4. Copy the webhook URL from the output (visible in the Actions run
   logs, or on the Modal dashboard). It looks like:
   ```
   https://<your-org>--coarse-review-run-review.modal.run
   ```

5. Verify the health endpoint:
   ```bash
   curl https://<your-org>--coarse-review-health.modal.run
   # → {"status": "ok", "service": "coarse-review"}
   ```

**How the worker runs**: When triggered by the frontend, it downloads the PDF from Supabase Storage, calls `coarse.review_paper()` with the user's OpenRouter key, writes the review markdown back to Supabase, sends a completion email, and deletes the PDF. Timeout is 10 minutes, memory is 512 MB.

If you also use the subscription/MCP flow, deploy `deploy/mcp_server.py`
and save the extract endpoint URL too:

```text
https://<your-org>--coarse-mcp-run-extract.modal.run
```

---

## 3. Vercel

1. Go to [vercel.com](https://vercel.com) and import the GitHub repo
   - Vercel auto-detects Next.js and configures the build
   - Set the **Root Directory** to `web/`

2. Add environment variables in **Settings → Environment Variables**:

   | Variable | Value | Notes |
   |----------|-------|-------|
   | `NEXT_PUBLIC_SUPABASE_URL` | `https://xxx.supabase.co` | From step 1 |
   | `NEXT_PUBLIC_SUPABASE_ANON_KEY` | `eyJ...` | From step 1 |
   | `SUPABASE_SERVICE_KEY` | `eyJ...` | From step 1 (server-side only) |
   | `MODAL_FUNCTION_URL` | `https://...modal.run` | From step 2 |
   | `MODAL_EXTRACT_URL` | `https://...modal.run` | `coarse-mcp` `run_extract` endpoint |
   | `MODAL_WEBHOOK_SECRET` | (same value as Modal secret) | Shared secret |
   | `RESEND_API_KEY` | `re_...` | Resend sending-access key (see step 5) |
   | `NEXT_PUBLIC_SITE_URL` | `https://coarse.ink` | Your public URL |
   | `NEXT_PUBLIC_MCP_SERVER_URL` | `https://.../mcp/` | Optional; used by legacy `/mcp` landing page |

3. Deploy. The site will be live at `https://coarse.ink` (or your Vercel preview URL during development).

For an isolated preview setup, see [deploy/PREVIEW_ENVIRONMENTS.md](PREVIEW_ENVIRONMENTS.md).

Default rollout for substantial changes:

1. Merge the change into `dev`
2. Open the Vercel preview deployment for the latest `dev` commit
3. On the preview website, run both user flows:
   - upload a small paper and click `Submit`
   - upload a small paper and click `Review with my subscription`
4. If the preview site shows `Service temporarily unavailable`, stop and
   fix preview infra before merging:
   - preview Vercel must have `NEXT_PUBLIC_SUPABASE_URL`,
     `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY`,
     `MODAL_FUNCTION_URL`, `MODAL_EXTRACT_URL`, and
     `MODAL_WEBHOOK_SECRET`
   - preview Supabase must have every SQL file listed in
     [deploy/PREVIEW_ENVIRONMENTS.md](PREVIEW_ENVIRONMENTS.md)
   - if Turnstile is enabled on preview, its hostname allowlist must
     include the preview URL
5. Confirm preview Supabase + preview Modal are the only backends
   touched
6. Merge `dev` into `main`
7. Let production CI deploy from `main`

Preview website signoff checklist:

1. Wait for Vercel preview creation for the latest `dev` commit
2. If the change touched `src/coarse/**`, `deploy/modal_worker.py`,
   `deploy/mcp_server.py`, `pyproject.toml`, or the preview workflow,
   also wait for `.github/workflows/modal-preview-deploy.yml` to finish
   or manually re-run it with `gh workflow run modal-preview-deploy.yml --ref dev`
3. Open the preview URL from the `dev` commit / PR checks
4. Log in through Vercel Authentication if prompted
5. Verify the upload succeeds, the status page loads, and the MCP
   handoff UI still works
6. Verify `coarse-review` and `coarse-mcp` invocations appear only in
   the Modal `preview` environment
7. Verify new rows land only in preview Supabase

---

## 4. Keep-Alive Cron

Supabase free tier pauses the database after 7 days of inactivity. A GitHub Actions workflow pings it every 5 days to prevent this.

The workflow is already at `.github/workflows/keepalive.yml`. You just need to add two **GitHub repo secrets** (Settings → Secrets and variables → Actions):

| Secret | Value |
|--------|-------|
| `SUPABASE_URL` | `https://xxx.supabase.co` |
| `SUPABASE_ANON_KEY` | `eyJ...` (the anon key, not the service key) |

---

## 5. Email (Optional)

Email notifications go through Resend. coarse sends both the "review received" confirmation and the "review ready" completion mail from `reviews@coarse.ink`. To set up:

1. Create a free Resend account at [resend.com](https://resend.com).
2. Add and verify the sending domain (e.g. `coarse.ink`) in **Domains → Add Domain**. Resend gives you SPF + DKIM records to publish with your DNS host.
3. Mint a **sending-access** API key at [resend.com/api-keys](https://resend.com/api-keys), scoped to that domain.
4. Set `RESEND_API_KEY` in all three places:
   - **Vercel**: Settings → Environment Variables → add to Production, Preview, and Development.
   - **Modal**: `modal secret create coarse-resend RESEND_API_KEY=...` (matches `@app.function(secrets=[...])` in `deploy/modal_worker.py`).
   - **GitHub Actions**: `gh secret set RESEND_API_KEY` (used by `.github/workflows/monitor.yml` for capacity alerts).

**Key rotation**: all three must rotate together — revoke the old key in the Resend dashboard only after the new one has replaced every environment. Fastest escape hatch if Resend ever breaks: flip `EMAIL_DELIVERY_DISABLED` to `true` in `web/src/lib/emailCapacity.ts` and redeploy — the web UI accepts empty-email submissions and the banner points users at their review key.

Resend Free is 3k emails/month (≈1500 reviews); Pro is 50k/month for $20. See `deploy/CAPACITY.md` for the math.

---

## Data Flow

```
User submits PDF + email + OpenRouter key
  │
  ▼
Vercel: POST /api/submit
  ├── INSERT into Supabase reviews table → gets UUID
  ├── Upload PDF to Supabase Storage as {uuid}.pdf
  ├── POST to Modal webhook with {uuid, pdf_path, api_key, email}
  ├── Send confirmation email (Resend)
  └── Return { id: uuid } → redirect to /status/{uuid}
  │
  ▼
Modal worker (async, up to 10 min)
  ├── Download PDF from Supabase Storage
  ├── Run coarse.review_paper() with user's OpenRouter key
  ├── UPDATE reviews SET status='done', result_markdown=...
  ├── Delete PDF from Supabase Storage
  └── Send completion email (Resend)
  │
  ▼
User views /review/{uuid}
  ├── Supabase Realtime subscription for live status
  └── Renders review markdown (react-markdown + KaTeX)
```

---

## Review Key

The review key is a UUID v4, generated by Supabase on row insert. It serves as:
- The database primary key
- The access token (no auth system — the UUID is unguessable)
- The URL path: `/review/{uuid}` and `/status/{uuid}`

Users receive the key:
1. Immediately after submission (shown on the status page)
2. In the confirmation email
3. In the completion email

They can paste it into the "Find a review" box on the homepage at any time.

---

## Security

- **User API keys**: passed to Modal via HTTPS, used for one review, cleared from the container environment afterward. Never stored in the database.
- **PDFs**: deleted from Supabase Storage immediately after processing. No retention.
- **Reviews**: stored in Supabase. Readable by anyone with the UUID. Writable only via service key.
- **Modal webhook**: authenticated with a shared secret (`MODAL_WEBHOOK_SECRET`).
- **Supabase service key**: only used server-side (Vercel API route + Modal worker). Never exposed to the browser.

---

## Cost Estimate

| Volume | Infrastructure | Operator LLM (OCR + QA) | Total |
|--------|---------------|--------------------------|-------|
| 0–50 reviews/mo | $0 | $1–3.50 | **$1–4** |
| 50–100 | $0 | $2–7 | **$2–7** |
| 100–500 | $0 | $4–35 | **$4–35** |
| 500+ | Modal may exceed free tier | $10–35 | Upgrade Modal |

---

## Local Development

```bash
cd web/
cp .env.local.example .env.local
# Fill in real values (or dummy values for frontend-only testing)
npm install
npm run dev
# → http://localhost:3000
```

The frontend works locally without Supabase/Modal — form submission will fail but you can develop the UI.

---

## Troubleshooting

**"Failed to create review record"**: Supabase project is paused or env vars are wrong. Check `NEXT_PUBLIC_SUPABASE_URL` and `SUPABASE_SERVICE_KEY`.

**"Failed to start review"**: Modal webhook URL is wrong or the worker isn't deployed. Check the most recent `deploy-modal` workflow run in GitHub Actions and verify with the health endpoint. Do not `modal deploy` manually unless `main` is broken — see step 3.

**Review stuck on "queued"**: Modal worker crashed or timed out. Check Modal logs at [modal.com/apps](https://modal.com/apps).

**No emails received**: Check that `RESEND_API_KEY` is set in both Vercel and Modal (and in GitHub secrets for the monitor workflow). Verify the key is live in the [Resend dashboard](https://resend.com/api-keys). Confirm the `coarse.ink` sending domain is still verified (Resend dashboard → Domains). Open the `/api/submit` and Modal worker logs and search for `Resend send ok` / `Resend send failed` lines. Finally, check spam folders — Resend domain warm-up takes a few days.

**Database paused**: Go to [supabase.com](https://supabase.com) dashboard and click "Restore". Ensure the keep-alive cron is running (check GitHub Actions).
