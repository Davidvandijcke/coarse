#!/usr/bin/env python3
# ruff: noqa: E402,E501,I001
"""Local browser app for running coarse on a Mac.

This intentionally avoids the hosted Next/Supabase/Modal stack. It serves a
small localhost-only UI, stores uploads/results under ``.coarse-local/``, and
uses the same ``coarse.pipeline.review_paper`` function as the packaged CLI.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import uuid
import warnings
import webbrowser
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

warnings.filterwarnings("ignore", category=DeprecationWarning, message="'cgi' is deprecated.*")

import cgi


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT / ".coarse-local"
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".tex", ".latex", ".html", ".htm", ".docx", ".epub"}
DEFAULT_MODEL = "qwen/qwen3.5-plus-02-15"
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def data_dir() -> Path:
    return Path(os.environ.get("COARSE_LOCAL_DATA_DIR", DEFAULT_DATA_DIR)).expanduser().resolve()


def jobs_dir() -> Path:
    return data_dir() / "jobs"


def job_dir(job_id: str) -> Path:
    return jobs_dir() / job_id


def job_json_path(job_id: str) -> Path:
    return job_dir(job_id) / "job.json"


def is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
    except ValueError:
        return False
    return True


def safe_filename(name: str) -> str:
    cleaned = Path(name or "paper.pdf").name.replace("\x00", "")
    return cleaned or "paper.pdf"


def read_job(job_id: str) -> dict[str, Any] | None:
    path = job_json_path(job_id)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_job(job: dict[str, Any]) -> None:
    path = job_json_path(job["id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(job, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def public_job(job: dict[str, Any]) -> dict[str, Any]:
    hidden = {"upload_path", "pid", "output_path", "log_path"}
    return {k: v for k, v in job.items() if k not in hidden}


def load_recent_jobs(limit: int = 20) -> list[dict[str, Any]]:
    if not jobs_dir().exists():
        return []
    jobs: list[dict[str, Any]] = []
    for path in jobs_dir().glob("*/job.json"):
        try:
            jobs.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    jobs.sort(key=lambda item: item.get("created_at", ""), reverse=True)
    return jobs[:limit]


def update_job(job_id: str, **updates: Any) -> dict[str, Any]:
    job = read_job(job_id)
    if job is None:
        raise FileNotFoundError(job_id)
    job.update(updates)
    write_job(job)
    return job


def run_worker(job_id: str, api_key: str) -> None:
    job = read_job(job_id)
    if job is None:
        raise SystemExit(f"Job not found: {job_id}")

    started = time.monotonic()
    update_job(job_id, status="running", started_at=utc_now(), error_message=None)
    if api_key:
        os.environ["OPENROUTER_API_KEY"] = api_key

    try:
        from coarse.pipeline import review_paper

        review, markdown, paper_text = review_paper(
            pdf_path=Path(job["upload_path"]),
            model=job.get("model") or DEFAULT_MODEL,
            skip_cost_gate=True,
            author_notes=job.get("author_notes") or None,
        )
        output_path = job_dir(job_id) / "review.md"
        paper_path = job_dir(job_id) / "paper.md"
        output_path.write_text(markdown, encoding="utf-8")
        paper_path.write_text(paper_text.full_markdown, encoding="utf-8")
        update_job(
            job_id,
            status="done",
            completed_at=utc_now(),
            duration_seconds=round(time.monotonic() - started, 1),
            paper_title=review.title,
            domain=review.domain,
            taxonomy=review.taxonomy,
            result_markdown=markdown,
            paper_markdown=paper_text.full_markdown,
            output_path=str(output_path),
        )
    except BaseException as exc:
        update_job(
            job_id,
            status="failed",
            completed_at=utc_now(),
            duration_seconds=round(time.monotonic() - started, 1),
            error_message=f"{type(exc).__name__}: {exc}",
        )
        raise


def spawn_worker(job_id: str, api_key: str) -> int:
    log_path = job_dir(job_id) / "worker.log"
    log_file = log_path.open("ab")
    proc = subprocess.Popen(
        [sys.executable, str(Path(__file__).resolve()), "--worker", job_id],
        cwd=str(ROOT),
        env={
            **os.environ,
            "COARSE_LOCAL_WORKER_API_KEY": api_key,
            "LITELLM_LOCAL_MODEL_COST_MAP": "True",
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
        },
        stdout=log_file,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    update_job(job_id, pid=proc.pid, log_path=str(log_path))
    return proc.pid


CSS = """
:root{color-scheme:dark;--board:#18241f;--chalk:#f5f1df;--dust:#c8c0a5;--accent:#e3c565;--line:#536159;--bad:#ffb1a6;--ok:#a8e6bd}
*{box-sizing:border-box}body{margin:0;background:var(--board);color:var(--chalk);font:16px/1.5 ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
a{color:var(--accent)}header,main{width:min(1040px,calc(100vw - 32px));margin:auto}header{display:flex;justify-content:space-between;align-items:baseline;padding:28px 0 18px;border-bottom:1px solid var(--line)}
h1{font-family:Georgia,serif;font-weight:400;margin:0;font-size:34px}h2{font-family:Georgia,serif;font-weight:400;margin:32px 0 12px;font-size:24px}p{color:var(--dust)}
.panel{border:1px solid var(--line);border-radius:6px;padding:20px;margin:24px 0;background:#1d2b25}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
label{display:block;color:var(--dust);margin:0 0 6px}input,textarea,select,button{width:100%;font:inherit;border-radius:4px;border:1px solid var(--line);padding:11px 12px;background:#111a16;color:var(--chalk)}
input[type=file]{padding:18px;border-style:dashed}textarea{min-height:92px;resize:vertical}.full{grid-column:1/-1}
button{background:var(--accent);border-color:var(--accent);color:#15130b;font-weight:700;cursor:pointer}button.secondary{background:transparent;color:var(--chalk);border-color:var(--line)}
.status{display:inline-flex;gap:8px;align-items:center;padding:4px 9px;border:1px solid var(--line);border-radius:99px;color:var(--dust);font-size:14px}.done{color:var(--ok)}.failed,.cancelled{color:var(--bad)}
.jobs{display:grid;gap:10px}.job{display:flex;justify-content:space-between;gap:16px;align-items:center;border:1px solid var(--line);border-radius:6px;padding:12px 14px;background:#15211c}
pre{white-space:pre-wrap;overflow:auto;border:1px solid var(--line);border-radius:6px;padding:16px;background:#101815;color:var(--chalk)}.actions{display:flex;gap:10px}.actions a,.actions form{flex:1}
@media(max-width:720px){.grid{grid-template-columns:1fr}header{display:block}.job{display:block}.actions{display:block}.actions>*{margin-top:8px}}
"""


def page(title: str, body: str) -> bytes:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title><style>{CSS}</style></head><body>
<header><h1>'coarse local</h1><p>AI academic paper review, running on this Mac.</p></header>
<main>{body}</main></body></html>""".encode()


def home_html() -> bytes:
    recent = load_recent_jobs()
    rows = "\n".join(
        f"""<div class="job"><div><strong>{html.escape(job.get("paper_filename","paper"))}</strong><br>
<span class="status {html.escape(job.get("status",""))}">{html.escape(job.get("status","queued"))}</span>
<small>{html.escape(job.get("created_at",""))}</small></div>
<div class="actions"><a href="/review/{job["id"]}"><button type="button" class="secondary">Open</button></a></div></div>"""
        for job in recent
    )
    body = f"""
<section class="panel">
  <h2>Review A Paper</h2>
  <form method="post" action="/api/reviews" enctype="multipart/form-data">
    <div class="grid">
      <div class="full"><label>Paper file</label><input name="paper" type="file" accept=".pdf,.txt,.md,.tex,.latex,.html,.htm,.docx,.epub" required></div>
      <div><label>OpenRouter API key</label><input name="api_key" type="password" placeholder="sk-or-v1-..."></div>
      <div><label>Model</label><input name="model" value="{DEFAULT_MODEL}"></div>
      <div class="full"><label>Author notes</label><textarea name="author_notes" maxlength="2000" placeholder="Optional focus areas for the review"></textarea></div>
      <div class="full"><button type="submit">Start Review</button></div>
    </div>
  </form>
  <p>Supported local formats: PDF, TXT, Markdown, LaTeX, DOCX, HTML, and EPUB. Reviews can take 30-60 minutes and use your provider account directly.</p>
</section>
<section><h2>Recent Reviews</h2><div class="jobs">{rows or "<p>No local reviews yet.</p>"}</div></section>
"""
    return page("coarse local", body)


def review_html(job_id: str) -> bytes:
    job = read_job(job_id)
    if job is None:
        return page("Review not found", "<h2>Review not found</h2>")
    status = html.escape(job.get("status", "queued"))
    title = html.escape(job.get("paper_title") or job.get("paper_filename") or "Review")
    result = job.get("result_markdown")
    error = job.get("error_message")
    refresh = "" if status in {"done", "failed", "cancelled"} else '<meta http-equiv="refresh" content="10">'
    body = f"""
<script>
async function poll() {{
  const r = await fetch('/api/reviews/{job_id}');
  const j = await r.json();
  document.getElementById('status').textContent = j.status;
  if (!['done','failed','cancelled'].includes(j.status)) setTimeout(poll, 5000);
  if (['done','failed','cancelled'].includes(j.status)) location.reload();
}}
if (!['done','failed','cancelled'].includes('{status}')) setTimeout(poll, 5000);
</script>
{refresh}
<section class="panel">
  <h2>{title}</h2>
  <p><span id="status" class="status {status}">{status}</span> model: {html.escape(job.get("model") or DEFAULT_MODEL)}</p>
  <div class="actions">
    <a href="/"><button type="button" class="secondary">New Review</button></a>
    <a href="/api/reviews/{job_id}/download"><button type="button" class="secondary">Download Markdown</button></a>
    <form method="post" action="/api/reviews/{job_id}/cancel"><button type="submit" class="secondary">Cancel</button></form>
  </div>
</section>
"""
    if result:
        body += f"<h2>Review</h2><pre>{html.escape(result)}</pre>"
    elif error:
        body += f"<h2>Error</h2><pre>{html.escape(error)}</pre>"
    else:
        log_tail = ""
        log_path = job.get("log_path")
        if log_path and Path(log_path).exists():
            log_tail = Path(log_path).read_text(encoding="utf-8", errors="replace")[-4000:]
        body += f"<p>The review worker is running. This page updates automatically.</p><pre>{html.escape(log_tail)}</pre>"
    return page(title, body)


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True


class Handler(BaseHTTPRequestHandler):
    server_version = "coarse-local/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))

    def send_bytes(self, body: bytes, status: int = 200, content_type: str = "text/html") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, value: Any, status: int = 200) -> None:
        self.send_bytes(json.dumps(value).encode(), status, "application/json")

    def redirect(self, location: str) -> None:
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", location)
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]
        if parsed.path == "/":
            self.send_bytes(home_html())
        elif len(parts) == 2 and parts[0] == "review" and is_uuid(parts[1]):
            self.send_bytes(review_html(parts[1]))
        elif len(parts) == 3 and parts[:2] == ["api", "reviews"] and is_uuid(parts[2]):
            job = read_job(parts[2])
            self.send_json(public_job(job) if job else {"error": "not found"}, 200 if job else 404)
        elif len(parts) == 4 and parts[:2] == ["api", "reviews"] and parts[3] == "download" and is_uuid(parts[2]):
            job = read_job(parts[2])
            if not job or not job.get("result_markdown"):
                self.send_json({"error": "review not ready"}, 404)
                return
            body = job["result_markdown"].encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            self.send_header("Content-Disposition", f'attachment; filename="{parts[2]}_review.md"')
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_bytes(page("Not found", "<h2>Not found</h2>"), 404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]
        if parsed.path == "/api/reviews":
            self.create_review()
        elif len(parts) == 4 and parts[:2] == ["api", "reviews"] and parts[3] == "cancel" and is_uuid(parts[2]):
            self.cancel_review(parts[2])
        else:
            self.send_json({"error": "not found"}, 404)

    def create_review(self) -> None:
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": self.headers.get("Content-Type", ""),
                "CONTENT_LENGTH": self.headers.get("Content-Length", "0"),
            },
        )
        file_item = form["paper"] if "paper" in form else None
        if file_item is None or not getattr(file_item, "filename", ""):
            self.send_json({"error": "paper file required"}, 400)
            return
        filename = safe_filename(file_item.filename)
        ext = Path(filename).suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            self.send_json({"error": f"unsupported format: {ext}"}, 400)
            return

        job_id = str(uuid.uuid4())
        directory = job_dir(job_id)
        directory.mkdir(parents=True, exist_ok=True)
        upload_path = directory / filename
        with upload_path.open("wb") as dest:
            shutil.copyfileobj(file_item.file, dest)

        model = (form.getfirst("model") or DEFAULT_MODEL).strip()[:128] or DEFAULT_MODEL
        author_notes = (form.getfirst("author_notes") or "").strip()[:2000]
        api_key = (form.getfirst("api_key") or "").strip()
        job = {
            "id": job_id,
            "paper_filename": filename,
            "status": "queued",
            "paper_title": None,
            "model": model,
            "domain": None,
            "taxonomy": None,
            "result_markdown": None,
            "paper_markdown": None,
            "cost_usd": None,
            "duration_seconds": None,
            "error_message": None,
            "created_at": utc_now(),
            "completed_at": None,
            "author_notes": author_notes,
            "upload_path": str(upload_path),
        }
        write_job(job)
        spawn_worker(job_id, api_key)
        self.redirect(f"/review/{job_id}")

    def cancel_review(self, job_id: str) -> None:
        job = read_job(job_id)
        if job is None:
            self.send_json({"error": "not found"}, 404)
            return
        if job.get("status") not in {"queued", "running"}:
            self.redirect(f"/review/{job_id}")
            return
        pid = job.get("pid")
        if isinstance(pid, int):
            try:
                os.killpg(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            except PermissionError:
                try:
                    os.kill(pid, signal.SIGTERM)
                except OSError:
                    pass
        update_job(
            job_id,
            status="cancelled",
            completed_at=utc_now(),
            error_message="Review cancelled by user",
        )
        self.redirect(f"/review/{job_id}")


def serve(host: str, port: int, open_browser: bool) -> None:
    data_dir().mkdir(parents=True, exist_ok=True)
    server = LocalServer((host, port), Handler)
    url = f"http://{host}:{server.server_port}"
    print(f"coarse local app: {url}", flush=True)
    print(f"data directory: {data_dir()}", flush=True)
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping coarse local app.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local coarse browser app.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-open", action="store_true", help="Do not open the browser automatically.")
    parser.add_argument("--worker", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        run_worker(args.worker, os.environ.get("COARSE_LOCAL_WORKER_API_KEY", ""))
        return
    serve(args.host, args.port, not args.no_open)


if __name__ == "__main__":
    main()
