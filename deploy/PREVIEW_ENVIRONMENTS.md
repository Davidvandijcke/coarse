# Preview environment setup — Tier 0 + Tier 1

**Status:** planned, not yet implemented. Pick up in a fresh Claude Code session using this file as the brief.

**Goal:** test `dev`-branch changes against a **fully isolated** preview
stack (Vercel preview deployment + second Supabase project + second
Modal app) so schema migrations, worker changes, and web-side fixes
can be validated end-to-end **without touching production**. After this
lands, the uncomfortable moments from the 2026-04-13 session — testing
locally against production Supabase, running `migrate_mcp_handoff.sql`
against the real prod DB because there was no preview to test it on —
should no longer happen.

## Why this exists (context for the next session)

During the 2026-04-13 session where `dev` was brought up to date with
`main` (Resend migration, Cloudflare Turnstile, the web hardening
commits) we discovered that:

1. **`web/.env.local` pointed at production Supabase**
   (`dgibkmnyiusglhdgzffk.supabase.co`), because that's the only
   Supabase project coarse has. Every local `localhost:3003` test
   was exercising production DB rows.
2. **The dev branch had accumulated schema changes** (`review_handoff_secrets`,
   `mcp_handoff_tokens`, widened `reviews_status_check`, `reviews.taxonomy`
   column) that were never applied to production because dev had never
   been merged. `/api/presign` started failing with
   `PGRST205: Could not find the table 'public.review_handoff_secrets'`
   mid-test, forcing us to apply `deploy/migrate_mcp_handoff.sql` to
   production Supabase just to unblock local testing.
3. **There was no staging / preview path** that would have let us
   apply the migration to a throwaway DB first, verify the upload
   flow, and only then roll to prod.

Tier 0 + Tier 1 closes this gap. After this lands, the workflow for
any future schema change becomes: push to a branch → Vercel auto-deploys
a preview → the preview env vars point at the preview Supabase →
migrations run on preview first → verify → *then* apply to prod as
part of the release PR.

## The three tiers recap

- **Tier 0** (this doc, part 1): **Vercel Preview Protection**. Every
  non-main push already auto-deploys to a unique Vercel URL. Tier 0
  just adds a login wall so only the team can view it. Zero code
  changes, dashboard-only. **Still hits production Supabase + Modal**
  — Tier 0 alone does not isolate downstream services.

- **Tier 1** (this doc, part 2): **Isolated downstream services** +
  **Preview-scoped env vars**. Second Supabase project, second Modal
  app, Vercel env vars scoped to the Preview environment. After Tier 1,
  preview deployments can break the preview Supabase / Modal without
  any risk to production.

- **Tier 2 / Tier 3** (out of scope for this doc):
  - Tier 2: stable `dev.coarse.ink` custom domain for the preview
    deployment, Cloudflare Access email-allowlist gate.
  - Tier 3: Supabase Branching (Pro plan, ~$25/mo), `staging.coarse.ink`,
    feature flags, canary routing. None of these are needed at current
    scale.

## Prerequisites

You'll need (or need to create):

- [ ] Vercel account on a Pro or Team plan (Preview Protection is a
  Pro+ feature). If the project is currently on Hobby, Vercel charges
  per-seat — double-check pricing before upgrading.
- [ ] Supabase account with permission to create a new project. The
  **free tier** is sufficient for preview (500MB DB, 1GB storage, 2GB
  bandwidth/mo) — way above anything preview will consume.
- [ ] Modal account with permission to create a second app. Same
  billing account as the existing `coarse-review` Modal app is fine;
  Modal bills per-second per-container so an idle second app costs
  roughly nothing.
- [ ] A second Resend API key (optional — you can also just leave
  `RESEND_API_KEY` unset in Preview so emails silently no-op, which
  matches the dev-loop behavior).
- [ ] GitHub repo admin access to add a new `secrets` → `MODAL_TOKEN_ID_PREVIEW`
  and `MODAL_TOKEN_SECRET_PREVIEW` pair (if you want the preview Modal
  app deployed via CI; see step 12 below for the alternative of
  deploying from a local checkout).
