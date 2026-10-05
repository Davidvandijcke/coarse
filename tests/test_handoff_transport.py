"""Exercise the real HTTP handoff boundary for every subscription host.

Only review reasoning is stubbed; bundle fetch, source download, local output,
finalization POST, and destination/query preservation use the real CLI paths.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

import pytest

from coarse.cli_review import main
from coarse.models import HEADLESS_DEFAULT_MODELS
from coarse.types import OverviewFeedback, OverviewIssue, PaperText, Review


@pytest.fixture
def handoff_server():
    events = []
    source = "# Handoff transport fixture\n\nThis is a synthetic test paper.\n"

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def respond(self, status, payload, content_type="application/json"):
            body = payload.encode() if isinstance(payload, str) else json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            events.append(("GET", self.path))
            if self.path.startswith("/h/token?"):
                assert self.headers["Accept"] == "application/json"
                self.respond(
                    200,
                    {
                        "paper_id": "00000000-0000-4000-8000-000000000000",
                        "paper_title": "fixture.md",
                        "signed_download_url": origin + "/paper.md?signature=a%2Bb&expires=123",
                        "callback_url": origin + "/finalize?bypass=test%2Bvalue&cookie=true",
                        "finalize_token": "test-finalize-token",
                    },
                )
            elif self.path.startswith("/paper.md?"):
                self.respond(200, source, "text/markdown")
            else:
                self.respond(404, {"error": "unexpected path"})

        def do_POST(self):
            payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            events.append(("POST", self.path, payload))
            self.respond(200, {"review_url": origin + "/review/test?token=test-access"})

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    origin = f"http://127.0.0.1:{server.server_port}"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield origin, events, source
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.mark.parametrize("host", ["codex", "claude", "gemini"])
@pytest.mark.parametrize("wrapper", ["{}", "[Paper]({})", "<{}>", "`{}`"])
def test_handoff_transport_round_trip(host, wrapper, handoff_server, tmp_path, capsys):
    origin, events, source = handoff_server
    handoff_path = "/h/token?bypass=test%2Bvalue&cookie=true"
    model = HEADLESS_DEFAULT_MODELS[host]
    review = Review(
        title="Handoff transport fixture",
        domain="social_sciences/economics",
        taxonomy="academic/research_paper",
        date="10/05/2026",
        overall_feedback=OverviewFeedback(
            issues=[
                OverviewIssue(title=f"Test {i}", body="Synthetic fixture feedback.")
                for i in range(4)
            ]
        ),
        detailed_comments=[],
    )
    captured = {}

    def reason(paper_path, **kwargs):
        assert paper_path.read_text() == source
        captured.update(kwargs)
        return review, "# Synthetic review\n", PaperText(full_markdown=source, token_estimate=15)

    with patch("coarse.headless_review.run_headless_review", side_effect=reason):
        result = main(
            [
                "--handoff",
                wrapper.format(origin + handoff_path),
                "--host",
                host,
                "--model",
                model,
                "--effort",
                "high",
                "--output-dir",
                str(tmp_path),
            ]
        )

    assert result == 0
    assert captured["host"] == host
    assert captured["model"] == model
    assert captured["effort"] == "high"
    assert events[0] == ("GET", handoff_path)
    assert events[1] == ("GET", "/paper.md?signature=a%2Bb&expires=123")
    assert len(events) == 3
    method, path, payload = events[2]
    assert (method, path) == ("POST", "/finalize?bypass=test%2Bvalue&cookie=true")
    assert payload["token"] == "test-finalize-token"
    assert payload["paper_markdown"] == source
    assert payload["markdown"] == "# Synthetic review\n"
    assert host in payload["model"]
    assert len(list(tmp_path.glob("*_review_*.md"))) == 1
    assert origin + "/review/test?token=test-access" in capsys.readouterr().out
