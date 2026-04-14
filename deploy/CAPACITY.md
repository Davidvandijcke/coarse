# Capacity Expansion Runbook

coarse runs on four free-tier services. This document explains what to do when any of them hits its limit.

---

## Emergency: Pause Submissions Immediately

Preferred operator path from the repo root:

```bash
make pause
make pause-status
make resume
```

`make pause` uses `scripts/kill_switch.py`, which PATCHes the singleton
`system_status` row over PostgREST using either:

- `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` from your shell, or
- `web/.env.local` (`NEXT_PUBLIC_SUPABASE_URL` + `SUPABASE_SERVICE_KEY`) if the shell vars are unset.

Override the pause banner when needed:

```bash
make pause MSG="Monthly capacity reached. Please use the CLI: pip install coarse-ink"
```

SQL fallback in the **Supabase SQL Editor** (no deploy needed):

```sql
UPDATE system_status
SET accepting_reviews = false,
    banner_message = 'We are at capacity right now. Please use the command-line version: pip install coarse-ink',
    updated_at = now()
WHERE id = 1;
```

To re-enable:

```sql
UPDATE system_status
SET accepting_reviews = true,
    banner_message = null,
    updated_at = now()
WHERE id = 1;
```

---

## Service-by-Service

### Modal ($30/month free compute credits)

**Symptom**: Reviews fail with timeout or "Failed to start review worker" errors.

**Check**: [Modal dashboard](https://modal.com) > Usage tab.

**Thresholds**: A typical review uses ~$0.08–0.10 of compute. 300 reviews/month ≈ free tier. The daily monitoring cron alerts at 300 and auto-pauses at 800.

**Expand**: Add a payment method in the Modal dashboard. Modal charges per compute-second beyond the free tier — no plan upgrade needed.

**Emergency**: Reduce `max_containers` from 20 to 10 (or lower) in `deploy/modal_worker.py` and redeploy (`modal deploy deploy/modal_worker.py`) to slow the burn rate. Also update `MAX_CONCURRENT_REVIEWS` in `web/src/app/api/status/route.ts` to match so the frontend busy banner is accurate. Or pause submissions via `make pause` (SQL fallback above).

---

### Supabase (500 MB database, 1 GB storage, 50K MAU)

**Symptom**: Insert failures, storage upload errors, or "Failed to create review record".

**Check**: [Supabase dashboard](https://supabase.com) > Settings > Usage.

**What consumes space**: `result_markdown` and `paper_markdown` columns are the biggest consumers (~50–200 KB per review). Storage is less of a concern since PDFs are deleted after processing.

**Expand**: Upgrade to Supabase Pro ($25/month) for 8 GB database, 100 GB storage, 100K MAU.

**Emergency — free space**:
```sql
-- Delete old completed reviews (keeps last 90 days)
DELETE FROM reviews WHERE status = 'done' AND completed_at < now() - interval '90 days';

-- Or just drop the paper text from old reviews (keeps the review itself)
UPDATE reviews SET paper_markdown = null WHERE completed_at < now() - interval '30 days';
```

**Database paused?** Supabase free tier pauses after 7 days of inactivity. Go to the dashboard and click "Restore". The keepalive cron (`.github/workflows/keepalive.yml`) prevents this under normal operation.

---

### Vercel (100 GB bandwidth/month)

**Symptom**: 503 errors, site slow or unreachable.

**Check**: [Vercel dashboard](https://vercel.com) > Usage.

**Thresholds**: Hard to predict — depends on page weight and traffic. At ~5 MB per page load, 100 GB ≈ 20K page loads/month.

**Expand**: Upgrade to Vercel Pro ($20/month) for 1 TB bandwidth and 60-second function timeout.

**Emergency**: Pause submissions via `make pause` (SQL fallback above). The CLI (`pip install coarse-ink`) works independently of the web app.

---

### Resend (Free: 3k/month ≈ 100/day; Pro: 50k/month for $20)

**Symptom**: Emails stop arriving. The `/api/submit` route and `deploy/modal_worker.py::_send_email` log the failure via the best-effort path in `web/src/lib/email.ts` / the Python wrapper — review submissions continue regardless.

**Check**: Resend dashboard > Emails. Each review sends up to 2 emails (submit confirmation + completion), so the practical ceiling is half the monthly quota: **1500/month on Free, 25k/month on Pro**. The daily burst ceiling is softer — Pro amortizes to ~1666/day but bursts of several thousand per day are fine as long as the monthly total holds.

**Expand**:
- **Stay on Free (3k/month)**: the CLI path (`pip install coarse-ink`) has no email dependency, so hitting the Free ceiling only affects the web UI.
- **Upgrade to Pro ($20/month)**: 50k emails/month, higher send burst rate, dedicated IP available. Upgrade in the Resend dashboard — no code change.
- **Alternatives**: AWS SES ($0.10 per 1000 emails) if Resend pricing stops scaling. Requires rewriting `web/src/lib/email.ts` and the Python wrapper against `boto3.client("ses")`.

**Emergency kill switch**: flip `EMAIL_DELIVERY_DISABLED` to `true` in `web/src/lib/emailCapacity.ts` and redeploy. The landing page disables the email field, `/api/submit` accepts empty-email submissions, and the top banner tells users to bookmark their review key. This is the fastest escape hatch when Resend is down, the API key is revoked, or domain verification is lost. No env-var edit needed, no DB write — just a one-line flip + `vercel --prod`.

**Key rotation**: The Resend API key lives in three places and all three must rotate together: `vercel env ...` for the web app, `modal secret create coarse-resend RESEND_API_KEY=...` for the worker, and `gh secret set RESEND_API_KEY` for the monitor workflow. See `deploy/DEPLOY.md`.

---

## Monitoring

The daily monitoring cron (`.github/workflows/monitor.yml`) runs at 8 AM UTC and emails you when:

| Threshold | Action |
|-----------|--------|
| Monthly reviews > 300 | Warning email — approaching Modal free tier |
| Monthly reviews > 800 | Auto-pauses submissions + alert email |
| Daily reviews > 5000 | Warning email — sustained Resend monthly quota pressure |

Note on the daily threshold: each review sends up to 2 emails (confirm +
complete), so 5000 reviews/day ≈ 10000 emails/day. Resend Pro amortizes
to ~1666 emails/day against its 50k/month cap, so 10k for one day is
fine but sustained load at this level would burn the monthly quota in
under a week. The frontend has a hard cutoff at
`EMAIL_CAPACITY_REVIEW_THRESHOLD` (2500 reviews/24h) in
`web/src/lib/emailCapacity.ts` that disables the email input in the
submit form — this cron warns the maintainer first so there's time to
react before that gate auto-fires.

The cron uses these GitHub repo secrets: `SUPABASE_URL`,
`SUPABASE_SERVICE_KEY`, `RESEND_API_KEY`, `ALERT_EMAIL`.

---

## Cost Summary at Scale

| Volume | Modal | Supabase | Vercel | Resend | Total |
|--------|-------|----------|--------|--------|-------|
| 0–300/mo | Free | Free | Free | Free (3k/mo) | **$0** |
| 300–1500/mo | ~$10–50 | Free | Free | Free (3k/mo) | **$10–50** |
| 1500–3000/mo | ~$50–100 | $25 (Pro) | Free | $20 (Pro, 50k/mo) | **$95–145** |
| 3000+/mo | $100+ | $25 | $20 (Pro) | $20 (Pro) | **$165+** |