- [ ] An extra ~2 hours of focused time. Most of the work is dashboard
  navigation and env-var management; there's very little code.

## Tier 0 — Vercel Preview Protection (30 min, dashboard only)

### Step 0.1 — Verify the current preview-deploy state

Push any small throwaway branch (e.g. `docs/verify-preview`) and
confirm that Vercel auto-creates a preview deployment at a URL like
`coarse-git-docs-verify-preview-<team>.vercel.app`. If Vercel
isn't doing this automatically, Git integration may not be wired up;
fix that in **Vercel dashboard → Project → Settings → Git** before
continuing.

### Step 0.2 — Enable Deployment Protection for Preview

**Vercel dashboard → coarse project → Settings → Deployment Protection**

- **Vercel Authentication**: switch to `Standard Protection` or
  `All Deployments`. This requires a Vercel login with the project's
  team access to view any preview deployment. Free on Pro.
  - *Alternative*: **Password Protection** (single shared password).
    Simpler if you're the only tester. Vercel's password protection
    is paid on Pro+; check current pricing.
- **Production Deployment**: leave unprotected. `coarse.ink`
  stays public, only the preview URLs get the login wall.

Verify: open an incognito window, hit the preview URL from step 0.1.
You should hit a Vercel login page. Log in with your Vercel team
account → you should see the preview deployment.

**At this point Tier 0 is done.** You have private preview URLs.
But they still talk to production Supabase + Modal. Don't stop here
for anything that would mutate DB or spawn workers — that's what
Tier 1 fixes.

## Tier 1 — Isolated preview infra (~2 hours)

### Step 1.1 — Create the preview Supabase project

**Supabase dashboard → New Project**

- Project name: `coarse-preview` (or `coarse-dev` — be consistent).
- Region: **same region as production** (`dgibkmnyiusglhdgzffk` is
  in `us-east-1` — match it to minimize latency-related surprises
  when comparing behavior).
- Database password: generate a strong one, save to a password manager.
- Plan: **Free tier**.

After the project is ready, collect three strings from
**Project Settings → API**:
- `NEXT_PUBLIC_SUPABASE_URL` — e.g. `https://<new-project-ref>.supabase.co`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` — the `anon public` key
- `SUPABASE_SERVICE_KEY` — the `service_role` key (server-side only,
  never expose to client)

### Step 1.2 — Apply schema + migrations to preview Supabase

**Supabase dashboard → SQL Editor**

Run, in this order:

1. `deploy/supabase_schema.sql` — the baseline schema. Creates the
   `reviews`, `review_emails`, `review_secrets`, `review_handoff_secrets`,
   `system_status`, `rate_limit_log`, `mcp_handoff_tokens` tables,
   plus RLS policies and the `papers` storage bucket.
2. `deploy/migrate_mcp_handoff.sql` — even though the baseline
   schema.sql already has `review_handoff_secrets` + `mcp_handoff_tokens`,
   this migration also widens `reviews_status_check` to allow
   `extracting` / `extracted` statuses and adds `reviews.taxonomy`.
   Idempotent (`alter table ... if not exists`) so safe on the fresh
   DB.
3. `deploy/migrate_review_access_security.sql` — adds
   `reviews.access_token_required boolean` + MCP review statuses
   to access migration. Also idempotent.
4. `deploy/migrate_active_review_capacity.sql` — adds the
   `count_active_submitted_reviews` RPC used by the capacity gate.
5. Any other `deploy/migrate_*.sql` files that exist by the time
   you run this — check the directory for files newer than this doc.

After each migration, run `select * from reviews limit 0;` in the
SQL editor to confirm the table exists with the expected columns.
A clean preview DB should have zero rows in every table at this
point.

### Step 1.3 — Create the `papers` storage bucket

`supabase_schema.sql` creates the bucket via
`insert into storage.buckets (id, name, public) values ('papers', 'papers', false);`.
Verify in **Storage → Buckets** that `papers` exists and is private.
If it doesn't, run the line manually.

### Step 1.4 — Create the preview Modal app

Open a terminal in the main `coarse` checkout.

```bash
# Confirm you're on main or a clean dev (no uncommitted stuff)
git checkout dev
git pull

