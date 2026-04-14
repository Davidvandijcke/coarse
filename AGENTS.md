# AGENTS.md — coarse

This repo uses `dev` as the integration branch and `main` as the
production branch.

For any substantial deploy-affecting change, the default workflow is:

1. Land the change on a feature branch into `dev`.
2. Use the Vercel preview deployment for the latest `dev` commit as the
   signoff site.
3. Let `.github/workflows/modal-preview-deploy.yml` deploy both Modal
   apps (`deploy/modal_worker.py` and `deploy/mcp_server.py`) into the
   Modal `preview` environment from `dev` when the change touches
   deploy-relevant paths, or rerun it manually on `dev` if needed.
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
- Treat this as a required human release discipline. The repo does not
  currently auto-prove that the preview smoke test happened.

## PyPI publishing is tag-driven, NOT main-merge-driven

`coarse-ink` is **not** auto-published when `dev` merges into `main`.
The `.github/workflows/release.yml` workflow only fires on
`push: tags: v*`, and the build job hard-fails unless the tag matches
both `pyproject.toml` `version` and `src/coarse/__init__.py`
`__version__`. Substantial changes can sit on `main` indefinitely
without ever shipping to PyPI.

When a release PR `dev` → `main` lands, the release steps are:

1. In the release PR, bump the version in both files and move
   CHANGELOG entries from `## Unreleased` to `## vX.Y.Z — YYYY-MM-DD`:
   - `pyproject.toml` → `version = "X.Y.Z"`
   - `src/coarse/__init__.py` → `__version__ = "X.Y.Z"`
2. Merge the PR to `main`.
3. Tag and push from `main`:
   ```bash
   git checkout main && git pull
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```
4. The `Release` workflow runs: tests → version-consistency check →
   `uv build` → PyPI Trusted Publishing (no API token, OIDC via the
   `pypi` GitHub environment).

Skipping step 3 leaves PyPI stale no matter how much code lands on
`main`. Doing step 3 without step 1 fails the version-consistency
check by design.

Changes outside `src/coarse/` (web, deploy, .github/workflows, data,
output) ship through their own paths and do not require a PyPI
release. Don't cut a new tag for web-only or deploy-only work; check
`git diff vX.Y.Z..main -- src/coarse/` first to see if the package
itself actually changed.

Primary operator docs:

- [deploy/PREVIEW_ENVIRONMENTS.md](deploy/PREVIEW_ENVIRONMENTS.md)
- [deploy/DEPLOY.md](deploy/DEPLOY.md)
- [CLAUDE.md](CLAUDE.md) — full project overview, pipeline, package structure, git workflow
