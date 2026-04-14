# AGENTS.md — coarse

This repo uses `dev` as the integration branch and `main` as the
production branch.

For any substantial deploy-affecting change, the default workflow is:

1. Land the change on a feature branch into `dev`.
2. Let Vercel create a preview deployment for that branch.
3. Let `.github/workflows/modal-preview-deploy.yml` deploy both Modal
   apps (`deploy/modal_worker.py` and `deploy/mcp_server.py`) into the
   Modal `preview` environment from `dev`.
4. Validate the change against preview Vercel + preview Supabase +
   preview Modal before touching `main`.
5. Merge `dev` to `main` only after preview passes.
6. Let `.github/workflows/modal-deploy.yml` deploy both Modal apps to
   production from `main`.

Hard rules:

- Do not use local dev against production Supabase for schema or worker
  validation when preview exists.
- Do not manually `modal deploy` production from a non-`main` branch.
- Treat preview as the mandatory soak environment for any big update
  that touches `src/coarse/`, `deploy/`, web API routes, database
  schema, or deployment config.

Primary operator docs:

- [deploy/PREVIEW_ENVIRONMENTS.md](/Users/davidvandijcke/University%20of%20Michigan%20Dropbox/David%20Van%20Dijcke/coarse/deploy/PREVIEW_ENVIRONMENTS.md)
- [deploy/DEPLOY.md](/Users/davidvandijcke/University%20of%20Michigan%20Dropbox/David%20Van%20Dijcke/coarse/deploy/DEPLOY.md)
- [CLAUDE.md](/Users/davidvandijcke/University%20of%20Michigan%20Dropbox/David%20Van%20Dijcke/coarse/CLAUDE.md)
