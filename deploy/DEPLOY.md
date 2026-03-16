# Deploying coarse

The web app runs on four free services:

| Service | Role | Free tier |
|---------|------|-----------|
| **Vercel** | Frontend + `/api/submit` | 100 GB bandwidth, 10s function timeout |
| **Supabase** | PostgreSQL + file storage | 500 MB DB, 1 GB storage, 50K MAU |
| **Modal** | Serverless Python worker | $30/month compute credits |
| **Gmail** | Email notifications | 500 emails/day (app password) |

Users provide their own OpenRouter API key, so **you only pay** for Mistral OCR + Gemini Flash extraction (~$0.02–0.07 per review). Everything else is free.

---

## Prerequisites

- GitHub repo (public, for free GitHub Actions)
- API keys: `OPENROUTER_API_KEY`, `MISTRAL_API_KEY`, `GEMINI_API_KEY`
- Accounts on: [Supabase](https://supabase.com), [Modal](https://modal.com), [Vercel](https://vercel.com)

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
   | `coarse-openrouter` | `OPENROUTER_API_KEY` (fallback if user doesn't provide one) |
   | `coarse-mistral` | `MISTRAL_API_KEY` |
   | `coarse-gemini` | `GEMINI_API_KEY` |
   | `coarse-supabase` | `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` |
   | `coarse-webhook` | `MODAL_WEBHOOK_SECRET` (generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"`) |
   | `coarse-gmail` | `GMAIL_USER`, `GMAIL_APP_PASSWORD`, `SITE_URL` (e.g. `https://coarse.vercel.app`) |

3. Deploy:
   ```bash
   modal deploy deploy/modal_worker.py
   ```

4. Copy the webhook URL from the output. It looks like:
   ```
   https://<your-org>--coarse-review-run-review.modal.run
   ```

5. Verify the health endpoint:
   ```bash
   curl https://<your-org>--coarse-review-health.modal.run
   # → {"status": "ok", "service": "coarse-review"}
   ```

**How the worker runs**: When triggered by the frontend, it downloads the PDF from Supabase Storage, calls `coarse.review_paper()` with the user's OpenRouter key, writes the review markdown back to Supabase, sends a completion email, and deletes the PDF. Timeout is 10 minutes, memory is 512 MB.

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
   | `MODAL_WEBHOOK_SECRET` | (same value as Modal secret) | Shared secret |
   | `GMAIL_USER` | `your@gmail.com` | Gmail address for sending |
   | `GMAIL_APP_PASSWORD` | `xxxx xxxx xxxx xxxx` | Gmail app password |
   | `NEXT_PUBLIC_SITE_URL` | `https://coarse.vercel.app` | Your public URL |

3. Deploy. The site will be live at `https://coarse.vercel.app` (or a custom domain if configured).

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

Email notifications use Gmail with an app password. To set up:

1. Use or create a Gmail account for sending
2. Enable 2-Factor Authentication on the account
3. Go to [Google App Passwords](https://myaccount.google.com/apppasswords) and generate a new app password
4. Set `GMAIL_USER` and `GMAIL_APP_PASSWORD` in both Vercel and Modal secrets

Gmail app passwords support ~500 emails/day, which covers ~250 reviews/day. If you need more volume, swap to a transactional email service (Resend, SES, etc.).

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
  ├── Send confirmation email (Gmail)
  └── Return { id: uuid } → redirect to /status/{uuid}
  │
  ▼
Modal worker (async, up to 10 min)
  ├── Download PDF from Supabase Storage
  ├── Run coarse.review_paper() with user's OpenRouter key
  ├── UPDATE reviews SET status='done', result_markdown=...
  ├── Delete PDF from Supabase Storage
  └── Send completion email (Gmail)
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

**"Failed to start review"**: Modal webhook URL is wrong or the worker isn't deployed. Run `modal deploy deploy/modal_worker.py` and verify with the health endpoint.

**Review stuck on "queued"**: Modal worker crashed or timed out. Check Modal logs at [modal.com/apps](https://modal.com/apps).

**No emails received**: Check that `GMAIL_USER` and `GMAIL_APP_PASSWORD` are set in both Vercel and Modal. Verify the app password is valid at [Google App Passwords](https://myaccount.google.com/apppasswords). Check spam folders.

**Database paused**: Go to [supabase.com](https://supabase.com) dashboard and click "Restore". Ensure the keep-alive cron is running (check GitHub Actions).