# Create a second Modal app by deploying modal_worker.py under a
# different app name. The name is set by `app = modal.App("coarse-review")`
# at the top of deploy/modal_worker.py. You have two options:
#
# Option A — change the app name via env var (CLEANER)
#   Modify deploy/modal_worker.py to read the app name from an
#   env var, e.g.:
#       MODAL_APP_NAME = os.environ.get("COARSE_MODAL_APP_NAME", "coarse-review")
#       app = modal.App(MODAL_APP_NAME)
#   Then:
#       COARSE_MODAL_APP_NAME=coarse-review-preview \
#       COARSE_MODAL_DEPLOY_FORCE=1 \
#       modal deploy deploy/modal_worker.py
#
# Option B — create a sibling file `deploy/modal_worker_preview.py`
#   that imports from modal_worker.py but overrides the app name.
#   Uglier, but zero changes to the production path.

# Either way, after the deploy you'll get a new Modal function URL
# that looks like:
#   https://<team>--coarse-review-preview-run-review.modal.run
# Save that URL — you need it for step 1.6.
```

**Important:** the `_enforce_deploy_branch` guard in
`deploy/modal_worker.py` refuses to deploy from a non-`main` branch
unless `COARSE_MODAL_DEPLOY_FORCE=1` is set. For the preview app,
set that env var on every local deploy, since you WILL be deploying
dev-branch code.

Also: on `web/src/app/api/submit/route.ts:50-51`, `getModalWebhookConfig`
currently whitelists only hostnames matching `*--coarse-review-run-review.modal.run`.
After Tier 1 you'll need to **relax that whitelist to also accept
`*--coarse-review-preview-run-review.modal.run`** (or parameterize it
on the env). This is the one code change Tier 1 needs; it's
~3 lines.

### Step 1.5 — Create the preview Modal secrets

The production Modal app uses three secrets (from `@app.function(secrets=[...])`
in `modal_worker.py`): `coarse-supabase`, `coarse-webhook`, `coarse-resend`.
You need preview equivalents.

**Modal dashboard → Secrets → Create**

1. `coarse-supabase-preview`:
   - `SUPABASE_URL` → preview Supabase URL from step 1.1
   - `SUPABASE_SERVICE_KEY` → preview Supabase service key from step 1.1
2. `coarse-webhook-preview`:
   - `MODAL_WEBHOOK_SECRET` → generate a fresh random string
     (`openssl rand -base64 32`), save it
3. `coarse-resend-preview` (optional — skip if you want preview
   submissions to silently no-op emails, which is usually fine):
   - `RESEND_API_KEY` → create a separate Resend key scoped to a
     preview sending domain, or skip entirely

You'll also need to update `deploy/modal_worker.py` to read
`coarse-supabase-preview` / `coarse-webhook-preview` / `coarse-resend-preview`
when deployed under the preview app name. Cleanest pattern:

```python
_MODAL_APP_NAME = os.environ.get("COARSE_MODAL_APP_NAME", "coarse-review")
_SECRET_SUFFIX = "-preview" if _MODAL_APP_NAME.endswith("-preview") else ""

