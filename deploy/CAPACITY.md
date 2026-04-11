# Capacity Expansion Runbook

coarse runs on four free-tier services. This document explains what to do when any of them hits its limit.

---

## Emergency: Pause Submissions Immediately

Run this in the **Supabase SQL Editor** (no deploy needed):

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

**Emergency**: Reduce `max_containers` from 20 to 10 (or lower) in `deploy/modal_worker.py` and redeploy (`modal deploy deploy/modal_worker.py`) to slow the burn rate. Also update `MAX_CONCURRENT_REVIEWS` in `web/src/app/api/status/route.ts` to match so the frontend busy banner is accurate. Or pause submissions via SQL above.

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

**Emergency**: Pause submissions via SQL above. The CLI (`pip install coarse-ink`) works independently of the web app.

---

### Gmail (500 emails/day)

**Symptom**: Emails stop arriving. No visible errors on the user side (email is fire-and-forget).

**Check**: Difficult to check programmatically. Each review sends 2 emails (confirmation + completion), so 250 reviews/day = 500 emails.

**Expand**: Replace Gmail with a transactional email service:
- **Resend**: Free for 100 emails/day, $20/month for 5K/day. Minimal code change (swap `nodemailer` transport).
- **AWS SES**: $0.10 per 1,000 emails. Requires domain verification.

Change the transport config in `web/src/app/api/submit/route.ts` (`getMailer()`) and `deploy/modal_worker.py` (`_send_email()`).

**Emergency**: The app works fine without email. Users can check their review status via the review key on the homepage. To disable email, remove or blank the `GMAIL_USER` / `GMAIL_APP_PASSWORD` env vars in Vercel and Modal.

---

## Monitoring

The daily monitoring cron (`.github/workflows/monitor.yml`) runs at 8 AM UTC and emails you when:

| Threshold | Action |
|-----------|--------|
| Monthly reviews > 300 | Warning email — approaching Modal free tier |
| Monthly reviews > 800 | Auto-pauses submissions + alert email |
| Daily reviews > 200 | Warning email — approaching Gmail daily limit (see note below) |

Note on the daily threshold: each review sends up to 2 emails (confirm +
complete), so 200 reviews/day ≈ 400 emails, leaving a ~100-email buffer
below Gmail's free-tier 500/day sender cap. The frontend also has a hard
cutoff at 240 reviews in `web/src/lib/emailCapacity.ts` that disables the
email input in the submit form — this cron warns the maintainer first so
there's time to react before the gate auto-fires.

The cron uses these GitHub repo secrets: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `GMAIL_USER`, `GMAIL_APP_PASSWORD`, `ALERT_EMAIL`.

---

## Cost Summary at Scale

| Volume | Modal | Supabase | Vercel | Gmail | Total |
|--------|-------|----------|--------|-------|-------|
| 0–300/mo | Free | Free | Free | Free | **$0** |
| 300–500/mo | ~$10–20 | Free | Free | Free | **$10–20** |
| 500–1000/mo | ~$20–70 | $25 (Pro) | Free | Free | **$45–95** |
| 1000+/mo | ~$70+ | $25 | $20 (Pro) | $20 (Resend) | **$135+** |
