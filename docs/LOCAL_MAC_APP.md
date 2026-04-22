# Local Mac App

This repo includes a localhost-only browser app for running coarse on a Mac
without Supabase, Modal, Vercel, or Node dependencies.

## Start

From the repo root:

```bash
make local-app
```

Then open:

```text
http://127.0.0.1:8765
```

The server binds to `127.0.0.1` by default, so it is only reachable from this
Mac.

## Features

- Upload and review PDF, TXT, Markdown, LaTeX, DOCX, HTML, and EPUB files.
- Use the same `coarse.pipeline.review_paper()` pipeline as the CLI.
- Choose any LiteLLM/OpenRouter model string.
- Paste an OpenRouter API key per run, without storing it in the job record.
- Add optional author notes that are passed into the review pipeline.
- Watch job status in the browser with automatic polling.
- Download the finished markdown review.
- Cancel queued or running local subprocess jobs.
- Keep local uploads, logs, extracted markdown, and reviews under
  `.coarse-local/jobs/`.

## Network Behavior

The local browser app serves only `127.0.0.1` and the page's JavaScript only
calls local `/api/...` routes. The app also sets
`LITELLM_LOCAL_MODEL_COST_MAP=True` so LiteLLM uses its bundled pricing map
instead of fetching the map from GitHub at import time.

It also sets `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` so optional
Docling/Transformer extraction paths fail locally instead of silently
downloading model assets.

During an actual review, the review pipeline may make provider/API calls needed
to do the work:

- OpenRouter or direct LLM provider calls through LiteLLM.
- OpenRouter file-parser/OCR calls for PDF extraction.
- Perplexity Sonar through OpenRouter for literature search when an
  OpenRouter key is available.
- arXiv API fallback literature search.

The local app does not call Supabase, Modal, Vercel, Resend, Cloudflare
Turnstile, the hosted coarse web app, or any external upload service.

## Notes

The hosted `web/` app has production-only features that depend on cloud
infrastructure: Supabase storage/database, Modal workers, Resend email, and
Cloudflare Turnstile. The local app replaces those pieces with local disk
storage and a local Python worker while preserving the actual review pipeline.

To start without opening a browser automatically:

```bash
scripts/run_local_mac_app.sh --no-open
```

To pass app arguments through `make`, use `LOCAL_APP_ARGS`:

```bash
make local-app LOCAL_APP_ARGS="--port 8770 --no-open"
```

Install optional Docling OCR support separately if you want Docling-specific
fallback extraction:

```bash
PYTHON=/Users/leoprice/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
$PYTHON -m pip install -e '.[docling]'
```