@app.function(
    ...
    secrets=[
        modal.Secret.from_name(f"coarse-supabase{_SECRET_SUFFIX}"),
        modal.Secret.from_name(f"coarse-webhook{_SECRET_SUFFIX}"),
        modal.Secret.from_name(f"coarse-resend{_SECRET_SUFFIX}"),
    ],
    ...
)
```

Re-deploy the preview app after this change.

### Step 1.6 — Scope Vercel env vars to Preview

**Vercel dashboard → coarse → Settings → Environment Variables**

For each env var below, click **Add** (or Edit the existing var) and
set **Environment** to `Preview` only, leaving `Production` with the
current value untouched. Use the preview values from steps 1.1–1.5:

| Variable                        | Preview value                                        |
|---------------------------------|------------------------------------------------------|
| `NEXT_PUBLIC_SUPABASE_URL`      | preview Supabase URL                                 |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | preview Supabase anon key                            |
| `SUPABASE_SERVICE_KEY`          | preview Supabase service key                         |
| `MODAL_FUNCTION_URL`            | preview Modal function URL from step 1.4             |
| `MODAL_WEBHOOK_SECRET`          | preview webhook secret from `coarse-webhook-preview` |
| `NEXT_PUBLIC_SITE_URL`          | `https://coarse-git-dev-<team>.vercel.app` (or the stable alias after Tier 2) |
| `RESEND_API_KEY`                | *(leave unset in Preview — emails will no-op)*       |
| `TURNSTILE_SECRET_KEY`          | *(leave unset in Preview — Turnstile fails open)*    |
| `NEXT_PUBLIC_TURNSTILE_SITE_KEY`| *(leave unset in Preview — widget skipped)*          |
| `REVIEW_ACCESS_SECRET`          | *(leave unset in Preview — falls back to `SUPABASE_SERVICE_KEY` via `getReviewAccessSecret`)* |

**Critical:** double-check that **Production** values are NOT edited.
A slipped keystroke here that replaces a Production value with a
preview one will break `coarse.ink`. If Vercel's UI is unclear,
use the CLI instead:

```bash
# Confirm current preview vars
vercel env ls preview

# Set one:
vercel env add NEXT_PUBLIC_SUPABASE_URL preview
# (paste value, done)
```

After all preview env vars are set, trigger a fresh preview deployment
(push an empty commit to dev or click **Redeploy** in Vercel) and
verify the build picks up the new values. In the Vercel deployment
logs, look for the `Environments: .env.local` line and confirm no
build errors from missing env vars.

### Step 1.7 — Relax the Modal host whitelist for preview

Edit `web/src/app/api/submit/route.ts` around line 22:

```typescript
// Current (production-only):
const MODAL_WEBHOOK_HOST_SUFFIX = "--coarse-review-run-review.modal.run";

// New (accepts both):
const MODAL_WEBHOOK_HOST_SUFFIXES = [
  "--coarse-review-run-review.modal.run",
  "--coarse-review-preview-run-review.modal.run",
];
```

Then update `getModalWebhookConfig` to check the hostname against
every entry in the list. Add a test in `tests/test_modal_worker.py`
(or a new `tests/test_submit_route.ts` if you want TS tests) pinning
that both suffixes are accepted.

**Commit this change to dev** so the preview deployment has it.

### Step 1.8 — End-to-end smoke test on preview

With everything wired up, open the preview deployment URL in a
browser. It should ask for Vercel login (from Tier 0). After login:

1. Upload a small test PDF.
2. Click **Submit** (or the "Review with Claude Code" handoff button).
3. Confirm the review row appears in the **preview Supabase** dashboard
   (`coarse-preview` project → Table Editor → `reviews`).
4. Confirm no row appears in the **production Supabase** dashboard
   (sanity check that env-var scoping worked).
5. If you submitted the OpenRouter flow, confirm the Modal worker
   fires — check the **preview Modal app** dashboard for invocation
   logs. The production app should show zero new invocations.

If any of the above lights up production infra, stop and
re-check the env-var scoping in step 1.6. This is the scenario
Tier 1 exists to prevent.

### Step 1.9 — Document + commit

Add a short section to `deploy/DEPLOY.md` pointing at this file and
explaining the preview flow. Update `CHANGELOG.md` under
`## Unreleased` → `### Added`:

> **Preview deployment environment** — `dev`-branch pushes now
> auto-deploy to a Vercel preview URL backed by an isolated Supabase
> project (`coarse-preview`) and Modal app (`coarse-review-preview`).
> Migrations can be validated on preview before rolling to production.
> See `deploy/PREVIEW_ENVIRONMENTS.md` for the setup contract.

Commit as `chore(deploy): set up Tier 0 + Tier 1 preview environment`.

## Success criteria

You're done with Tier 0 + Tier 1 when all of the following are true:

- [ ] A fresh push to any non-main branch auto-creates a Vercel preview
  URL.
- [ ] That URL requires a Vercel login to view (Tier 0).
- [ ] A submission on the preview URL creates rows in the preview
  Supabase project, not production.
- [ ] A submission on the preview URL fires the preview Modal app,
  not production.
- [ ] A submission on the preview URL does NOT send emails (Resend key
  unset) and does NOT enforce Turnstile (keys unset) — both fail open.
- [ ] `coarse.ink` production traffic is still routed to production
  Supabase + Modal, unchanged.
- [ ] `deploy/DEPLOY.md` points at this file.
- [ ] `CHANGELOG.md` has an `### Added` entry under `## Unreleased`.

## Rollback plan

If anything breaks production during Tier 1 setup:

1. **Vercel env var slip** — hit the most recent Production deployment
   and click **Redeploy** to rebuild with the correct vars. Or revert
   the env var edit and trigger a production redeploy.
2. **Modal deployment hit the wrong app** — the production Modal app
   is `coarse-review`. If you accidentally pushed dev code to it, the
   fix is to `git checkout main && modal deploy deploy/modal_worker.py`
   from a clean checkout. The `.github/workflows/modal-deploy.yml`
   auto-deploy from main will also recover on the next push to main.
3. **Schema migration applied to wrong DB** — the migrations in
   `deploy/*.sql` are all idempotent additive changes. No rollback
   path is usually needed; they don't drop tables or columns. If
   you need to hard-revert, do it manually in the Supabase SQL
   editor with `drop table if exists ...`.
4. **The Modal host whitelist change (step 1.7) broke production** —
   revert the commit. The change is small and self-contained.

In all cases, the preview Supabase project and preview Modal app are
independent of production — you can delete them and start over
without touching `coarse.ink`.

## Out of scope (explicit)

- **Tier 2** (stable `dev.coarse.ink` custom domain + Cloudflare Access
  email allowlist). Do this only after Tier 1 is stable and you find
  yourself wanting a memorable URL.
- **Tier 3** (Supabase Branching, `staging.coarse.ink`, feature flags,
  canary routing). Not needed at current scale. Revisit when coarse
  has multiple contributors or paying users.
- **Automated migration runner** for preview. For now, schema changes
  to preview Supabase are applied manually via the SQL editor. A
  future improvement is a GitHub Action that runs `deploy/*.sql`
  files against the preview project on every push to dev.
- **Per-PR ephemeral Supabase projects.** Supabase Branching (Pro plan)
  does this automatically. Not doing it manually — Tier 1's single
  long-lived preview project is good enough.

## Notes for the next Claude Code session

- **You're picking up a plan, not an in-progress implementation.**
  Nothing has been started. Read this file, then start at step 0.1.
- **The user's `.env.local` currently points at production Supabase.**
  After Tier 1 you might want to also swap local dev to preview by
  editing `web/.env.local` — but that's optional and outside this
  plan's scope.
- **Release blockers from the 2026-04-13 session are unrelated** —
  they live in `CHANGELOG.md` under `## Unreleased` as a warning block
  (`DEFAULT_MCP_UVX_FROM` still pinned to a git ref, needs to flip
  to `coarse-ink[mcp]==1.3.0` on the next release). Tier 0 + Tier 1
  does not touch those; the two are independent.
- **Every Modal deploy from a non-main branch requires
  `COARSE_MODAL_DEPLOY_FORCE=1`** to bypass `_enforce_deploy_branch`.
  You will be deploying dev-branch code to the preview Modal app, so
  this env var is needed on every local preview deploy.
- **Do not run any `coarse-review` CLI flow against the preview
  infrastructure until step 1.8.** The CLI writes to real Supabase via
  the configured env vars; make sure those env vars are scoped first.
- **When in doubt, verify in the Supabase dashboard.** The production
  project ID is `dgibkmnyiusglhdgzffk`. Any sign that preview traffic
  is landing in production = stop, rollback, re-check env var scoping.
