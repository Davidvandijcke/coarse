"""coarse MCP server — capability-based, zero ambient credentials.

Exposes coarse's deterministic pipeline (extraction, structure parsing,
quote verification, synthesis, prompt rendering) as MCP tools so
Claude.ai custom connectors, Claude Code, Gemini CLI, and the ChatGPT
Apps SDK can drive a paper review using the host's own LLM
subscription. The host model runs the review stages (overview,
per-section, crossref, critique); this server only does the
deterministic work and hands back ready-to-use prompts.

## Security model

**The MCP server holds zero persistent credentials.** No Supabase
service key, no Modal secrets, no per-user auth tokens. It accepts
each tool call on its own merits and makes no ambient queries. That
matters because the server is publicly reachable (via Modal on prod,
or via whatever tunnel a dev points at it), and it has no auth on
its HTTP surface today beyond whatever MCP connector install flow
the host chose. A stolen tunnel URL must not grant read access to
anyone else's paper or write access to any review.

State flows through the server entirely via **capability handoffs**
minted by the Next.js backend:

- **Ingestion**: the web form POSTs to ``/api/mcp-handoff`` which mints
  a 15-minute Supabase signed download URL scoped to one PDF and a
  60-minute single-use ``finalize_token``. Both capabilities travel
  in the clipboard prompt the user pastes into their chat host.

- **Extraction**: the host LLM calls ``upload_paper_url`` with the
  signed URL. The MCP server downloads, extracts, and stores state
  in its own in-process dict (``InMemoryStore``) keyed by paper_id.
  State is intentionally ephemeral — container restart loses it,
  and the host can always re-upload via the still-valid signed URL.

- **Persistence**: when the host calls ``finalize_review`` with the
  ``finalize_token`` + ``callback_url``, the server renders the
  markdown locally and POSTs it to
  ``https://coarse.vercel.app/api/mcp-finalize``. The Next.js route
  validates the token, consumes it, and upserts the ``reviews`` row.
  The MCP server never touches Supabase.

## OpenRouter key handling

The ingestion tools (``upload_paper_url``, ``upload_paper_bytes``,
``upload_paper_path``) take an ``openrouter_key`` argument used
ONLY to fund the Mistral OCR + structure LLM call during extraction.
The key is installed into ``OPENROUTER_API_KEY`` via the
``scoped_openrouter_key`` context manager — same save/restore
pattern as ``modal_worker.py:260-265``. It is never stored, never
logged, and never sent to the host LLM in a tool response.

## Running modes

1. **Local development**: ``uv run python deploy/mcp_server.py``
   starts a streamable-HTTP server on ``127.0.0.1:8765``.
   ``finalize_review`` defaults to the in-memory persistence path
   (no callback needed) so tests + the reference client in
   ``deploy/mcp_test_client.py`` run without the web backend.

2. **Production**: ``modal deploy deploy/mcp_server.py`` publishes the
   same server as a Modal ASGI app with NO secrets attached. Every
   review routed through it comes in via the capability-handoff path
   from the web frontend.
"""

from __future__ import annotations

import base64
import ipaddress
import json
import logging
import os
import re
import tempfile
import threading
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# Safety caps
# ---------------------------------------------------------------------------

_MAX_PAPER_BYTES = 100 * 1024 * 1024  # 100 MB — mirrors extraction.py
_MAX_URL_REDIRECTS = 5
_URL_FETCH_TIMEOUT = 120  # seconds
_DEFAULT_SITE_URL = "https://coarse.vercel.app"
_DEFAULT_SUPABASE_HOST_SUFFIXES = (".supabase.co", ".supabase.in")
_SUPPORTED_EXT_FOR_URL = frozenset(
    {
        ".pdf",
        ".txt",
        ".md",
        ".tex",
        ".latex",
        ".html",
        ".htm",
        ".docx",
        ".epub",
    }
)
_OPENROUTER_ENV_LOCK = threading.RLock()


# ---------------------------------------------------------------------------
# Paper-state store — Supabase when configured, in-memory otherwise
# ---------------------------------------------------------------------------


class PaperStore:
    """Abstract store for extracted paper state keyed by paper_id."""

    def insert_paper(self, paper_id: str, row: dict) -> None:
        raise NotImplementedError

    def get_paper(self, paper_id: str) -> dict | None:
        raise NotImplementedError

    def insert_review(self, review_id: str, row: dict) -> None:
        raise NotImplementedError


class InMemoryStore(PaperStore):
    """In-process dict store for local development only.

    State is lost when the process exits. Every call path that writes here
    grabs ``_lock`` first so the MCP server remains safe under the default
    FastMCP thread pool.
    """

    def __init__(self) -> None:
        self._papers: dict[str, dict] = {}
        self._reviews: dict[str, dict] = {}
        self._lock = threading.Lock()

    def insert_paper(self, paper_id: str, row: dict) -> None:
        with self._lock:
            self._papers[paper_id] = row

    def get_paper(self, paper_id: str) -> dict | None:
        with self._lock:
            row = self._papers.get(paper_id)
            return dict(row) if row is not None else None

    def insert_review(self, review_id: str, row: dict) -> None:
        with self._lock:
            self._reviews[review_id] = row


# NOTE: There is deliberately no SupabaseStore variant here. The MCP
# server must not hold a Supabase service key — giving it one would
# grant a publicly-reachable (via Modal / tunnel) server unchecked
# read/write access to every paper and every review in the database,
# and the server has no per-request auth to gate that with. Instead,
# paper state lives in-process for the duration of a review session,
# and finalized reviews are persisted via a *capability callback* to
# the Next.js backend's /api/mcp-finalize route, authenticated by a
# single-use finalize_token that was minted when the web form handed
# the paper off. See deploy/migrate_mcp_handoff.sql and
# web/src/app/api/mcp-handoff/route.ts for the matching pieces.


# ---------------------------------------------------------------------------
# OpenRouter key save/restore (copies modal_worker.py pattern)
# ---------------------------------------------------------------------------


@contextmanager
def scoped_openrouter_key(key: str):
    """Install ``key`` as ``OPENROUTER_API_KEY`` for the duration of the block.

    Mirrors the save/restore pattern in ``deploy/modal_worker.py:260-265``.
    The container may be reused across tool calls; we must not leak a user's
    key into the next call's environment. Clear before restoring so a raising
    restore leaves the env in a clean state.
    """
    if not key or not key.strip():
        raise ValueError("openrouter_key must be non-empty")
    key = key.strip()
    with _OPENROUTER_ENV_LOCK:
        original = os.environ.get("OPENROUTER_API_KEY")
        os.environ["OPENROUTER_API_KEY"] = key
        try:
            yield
        finally:
            os.environ.pop("OPENROUTER_API_KEY", None)
            if original is not None:
                os.environ["OPENROUTER_API_KEY"] = original


def _public_http_mode() -> bool:
    """Return True when the server is handling public HTTP traffic."""
    return os.environ.get("COARSE_MCP_PUBLIC_HTTP", "").strip() == "1"


def _configured_site_origins() -> set[str]:
    """Return the allowed callback origins for finalize_review."""
    origins = {_DEFAULT_SITE_URL}
    if not _public_http_mode():
        origins.update({"http://localhost:3000", "http://127.0.0.1:3000"})
    for raw in (
        os.environ.get("NEXT_PUBLIC_SITE_URL"),
        os.environ.get("SITE_URL"),
        (
            f"https://{os.environ['NEXT_PUBLIC_VERCEL_URL']}"
            if os.environ.get("NEXT_PUBLIC_VERCEL_URL")
            else None
        ),
    ):
        if not raw:
            continue
        parsed = urlparse(raw)
        if parsed.scheme in ("http", "https") and parsed.netloc:
            origins.add(f"{parsed.scheme}://{parsed.netloc}")
    return origins


def _configured_supabase_hosts() -> set[str]:
    """Return the expected Supabase hosts for signed storage URLs."""
    hosts: set[str] = set()
    for raw in (os.environ.get("NEXT_PUBLIC_SUPABASE_URL"), os.environ.get("SUPABASE_URL")):
        if not raw:
            continue
        parsed = urlparse(raw)
        if parsed.hostname:
            hosts.add(parsed.hostname.lower())
    return hosts


def _is_ip_literal(hostname: str) -> bool:
    try:
        ipaddress.ip_address(hostname)
        return True
    except ValueError:
        return False


def _is_loopbackish_host(hostname: str) -> bool:
    lowered = hostname.lower()
    if lowered in {"localhost", "localhost.localdomain"} or lowered.endswith(".localhost"):
        return True
    try:
        ip = ipaddress.ip_address(lowered)
    except ValueError:
        return False
    return ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_reserved


def _validate_signed_state_url(url: str) -> None:
    """Allow only signed Supabase storage URLs for the MCP state blob."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError(f"signed_state_url must be a fully-qualified http(s) URL, got {url!r}")
    hostname = (parsed.hostname or "").lower()
    if not hostname:
        raise ValueError("signed_state_url is missing a hostname")
    if _is_ip_literal(hostname):
        raise ValueError("signed_state_url must use a configured Supabase hostname, not a raw IP")
    configured_hosts = _configured_supabase_hosts()
    if configured_hosts:
        if hostname not in configured_hosts:
            raise ValueError(
                f"signed_state_url host {hostname!r} does not match the configured Supabase host"
            )
    elif not hostname.endswith(_DEFAULT_SUPABASE_HOST_SUFFIXES):
        raise ValueError(
            "signed_state_url must point at a Supabase Storage signed URL for the papers bucket"
        )
    if "/storage/v1/object/sign/papers/" not in parsed.path:
        raise ValueError("signed_state_url must target the signed papers bucket path")
    if not parsed.path.endswith(".mcp.json"):
        raise ValueError("signed_state_url must point to a .mcp.json state blob")
    if not parsed.query:
        raise ValueError("signed_state_url must include a signed query string")


def _validate_callback_url(url: str) -> None:
    """Allow only coarse's own finalize callback endpoint."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError(f"callback_url must be a fully-qualified http(s) URL, got {url!r}")
    hostname = (parsed.hostname or "").lower()
    if not hostname:
        raise ValueError("callback_url is missing a hostname")
    if _public_http_mode() and _is_loopbackish_host(hostname):
        raise ValueError(
            "callback_url cannot target localhost or a private host in public HTTP mode"
        )
    if parsed.path.rstrip("/") != "/api/mcp-finalize":
        raise ValueError("callback_url must point to /api/mcp-finalize")
    origin = f"{parsed.scheme}://{parsed.netloc}"
    if origin not in _configured_site_origins():
        raise ValueError(f"callback_url origin {origin!r} is not an allowed coarse site origin")


# ---------------------------------------------------------------------------
# URL fetch for upload_paper_url
# ---------------------------------------------------------------------------


def _fetch_to_tempfile(url: str) -> Path:
    """Download ``url`` to a temp file, enforce extension + size caps.

    Validates the extension from the URL path (not Content-Type — servers
    lie) and refuses anything not in the extractable set. Size cap mirrors
    ``extraction._MAX_FILE_SIZE``.
    """
    import requests

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"url must be http(s), got {parsed.scheme!r}")

    # Derive ext from the URL path. Query strings don't contain the ext;
    # a redirect to a different URL may change it (we re-check after).
    path_suffix = Path(parsed.path).suffix.lower()
    if path_suffix not in _SUPPORTED_EXT_FOR_URL:
        raise ValueError(
            f"URL must point to a file with one of: {', '.join(sorted(_SUPPORTED_EXT_FOR_URL))}"
        )

    with requests.get(
        url,
        stream=True,
        timeout=_URL_FETCH_TIMEOUT,
        allow_redirects=True,
    ) as resp:
        resp.raise_for_status()
        # Pick the tempfile extension from the *original* URL path. We
        # already validated it against the supported set above. arXiv
        # (and other sites) redirect ``.../paper.pdf`` to ``.../paper``
        # without the extension, so Path(resp.url).suffix is unreliable
        # — it would trip this branch on ``2301.00001`` and report
        # extension='.00001'. Only bother re-validating the final URL
        # if it has a suffix that looks like a real, *different*
        # extension (possible malicious redirect to .exe etc.).
        final_ext = Path(urlparse(resp.url).path).suffix.lower()
        if (
            final_ext
            and final_ext != path_suffix
            and final_ext not in _SUPPORTED_EXT_FOR_URL
            # Reject only if the final ext looks like a real extension
            # (alpha-only, ≤5 chars). Numeric suffixes like ``.00001``
            # from arXiv's identifier format are spurious.
            and final_ext[1:].isalpha()
            and len(final_ext) <= 5
        ):
            raise ValueError(f"redirect landed on unsupported extension {final_ext!r}")

        tmp = tempfile.NamedTemporaryFile(suffix=path_suffix, delete=False)
        total = 0
        try:
            for chunk in resp.iter_content(chunk_size=64 * 1024):
                if not chunk:
                    continue
                total += len(chunk)
                if total > _MAX_PAPER_BYTES:
                    tmp.close()
                    os.unlink(tmp.name)
                    raise ValueError(f"file exceeds {_MAX_PAPER_BYTES // 1024 // 1024} MB cap")
                tmp.write(chunk)
        finally:
            tmp.close()
        return Path(tmp.name)


def _decode_bytes_to_tempfile(filename: str, data_b64: str) -> Path:
    """Decode a base64-encoded file payload into a temp file with the right extension."""
    ext = Path(filename).suffix.lower()
    if ext not in _SUPPORTED_EXT_FOR_URL:
        raise ValueError(f"filename must have one of: {', '.join(sorted(_SUPPORTED_EXT_FOR_URL))}")
    try:
        data = base64.b64decode(data_b64, validate=True)
    except Exception as exc:
        raise ValueError(f"data_b64 is not valid base64: {exc}") from exc
    if len(data) > _MAX_PAPER_BYTES:
        raise ValueError(f"file exceeds {_MAX_PAPER_BYTES // 1024 // 1024} MB cap")
    tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    try:
        tmp.write(data)
    finally:
        tmp.close()
    return Path(tmp.name)


# ---------------------------------------------------------------------------
# Pipeline wiring
# ---------------------------------------------------------------------------


def _run_extraction(file_path: Path) -> tuple[Any, Any]:
    """Call coarse's extract_and_structure helper with a fresh LLMClient.

    Imported lazily so the MCP server module itself can be imported without
    paying litellm's import cost when callers only want to probe tool
    metadata (e.g. MCP Inspector discovery).
    """
    from coarse import extract_and_structure
    from coarse.config import CoarseConfig
    from coarse.llm import LLMClient

    # Force extraction QA off on the MCP path for now — it needs GEMINI_API_KEY,
    # which we don't ask the user for. The auto-trigger on high garble ratio
    # still fires inside extract_and_structure if the env key happens to be set.
    config = CoarseConfig(extraction_qa=False)
    client = LLMClient(config=config)
    return extract_and_structure(file_path, client, config=config, run_qa=False)


def _structure_to_dict(structure) -> dict:
    """Serialize a PaperStructure to a JSON-safe dict for storage."""
    return json.loads(structure.model_dump_json())


def _structure_from_dict(data: dict):
    """Rehydrate a PaperStructure from stored JSON."""
    from coarse.types import PaperStructure

    return PaperStructure.model_validate(data)


def _section_summary(structure) -> list[dict]:
    """Return the compact {id, title, type, chars} list the host uses to iterate."""
    return [
        {
            "id": str(sec.number),
            "title": sec.title,
            "type": sec.section_type.value,
            "chars": len(sec.text or ""),
            "math_content": bool(sec.math_content),
        }
        for sec in structure.sections
    ]


def _find_section(structure, section_id: str):
    """Look up a section by its stringified number within a structure."""
    for sec in structure.sections:
        if str(sec.number) == section_id:
            return sec
    return None


def _detect_focus(section) -> str:
    """Replicate ``pipeline._detect_section_focus`` without importing the agents."""
    from coarse.types import SectionType

    if section.math_content:
        return "proof"
    if section.section_type == SectionType.METHODOLOGY:
        return "methodology"
    if section.section_type == SectionType.RESULTS:
        return "results"
    if section.section_type == SectionType.RELATED_WORK:
        return "literature"
    if section.section_type in (SectionType.DISCUSSION, SectionType.CONCLUSION):
        return "discussion"
    return "general"


def _ingest_file(
    file_path: Path,
    openrouter_key: str,
    *,
    own_file: bool = True,
    paper_id: str | None = None,
) -> dict:
    """Shared ingestion body used by every ``upload_paper_*`` tool.

    Runs extraction+structure with the supplied OpenRouter key scoped to the
    env, writes a new row to the paper store, and returns the section
    summary the host LLM will iterate over.

    ``own_file`` controls whether the ingestion body unlinks the file on
    completion. ``upload_paper_url`` / ``upload_paper_bytes`` pass ``True``
    because they own the temp file they created; ``upload_paper_path``
    passes ``False`` because the file belongs to the user.

    ``paper_id`` lets callers reuse an existing UUID (e.g. the one minted
    by the web form's presign route) so the MCP review path and the web
    review path share one canonical ID. When ``None`` a fresh UUID is
    minted.
    """
    try:
        with scoped_openrouter_key(openrouter_key):
            paper_text, structure = _run_extraction(file_path)
    finally:
        if own_file:
            try:
                os.unlink(file_path)
            except FileNotFoundError:
                pass

    if paper_id is None:
        paper_id = str(uuid.uuid4())
    row = {
        "title": structure.title,
        "domain": structure.domain,
        "taxonomy": structure.taxonomy,
        "abstract": structure.abstract,
        "paper_markdown": paper_text.full_markdown,
        "structure_json": _structure_to_dict(structure),
    }
    _STORE.insert_paper(paper_id, row)

    return {
        "paper_id": paper_id,
        "title": structure.title,
        "domain": structure.domain,
        "taxonomy": structure.taxonomy,
        "section_count": len(structure.sections),
        "sections": _section_summary(structure),
        "next_step": (
            "Call get_review_prompt(paper_id, stage='overview') to get the "
            "prompts for the macro-level review pass, then iterate per "
            "section with stage='section' and section_id from the 'sections' "
            "list above."
        ),
    }


def _load_paper(paper_id: str) -> tuple[dict, Any]:
    """Fetch a paper row + reconstruct its PaperStructure or raise."""
    row = _STORE.get_paper(paper_id)
    if row is None:
        raise ValueError(
            f"paper_id {paper_id!r} not found — call upload_paper_url or "
            f"upload_paper_bytes first to ingest a paper"
        )
    raw_structure = row.get("structure_json")
    if isinstance(raw_structure, str):
        raw_structure = json.loads(raw_structure)
    if not raw_structure:
        raise ValueError(f"paper_id {paper_id!r} has no stored structure")
    return row, _structure_from_dict(raw_structure)


def _fence_untrusted_block(tag: str, text: str) -> str:
    """Wrap untrusted paper-derived text in a safe fence tag."""
    from coarse.prompts import _strip_fence_tags

    safe = _strip_fence_tags(text or "")
    return f"<{tag}>\n{safe}\n</{tag}>"


# ---------------------------------------------------------------------------
# FastMCP server + tool registration
# ---------------------------------------------------------------------------


try:
    from fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "deploy/mcp_server.py requires the 'mcp' extra. "
        "Install with `uv sync --extra mcp` or `pip install coarse-ink[mcp]`."
    ) from exc


mcp = FastMCP(
    name="coarse",
    instructions=(
        "IMPORTANT: You MUST call the tools below immediately — do not "
        "describe, plan, or narrate. Execute each step by calling the "
        "tool, wait for its result, then call the next tool.\n\n"
        "RESPONSE FORMAT: Every tool returns a JSON object with named "
        "fields (paper_id, system, user, response_schema, etc.). Parse "
        "the JSON directly — do not inspect or unwrap it.\n\n"
        "coarse is a free AI paper reviewer. You are the reviewer. This "
        "server runs only deterministic steps (extraction, prompts, quote "
        "verification, rendering). You provide the reasoning.\n\n"
        "PIPELINE — exactly 2 tool calls:\n\n"
        "1. LOAD: Call load_paper_state or upload_paper_url. The result "
        "contains review_instructions (how to review), paper_text (the "
        "full paper organized by section), and next_step. Read the "
        "review_instructions, review the paper_text, and produce a JSON "
        "object with 'overview' and 'comments' fields as described in "
        "the instructions.\n\n"
        "2. FINALIZE: Call finalize_review(paper_id=..., overview=<your "
        "overview>, comments=<your comments>, finalize_token=<if provided>, "
        "callback_url=<if provided>). Quote verification runs automatically. "
        "Show the user the review_url.\n\n"
        "QUOTE RULES: Copy quotes CHARACTER-FOR-CHARACTER from paper_text. "
        "Each quote must be 50-200 chars, unique per comment. Do NOT use "
        "section headers. Do NOT clean up OCR formatting.\n\n"
        "START IMMEDIATELY. Call the first tool NOW."
    ),
)


# Paper state is always in-memory for the duration of one review session.
# On Modal this means state lives for the lifetime of one container handling
# one review's worth of tool calls; after the container recycles the state
# is gone. That's intentional — no ambient credentials means no persistence,
# and the host LLM can always re-upload via the signed URL if the container
# rolled over mid-review.
_STORE: PaperStore = InMemoryStore()


_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def _validate_paper_id(paper_id: str | None) -> str | None:
    """Return a normalized lowercase UUID or raise.

    Accepted by the ``upload_paper_*`` tools to let the caller pin the
    MCP-side paper_id to a specific UUID — required when the host came
    through the capability-handoff flow from coarse.vercel.app, because
    the finalize_token minted by ``/api/mcp-handoff`` is bound to the
    web-side reviews.id. If the MCP server mints its own random UUID,
    ``/api/mcp-finalize`` rejects the callback with 403 "Token paper_id
    does not match request paper_id".

    Passing None (the default) returns None — the caller didn't override
    and ``_ingest_file`` will mint a fresh UUID.
    """
    if paper_id is None:
        return None
    if not isinstance(paper_id, str) or not _UUID_RE.match(paper_id):
        raise ValueError(
            f"paper_id must be a UUID string, got {paper_id!r}. When "
            f"coming from the coarse.vercel.app handoff flow, use the "
            f"paper_id that was handed to you alongside the signed URL."
        )
    return paper_id.lower()


# --- Ingestion tools ---


@mcp.tool()
def upload_paper_url(
    url: str,
    openrouter_key: str,
    paper_id: str | None = None,
) -> dict:
    """Download a paper from an HTTPS URL, extract it, and return a section map.

    The ``openrouter_key`` is used *only* for the duration of this call to
    fund Mistral OCR + structure + extraction QA. It is not persisted. The
    URL must point to one of: .pdf, .txt, .md, .tex, .latex, .html, .htm,
    .docx, .epub. Cap: 100 MB.

    Optional ``paper_id``: if supplied (must be a UUID), the MCP server
    stores the extracted state under that exact UUID instead of minting
    a fresh random one. **Use this whenever you came through the
    coarse.vercel.app capability handoff flow** — the finalize_token in
    your clipboard prompt is bound to that paper_id, so the MCP-side
    paper_id MUST match or finalize_review will fail the callback check.

    Returns a dict with ``paper_id``, ``title``, ``domain``, ``taxonomy``,
    ``section_count``, and a ``sections`` list of ``{id, title, type,
    chars, math_content}`` entries the caller can iterate.
    """
    resolved_paper_id = _validate_paper_id(paper_id)
    tmp_path = _fetch_to_tempfile(url)
    return _ingest_file(tmp_path, openrouter_key, paper_id=resolved_paper_id)


@mcp.tool()
def upload_paper_bytes(
    filename: str,
    data_b64: str,
    openrouter_key: str,
    paper_id: str | None = None,
) -> dict:
    """Ingest a paper from an inline base64-encoded file.

    Use this when the host can read a local file (Claude Code, Gemini CLI)
    and the content isn't reachable via a public URL. ``filename`` must
    have one of the supported extensions. Size cap and key handling are
    identical to ``upload_paper_url``.

    The optional ``paper_id`` override works exactly like
    ``upload_paper_url``'s — pass the UUID from your capability handoff
    prompt so the finalize_token matches.
    """
    resolved_paper_id = _validate_paper_id(paper_id)
    tmp_path = _decode_bytes_to_tempfile(filename, data_b64)
    return _ingest_file(tmp_path, openrouter_key, paper_id=resolved_paper_id)


@mcp.tool()
def upload_paper_path(
    path: str,
    openrouter_key: str,
    paper_id: str | None = None,
) -> dict:
    """Ingest a paper that lives on the MCP server's filesystem.

    Use this when the server and the file share a filesystem — always
    true in stdio mode (Claude Code / Gemini CLI spawn the server as a
    subprocess on your machine) and in local HTTP mode. When the server
    runs remotely (Modal), use ``upload_paper_url`` or
    ``upload_paper_bytes`` instead; the remote container has no view of
    your local files.

    ``path`` must be an absolute path. Relative paths are rejected
    because the MCP server's working directory is unspecified and
    accepting relatives would be a footgun. Supported extensions and
    the 100 MB size cap match the other ingestion tools. The file is
    read in place — this tool never modifies or deletes the user's
    file.
    """
    if _public_http_mode():
        raise ValueError(
            "upload_paper_path is disabled on the public HTTP MCP server. "
            "Use load_paper_state for coarse.vercel.app handoffs or "
            "upload_paper_url/upload_paper_bytes in local stdio mode."
        )
    p = Path(path).expanduser()
    if not p.is_absolute():
        raise ValueError(
            f"path must be absolute (got {path!r}); relative paths are "
            f"rejected because the MCP server's cwd is unspecified"
        )
    p = p.resolve()
    if not p.exists():
        raise ValueError(f"file not found: {p}")
    if not p.is_file():
        raise ValueError(f"not a regular file: {p}")
    ext = p.suffix.lower()
    if ext not in _SUPPORTED_EXT_FOR_URL:
        raise ValueError(
            f"unsupported extension {ext!r}; must be one of "
            f"{', '.join(sorted(_SUPPORTED_EXT_FOR_URL))}"
        )
    size = p.stat().st_size
    if size > _MAX_PAPER_BYTES:
        raise ValueError(
            f"file exceeds {_MAX_PAPER_BYTES // 1024 // 1024} MB cap "
            f"(got {size // 1024 // 1024} MB)"
        )
    resolved_paper_id = _validate_paper_id(paper_id)
    return _ingest_file(p, openrouter_key, own_file=False, paper_id=resolved_paper_id)


# NOTE: There is deliberately no ``upload_paper_from_id`` tool here.
# That function would require the MCP server to download from the
# coarse.vercel.app Supabase bucket, which in turn would require giving
# the server a service key with broad read access. The capability-based
# handoff path (web → /api/mcp-handoff → signed URL → ``load_paper_state``)
# replaces it: the web frontend mints a short-lived, paper-scoped signed
# URL for an already-extracted JSON state blob, and the host passes that
# URL to ``load_paper_state``. The MCP server only ever sees a single-use
# URL it was explicitly handed, never a Supabase credential.
#
# Result: four ingestion tools — ``upload_paper_url``, ``upload_paper_bytes``,
# and ``upload_paper_path`` for direct users (CLI, Claude Code, Gemini CLI,
# local dev); ``load_paper_state`` for the web→MCP handoff from
# coarse.vercel.app. All four run without any ambient state.


@mcp.tool()
def load_paper_state(
    signed_state_url: str,
    paper_id: str,
) -> dict:
    """Load an already-extracted paper state blob via a signed URL.

    Used by the web→MCP handoff flow from coarse.vercel.app. The
    browser already triggered /api/mcp-extract server-side, so the
    PDF has been OCR'd + structured *before* the host LLM ever sees
    it. ``signed_state_url`` is a short-lived (15-minute) Supabase
    Storage signed URL pointing at ``papers/<paper_id>.mcp.json``,
    minted by /api/mcp-handoff.

    Compared to ``upload_paper_url``:

    - No OpenRouter key argument — extraction already ran server-side
      and billed the user's key there. The host never sees the key.
    - No OCR in the tool call — the tool is a single HTTP GET of a
      JSON blob + an in-memory store write. Completes in <1 second
      on a healthy network, well under any host LLM's tool-call
      timeout ceiling.
    - Deterministic — the same blob from the same signed URL always
      rehydrates to the same in-memory state. No LLM calls at all.

    ``paper_id`` must be the UUID bound to the state blob (it's the
    same UUID embedded in the signed URL path, and the Next.js
    /api/mcp-handoff route guarantees they agree). Passing it
    explicitly lets the host's subsequent tool calls use the same
    paper_id without parsing the URL.

    Returns the same ``{paper_id, title, domain, taxonomy,
    section_count, sections, next_step}`` shape as the upload tools
    so the host's downstream tool-call loop doesn't branch.
    """
    import requests

    resolved_paper_id = _validate_paper_id(paper_id)
    if resolved_paper_id is None:
        raise ValueError("paper_id is required and must be a UUID")
    _validate_signed_state_url(signed_state_url)

    try:
        resp = requests.get(
            signed_state_url,
            timeout=30,
            headers={"User-Agent": "coarse-mcp-server/1.0"},
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Failed to GET signed_state_url: {exc}. The URL may have "
            f"expired (15-minute TTL) — ask the user to re-trigger the "
            f"handoff from coarse.vercel.app."
        ) from exc
    if not resp.ok:
        raise RuntimeError(f"signed_state_url returned HTTP {resp.status_code}: {resp.text[:200]}")
    if len(resp.content) > _MAX_PAPER_BYTES:
        raise ValueError(f"state blob exceeds {_MAX_PAPER_BYTES // 1024 // 1024} MB cap")

    try:
        blob = resp.json()
    except Exception as exc:
        raise ValueError(f"signed_state_url did not return JSON: {exc}") from exc

    required_fields = ("title", "domain", "taxonomy", "paper_markdown", "structure_json")
    missing = [f for f in required_fields if f not in blob]
    if missing:
        raise ValueError(
            f"state blob is missing required fields: {missing}. This is "
            f"a bug in the extractor (deploy/modal_worker.py::do_extract)."
        )

    # Rehydrate PaperStructure server-side (via Pydantic) so we fail
    # fast on malformed state, rather than discovering it during
    # ``get_paper_section`` or ``finalize_review``.
    structure = _structure_from_dict(blob["structure_json"])

    row = {
        "title": blob.get("title") or structure.title,
        "domain": blob.get("domain") or structure.domain,
        "taxonomy": blob.get("taxonomy") or structure.taxonomy,
        "abstract": blob.get("abstract") or structure.abstract,
        "paper_markdown": blob["paper_markdown"],
        "structure_json": blob["structure_json"],
    }
    _STORE.insert_paper(resolved_paper_id, row)

    # Build the review instructions inline so the host LLM gets
    # everything in one tool call (no need for get_review_instructions).
    from coarse.prompts import _CONTENT_BOUNDARY_NOTICE, _strip_fence_tags

    sections_block = []
    for sec in structure.sections:
        text_len = len(sec.text.strip()) if sec.text else 0
        if text_len == 0:
            continue
        if sec.section_type == "references":
            continue
        focus = _detect_focus(sec)
        safe_section_title = _strip_fence_tags(sec.title or "")
        sections_block.append(
            f"### Section {sec.number}\n"
            f"{_fence_untrusted_block('paper_section_title', safe_section_title)}\n\n"
            f"**Focus**: {focus}"
            f"{' — VERIFY PROOFS CAREFULLY' if focus == 'proof' else ''}\n"
            f"**Type**: {sec.section_type}\n\n"
            f"{_fence_untrusted_block('paper_content', sec.text)}\n"
        )

    paper_body = "\n---\n\n".join(sections_block)
    sections = _section_summary(structure)
    safe_title = _strip_fence_tags(row["title"] or "")
    safe_domain = _strip_fence_tags(row["domain"] or "")
    safe_taxonomy = _strip_fence_tags(row["taxonomy"] or "")
    abstract_block = _fence_untrusted_block("paper_abstract", row.get("abstract", ""))
    sections_wrapped = f"<paper_sections>\n{paper_body}\n</paper_sections>"

    return {
        "paper_id": resolved_paper_id,
        "title": row["title"],
        "domain": row["domain"],
        "taxonomy": row["taxonomy"],
        "section_count": len(sections),
        "sections": sections,
        "review_instructions": (
            "You are a rigorous academic peer reviewer. Produce a structured "
            "review. Your response MUST be a JSON object with two fields:\n\n"
            f"{_CONTENT_BOUNDARY_NOTICE.strip()}\n\n"
            "1. **overview**: {summary (1-2 sentences), assessment (1 paragraph), "
            "issues (4-6 titled macro issues, each {title, body}), "
            "recommendation (accept/revise_and_resubmit/reject), "
            "revision_targets (3-5 strings)}\n\n"
            "2. **comments**: flat list of {number (int), title (short), "
            "quote (VERBATIM 50-200 char passage copied character-for-character "
            "from the paper — each comment must have a DIFFERENT quote, do NOT "
            "use section headers or generic sentences), feedback (constructive), "
            "severity (critical/major/minor), confidence (high/medium/low)}\n\n"
            "Aim for 10-25 comments. Review ALL sections including appendix "
            "proofs. For sections marked 'VERIFY PROOFS CAREFULLY', check "
            "each derivation step-by-step.\n\n"
            "Respond with ONLY the JSON — no prose outside it."
        ),
        "paper_text": (
            f"{_fence_untrusted_block('paper_title', safe_title)}\n\n"
            f"{_fence_untrusted_block('paper_domain', safe_domain)}\n\n"
            f"{_fence_untrusted_block('paper_taxonomy', safe_taxonomy)}\n\n"
            f"## Abstract\n\n{abstract_block}\n\n"
            f"## Sections\n\n{sections_wrapped}"
        ),
        "next_step": (
            "Read review_instructions above. Use paper_text as the paper "
            "to review. Produce the JSON review, then call finalize_review."
        ),
    }


# --- Read tools (no key needed) ---


@mcp.tool()
def get_paper_section(paper_id: str, section_id: str) -> dict:
    """Return the full text of one section of an ingested paper.

    ``section_id`` must match an ``id`` from the ``sections`` list returned
    by ``upload_paper_*``. Returns title, type, full text, any extracted
    claims / definitions, and ``has_next`` / ``next_section_id`` hints so
    the caller can walk the paper without re-querying the section map.
    """
    _row, structure = _load_paper(paper_id)
    sec = _find_section(structure, section_id)
    if sec is None:
        raise ValueError(f"section_id {section_id!r} not found in paper {paper_id!r}")

    # Compute next-section hint so the host can iterate without looking it up
    ids = [str(s.number) for s in structure.sections]
    try:
        idx = ids.index(section_id)
    except ValueError:
        idx = -1
    next_id = ids[idx + 1] if 0 <= idx < len(ids) - 1 else None

    return {
        "paper_id": paper_id,
        "section_id": section_id,
        "number": sec.number,
        "title": sec.title,
        "type": sec.section_type.value,
        "text": sec.text,
        "claims": list(sec.claims),
        "definitions": list(sec.definitions),
        "math_content": bool(sec.math_content),
        "has_next": next_id is not None,
        "next_section_id": next_id,
    }


@mcp.tool()
def get_review_prompt(
    paper_id: str,
    stage: Literal["overview", "section", "crossref", "critique"],
    section_id: str | None = None,
    overview: dict | None = None,
    comments: list[dict] | None = None,
) -> dict:
    """Return ``{system, user, response_schema}`` for one review stage.

    The caller (host LLM) must execute the prompt itself against its own
    model and return a JSON response matching ``response_schema``. This
    server never makes review-reasoning LLM calls — it only hands back the
    prompt strings used by the coarse pipeline.

    Stage requirements:

    - ``overview``: no extra args.
    - ``section``: ``section_id`` required.
    - ``crossref`` / ``critique``: ``overview`` (``OverviewFeedback`` dict)
      and ``comments`` (list of ``DetailedComment`` dicts) required.
    """
    from coarse.prompts import get_prompt
    from coarse.types import DetailedComment, OverviewFeedback

    _row, structure = _load_paper(paper_id)

    def _rehydrate_overview(blob: dict | None):
        if blob is None:
            return None
        return OverviewFeedback.model_validate(blob)

    def _rehydrate_comments(blobs: list[dict] | None):
        if not blobs:
            return []
        return [DetailedComment.model_validate(b) for b in blobs]

    if stage == "overview":
        system, user = get_prompt(
            "overview",
            structure=structure,
            document_form=structure.document_form,
        )
        schema = _response_schema("OverviewFeedback")
    elif stage == "section":
        if not section_id:
            raise ValueError("stage='section' requires section_id")
        sec = _find_section(structure, section_id)
        if sec is None:
            raise ValueError(f"section_id {section_id!r} not found in paper {paper_id!r}")
        focus = _detect_focus(sec)
        system, user = get_prompt(
            "section",
            section=sec,
            all_sections=list(structure.sections),
            focus=focus,
            overview=_rehydrate_overview(overview),
            title=structure.title,
            abstract=structure.abstract,
            document_form=structure.document_form,
        )
        schema = _response_schema("SectionComments")
    elif stage in ("crossref", "critique"):
        ov = _rehydrate_overview(overview)
        cm = _rehydrate_comments(comments)
        if ov is None:
            raise ValueError(f"stage={stage!r} requires overview")
        if not cm:
            raise ValueError(f"stage={stage!r} requires comments")
        system, user = get_prompt(
            stage,
            overview=ov,
            comments=cm,
            title=structure.title,
            abstract=structure.abstract,
            document_form=structure.document_form,
        )
        schema = _response_schema("CommentList")
    else:
        raise ValueError(f"unknown stage {stage!r}")

    return {
        "paper_id": paper_id,
        "stage": stage,
        "system": system,
        "user": user,
        "response_schema": schema,
    }


_MIN_SECTION_CHARS = 200


def get_review_instructions(paper_id: str) -> dict:
    """Return a single compact prompt to produce a full paper review.

    This is the recommended tool for the 3-call pipeline:
    ``load_paper_state`` → ``get_review_instructions`` → ``finalize_review``.

    Returns ``{paper_id, system, user, response_schema}``. The ``user``
    field contains the paper title, abstract, a section map with focus
    tags, and the full text of each reviewable section (empty sections
    and references are excluded). The host LLM should respond with a
    single JSON object containing ``overview`` (OverviewFeedback) and
    ``comments`` (list of DetailedComment).

    Quote verification runs automatically inside ``finalize_review``,
    so the host does NOT need to call ``verify_quotes`` separately.
    """
    _row, structure = _load_paper(paper_id)

    sections_block = []
    for sec in structure.sections:
        text_len = len(sec.text.strip()) if sec.text else 0
        if text_len == 0:
            continue
        if sec.section_type == "references":
            continue
        focus = _detect_focus(sec)
        sections_block.append(
            f"### Section {sec.number}: {sec.title}\n"
            f"**Focus**: {focus}"
            f"{' — VERIFY PROOFS CAREFULLY' if focus == 'proof' else ''}\n"
            f"**Type**: {sec.section_type}\n\n"
            f"{sec.text}\n"
        )

    paper_body = "\n---\n\n".join(sections_block)

    system = (
        "You are a rigorous academic peer reviewer. Produce a structured "
        "review of the paper below. Your review must contain:\n\n"
        "1. **overview**: An OverviewFeedback object with fields: summary "
        "(1-2 sentences), assessment (1 paragraph), issues (4-6 titled "
        "macro issues, each with title + body), recommendation (one of: "
        "accept, revise_and_resubmit, reject), revision_targets (3-5 "
        "bullet points).\n\n"
        "2. **comments**: A flat list of DetailedComment objects, each with "
        "fields: number (integer), title (short), quote (a VERBATIM "
        "passage of 50-200 characters copied character-for-character from "
        "the paper text — must be a unique, specific passage that grounds "
        "the comment, NOT a section header or generic sentence. Do NOT "
        "clean up OCR artifacts or formatting. Each comment MUST have a "
        "DIFFERENT quote — no duplicates), feedback (constructive "
        "guidance), severity (critical/major/minor), confidence "
        "(high/medium/low).\n\n"
        "Aim for 10-25 comments across all sections. Cover methodology, "
        "results, proofs (verify step by step), and exposition. For math "
        "sections marked 'VERIFY PROOFS CAREFULLY', check each derivation "
        "for correctness.\n\n"
        "Respond with ONLY a JSON object matching the response_schema. "
        "No prose, no markdown, no commentary outside the JSON."
    )

    user = (
        f"# {structure.title}\n\n"
        f"**Domain**: {structure.domain}\n"
        f"**Taxonomy**: {structure.taxonomy}\n\n"
        f"## Abstract\n\n{structure.abstract}\n\n"
        f"## Sections\n\n{paper_body}"
    )

    schema = {
        "type": "object",
        "required": ["overview", "comments"],
        "properties": {
            "overview": _response_schema("OverviewFeedback"),
            "comments": {
                "type": "array",
                "items": _response_schema("SectionComments")["properties"]["comments"]["items"],
            },
        },
    }

    return {
        "paper_id": paper_id,
        "section_count": len(sections_block),
        "system": system,
        "user": user,
        "response_schema": schema,
    }


def get_all_section_prompts(
    paper_id: str,
    overview: dict,
) -> dict:
    """Return review prompts for all reviewable sections in one call.

    Automatically filters out empty sections (<200 chars) and reference
    lists. Keeps ALL substantive sections including appendix proofs —
    those get a specialized proof-verification prompt.

    Returns ``{paper_id, section_count, skipped, prompts: {section_id:
    {section_title, focus, system, user, response_schema}, ...}}``.
    The host LLM MUST execute EVERY returned prompt and collect all
    comments into a single flat list.
    """
    from coarse.prompts import get_prompt
    from coarse.types import OverviewFeedback

    _row, structure = _load_paper(paper_id)
    ov = OverviewFeedback.model_validate(overview)

    prompts = {}
    skipped = []
    for sec in structure.sections:
        sid = str(sec.number)
        text_len = len(sec.text.strip()) if sec.text else 0

        if text_len < _MIN_SECTION_CHARS:
            skipped.append(
                {"id": sid, "title": sec.title, "reason": "too short", "chars": text_len}
            )
            continue
        if sec.section_type == "references":
            skipped.append({"id": sid, "title": sec.title, "reason": "references"})
            continue

        focus = _detect_focus(sec)
        system, user = get_prompt(
            "section",
            section=sec,
            all_sections=list(structure.sections),
            focus=focus,
            overview=ov,
            title=structure.title,
            abstract=structure.abstract,
        )
        prompts[sid] = {
            "section_title": sec.title,
            "focus": focus,
            "system": system,
            "user": user,
            "response_schema": _response_schema("SectionComments"),
        }

    return {
        "paper_id": paper_id,
        "section_count": len(prompts),
        "skipped": skipped,
        "prompts": prompts,
    }


def _response_schema(name: str) -> dict:
    """Return a minimal JSON-schema stub so the host LLM emits the right shape.

    We don't ship the full Pydantic-generated schemas here — those are
    huge and the host LLM usually matches on the handful of keys that
    matter. The crossref/critique stages both return ``{comments: [...]}``
    envelopes; overview returns an ``OverviewFeedback`` shape; section
    returns a ``SectionComments`` envelope.
    """
    if name == "OverviewFeedback":
        return {
            "type": "object",
            "required": ["issues"],
            "properties": {
                "summary": {"type": "string"},
                "assessment": {"type": "string"},
                "issues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["title", "body"],
                        "properties": {
                            "title": {"type": "string"},
                            "body": {"type": "string"},
                        },
                    },
                },
                "recommendation": {"type": "string"},
                "revision_targets": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
        }
    # Both SectionComments and CommentList (crossref/critique) share the
    # envelope shape used by the existing agents.
    return {
        "type": "object",
        "required": ["comments"],
        "properties": {
            "comments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["number", "title", "quote", "feedback"],
                    "properties": {
                        "number": {"type": "integer"},
                        "title": {"type": "string"},
                        "quote": {
                            "type": "string",
                            "description": (
                                "Verbatim substring of the paper text "
                                "(50-200 chars, unique per comment)"
                            ),
                        },
                        "feedback": {"type": "string"},
                        "severity": {
                            "type": "string",
                            "enum": ["critical", "major", "minor"],
                        },
                        "confidence": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                        },
                    },
                },
            }
        },
    }


# --- Verification + finalization ---


@mcp.tool()
def verify_quotes(paper_id: str, comments: list[dict]) -> dict:
    """Fuzzy-match each comment's quote against the stored paper markdown.

    Drops comments whose quote can't be verified (no substring match within
    the coarse fuzzy-match threshold). Returns ``{verified: [...], dropped:
    [...]}`` where ``verified`` comments have their quote field corrected
    to the canonical passage from the paper and ``dropped`` entries carry
    the original index + title + fuzzy ratio so the caller can decide
    whether to retry with a different quote.
    """
    from coarse.quote_verify import _find_nearest_passage
    from coarse.quote_verify import verify_quotes as _vq
    from coarse.types import DetailedComment

    row, _structure = _load_paper(paper_id)
    paper_md = row.get("paper_markdown") or ""
    if not paper_md:
        raise ValueError(f"paper {paper_id!r} has no stored markdown")

    rehydrated: list[DetailedComment] = []
    for i, blob in enumerate(comments):
        try:
            rehydrated.append(DetailedComment.model_validate(blob))
        except Exception as exc:
            raise ValueError(f"comments[{i}] does not match DetailedComment schema: {exc}") from exc

    # Dedupe comments into the subset that survived quote verification, and
    # compute fuzzy diagnostics for the ones that were dropped.
    kept = _vq(rehydrated, paper_md, drop_unverified=True)
    kept_titles = {c.title for c in kept}
    dropped = []
    for c in rehydrated:
        if c.title in kept_titles:
            continue
        _passage, ratio = _find_nearest_passage(c.quote or "", paper_md)
        dropped.append(
            {
                "title": c.title,
                "original_quote": c.quote,
                "fuzzy_ratio": round(ratio, 3),
            }
        )

    return {
        "paper_id": paper_id,
        "verified": [c.model_dump() for c in kept],
        "dropped": dropped,
        "kept_count": len(kept),
        "dropped_count": len(dropped),
    }


@mcp.tool()
def finalize_review(
    paper_id: str,
    overview: dict,
    comments: list[dict],
    *,
    finalize_token: str | None = None,
    callback_url: str | None = None,
) -> dict:
    """Render a completed review to markdown and (optionally) persist it via callback.

    The MCP server renders the markdown locally using coarse's
    deterministic ``render_review`` synthesizer (same output format as
    the OpenRouter path). How it gets persisted depends on whether a
    capability callback was handed in:

    - **Callback mode** (``finalize_token`` + ``callback_url`` both set):
      POST the rendered review + metadata to ``callback_url`` with the
      token in the body. The callback validates the token and writes
      the review row on its side. This is the only path that persists
      to Supabase when the web→MCP round-trip is in use, and it keeps
      the MCP server free of Supabase credentials.
    - **In-memory mode** (both None): store the review in this process's
      in-memory dict so local dev + tests can inspect it without a
      callback. Nothing leaves the process. Used by the CLI test
      harness (`deploy/mcp_test_client.py`) and unit tests.

    The host LLM can pass ``finalize_token`` and ``callback_url`` that
    came in the clipboard handoff prompt from coarse.vercel.app. If one
    is supplied but not the other, that's a caller bug — raise to
    surface it rather than silently dropping to in-memory mode.

    Returns ``{review_id, review_url, markdown, comment_count}``. The
    ``review_url`` comes from the callback's response in callback mode,
    or is derived from the ``SITE_URL`` env var in in-memory mode.
    """
    import datetime

    from coarse.synthesis import render_review
    from coarse.types import DetailedComment, OverviewFeedback, Review

    row, _structure = _load_paper(paper_id)

    try:
        overview_obj = OverviewFeedback.model_validate(overview)
    except Exception as exc:
        raise ValueError(f"overview does not match OverviewFeedback: {exc}") from exc

    try:
        rehydrated_comments = [DetailedComment.model_validate(b) for b in (comments or [])]
    except Exception as exc:
        raise ValueError(f"comments do not match DetailedComment schema: {exc}") from exc

    # Auto-verify quotes before rendering. This eliminates the need for
    # a separate verify_quotes tool call in the pipeline.
    from coarse.quote_verify import verify_quotes as _vq

    paper_md = row.get("paper_markdown") or ""
    if paper_md:
        rehydrated_comments = _vq(rehydrated_comments, paper_md, drop_unverified=True)

    # Ensure sequential numbering so the output matches the web format.
    renumbered = [
        c.model_copy(update={"number": i}) for i, c in enumerate(rehydrated_comments, start=1)
    ]

    review = Review(
        title=row.get("title") or "Untitled",
        domain=row.get("domain") or "unknown",
        taxonomy=row.get("taxonomy") or "academic/research_paper",
        date=datetime.date.today().strftime("%m/%d/%Y"),
        overall_feedback=overview_obj,
        detailed_comments=renumbered,
    )
    markdown = render_review(review)

    # Partial-arg check: either both callback fields or neither.
    has_token = bool(finalize_token and finalize_token.strip())
    has_callback = bool(callback_url and callback_url.strip())
    if has_token != has_callback:
        raise ValueError(
            "finalize_review requires both finalize_token AND callback_url "
            "to be set for callback mode, or neither for in-memory mode. "
            f"Got finalize_token={bool(has_token)}, callback_url={bool(has_callback)}."
        )

    if has_token and has_callback:
        # --- Callback mode: POST to the Next.js /api/mcp-finalize endpoint. ---
        return _finalize_via_callback(
            paper_id=paper_id,
            row=row,
            markdown=markdown,
            comment_count=len(renumbered),
            finalize_token=finalize_token.strip(),  # type: ignore[union-attr]
            callback_url=callback_url.strip(),  # type: ignore[union-attr]
        )

    # --- In-memory mode: store in _STORE and derive URL from SITE_URL. ---
    review_id = paper_id
    site_url = os.environ.get("SITE_URL", "https://coarse.vercel.app").rstrip("/")
    review_url = f"{site_url}/review/{review_id}"

    _STORE.insert_review(
        review_id,
        {
            "paper_filename": row.get("title") or "Untitled",
            "paper_title": row.get("title"),
            "domain": row.get("domain"),
            "status": "done",
            "result_markdown": markdown,
            "paper_markdown": row.get("paper_markdown"),
            "model": "mcp-host",
            "completed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
    )

    return {
        "review_id": review_id,
        "review_url": review_url,
        "markdown": markdown,
        "comment_count": len(renumbered),
    }


def _finalize_via_callback(
    *,
    paper_id: str,
    row: dict,
    markdown: str,
    comment_count: int,
    finalize_token: str,
    callback_url: str,
) -> dict:
    """POST the rendered review to the Next.js /api/mcp-finalize endpoint.

    Used by ``finalize_review`` in callback mode to hand the review over
    to the Next.js backend for persistence. The backend validates the
    token, upserts the reviews row, and returns the ``review_url``.

    We intentionally do NOT retry on non-2xx or consume the token
    ourselves on failure: the Next.js side owns the token's lifecycle
    (consume-before-write), so a failed callback either (a) didn't
    reach the backend, in which case the token is still fresh and the
    host can retry, or (b) reached it after consumption, in which case
    retrying won't help and the user needs a new handoff. In both
    cases surfacing the HTTP error verbatim is the right behavior.
    """
    import requests

    payload = {
        "token": finalize_token,
        "paper_id": paper_id,
        "paper_title": row.get("title") or "",
        "domain": row.get("domain") or "",
        "taxonomy": row.get("taxonomy") or "",
        "markdown": markdown,
        "paper_markdown": row.get("paper_markdown") or "",
        "model": "mcp-host",
    }
    _validate_callback_url(callback_url)

    try:
        resp = requests.post(
            callback_url,
            json=payload,
            timeout=30,
            headers={"User-Agent": "coarse-mcp-server/1.0"},
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            f"finalize_review callback to {callback_url!r} failed at the "
            f"network layer: {exc}. The token is likely still valid — "
            f"ask the host to re-run finalize_review."
        ) from exc

    if not resp.ok:
        # Surface the backend's error message verbatim so the host can
        # make sense of token-expired / invalid-payload / etc.
        try:
            body = resp.json()
            msg = body.get("error") or str(body)
        except Exception:
            msg = resp.text[:500]
        raise RuntimeError(f"finalize_review callback returned HTTP {resp.status_code}: {msg}")

    data = resp.json()
    review_id = data.get("review_id") or paper_id
    review_url = data.get("review_url")
    if not review_url:
        raise RuntimeError(f"finalize_review callback response missing review_url: {data!r}")

    return {
        "review_id": review_id,
        "review_url": review_url,
        "markdown": markdown,
        "comment_count": comment_count,
    }


# ---------------------------------------------------------------------------
# Modal deployment (optional — skipped in local dev when modal isn't available)
# ---------------------------------------------------------------------------


try:
    import modal
    from fastapi import HTTPException, Request
    from pydantic import BaseModel as _BaseModel

    _repo_root = Path(__file__).resolve().parent.parent

    _modal_image = (
        modal.Image.debian_slim(python_version="3.12")
        .apt_install("libgl1", "libglib2.0-0")
        .pip_install(
            "litellm>=1.83.0",
            "instructor>=1.7",
            "pydantic>=2.0",
            "typer>=0.12",
            "rich>=13.0",
            "tomli-w>=1.0",
            "pymupdf>=1.24",
            # Fast PDF-to-markdown extractor used by the MCP handoff flow.
            # Pinned to >= 1.27 to align with pymupdf 1.27.x. Note that
            # 1.27 ships pymupdf_layout, which auto-activates a per-page
            # OCR pass at import time and balloons extraction to ~150s
            # for a 30-page paper. We disable it via
            # ``pymupdf4llm.use_layout(False)`` inside
            # ``extraction._extract_pymupdf4llm`` so we get the legacy
            # pymupdf_rag text path: pure-Python, no OCR, ~10s typical.
            "pymupdf4llm>=1.27",
            "python-dotenv>=1.0",
            "supabase>=2.0",
            "requests>=2.33.1",
            "fastmcp>=2.10",
            "fastapi[standard]",
            # Multi-format extraction fallbacks for DOCX / HTML / EPUB.
            # Note: docling is deliberately NOT installed in the coarse-mcp
            # image. It's ~600 MB of torch + transformers + RapidOCR and
            # its PDF cold-start was the 498-second hang that motivated
            # moving to pymupdf4llm in the first place. The OCR cascade
            # (pymupdf4llm → mistral → pdf-text) falls through to a hard
            # failure for scanned PDFs in this image, which is acceptable
            # because academic papers overwhelmingly have embedded text.
            # Production do_review (coarse-review app) keeps docling.
            "mammoth>=1.6",
            "markdownify>=0.12",
            "ebooklib>=0.18",
        )
        .add_local_dir(_repo_root / "src" / "coarse", remote_path="/root/coarse")
    )

    modal_app = modal.App("coarse-mcp")

    # ----- ASGI MCP server (zero ambient credentials) -----

    @modal_app.function(
        image=_modal_image,
        timeout=900,
        memory=1024,
        region=["us-east-1", "us-east-2", "us-west-2", "eu-west-1"],
        # HARD CAP at 1 container. FastMCP's streamable-HTTP transport
        # holds per-session state (the MCP session ID → request queue
        # mapping) in process memory, and our in-memory ``_STORE`` holds
        # the paper state keyed by paper_id. If Modal autoscales across
        # multiple containers, a follow-up tool call in the same host
        # session routes to a different container and gets a 404 on
        # "session not found" + a "paper_id not found" on the in-memory
        # store lookup. Pinning to max_containers=1 serializes all
        # concurrent reviews through one process — fine for a single
        # user demo and for low-volume production. Scaling beyond this
        # requires a Redis/Postgres-backed session store for FastMCP
        # AND moving ``_STORE`` to a shared persistence layer. See
        # ``deploy/DEPLOY_MCP.md`` for the scaling path.
        min_containers=1,
        max_containers=1,
        # No secrets: the MCP server itself holds zero ambient
        # credentials. Every capability (paper download, review
        # persistence) is supplied per-call by the user's clipboard
        # handoff prompt. See web/src/app/api/mcp-handoff/route.ts.
        # The extract worker below DOES attach secrets — it's a
        # separate Modal function in the same app with its own
        # narrower grant.
    )
    @modal.asgi_app()
    def asgi():
        """Expose the FastMCP server as a Modal ASGI app.

        The server instance (``mcp``) is created at module import time so
        Modal cold-starts don't re-register tools. ``http_app()`` returns a
        Starlette ASGI app with the streamable-HTTP transport FastMCP
        clients expect.
        """
        os.environ["COARSE_MCP_PUBLIC_HTTP"] = "1"
        inner = mcp.http_app(transport="http")

        async def _wrapper(scope, receive, send):
            if scope["type"] == "http":
                method = scope.get("method", "")
                path = scope.get("path", "")
                headers = dict(scope.get("headers", []))
                accept = headers.get(b"accept", b"").decode()

                # Route all MCP-like paths to /mcp. Claude.ai may:
                # - Send /mcp/ (trailing slash → 307 redirect, breaks)
                # - Send / if it strips the path from the URL
                # - Send /mcp/mcp if it appends /mcp to the given URL
                if path in ("/mcp/", "/", "/mcp/mcp", "/mcp/mcp/"):
                    scope = dict(scope, path="/mcp")

                # Claude.ai probes GET /mcp during connector setup without
                # Accept: text/event-stream. FastMCP rejects that with 406.
                # Return a clean 200 so the health check passes.
                if method == "GET" and path in ("/mcp", "/mcp/", "/", "/mcp/mcp", "/mcp/mcp/"):
                    if "text/event-stream" not in accept:
                        from starlette.responses import JSONResponse

                        resp = JSONResponse(
                            {
                                "status": "ok",
                                "server": "coarse-mcp",
                                "transport": "streamable-http",
                                "mcp_endpoint": "/mcp",
                            }
                        )
                        await resp(scope, receive, send)
                        return

                # CORS preflight — FastMCP doesn't handle OPTIONS.
                if method == "OPTIONS":
                    from starlette.responses import Response

                    resp = Response(
                        status_code=204,
                        headers={
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
                            "Access-Control-Allow-Headers": "*",
                            "Access-Control-Expose-Headers": "mcp-session-id",
                            "Access-Control-Max-Age": "86400",
                        },
                    )
                    await resp(scope, receive, send)
                    return

            await inner(scope, receive, send)

        return _wrapper

    # ----- Extract worker (OCR + structure → state blob) -----
    #
    # Runs the pre-handoff extraction for the web→MCP subscription flow.
    # Intentionally co-located with the MCP server Modal app (``coarse-mcp``)
    # rather than the OpenRouter ``coarse-review`` worker app so prod
    # deploys of either app can't interfere with the other. Attaches the
    # ``coarse-supabase`` + ``coarse-webhook`` Modal secrets narrowly to
    # just the two extract functions — the ASGI MCP server still gets
    # no ambient credentials.

    class ExtractRequest(_BaseModel):
        """Payload for the ``run_extract`` web endpoint.

        Intentionally excludes the user's OpenRouter key. The key is
        ferried through the same ``review_secrets`` side-table pattern
        as ``deploy/modal_worker.py``'s ``do_review`` — frontend
        (``/api/mcp-extract``) inserts a row under RLS deny-all, and
        ``do_extract`` reads + deletes it in one shot. The key never
        rides through Modal's managed queue.
        """

        job_id: str  # reviews.id minted by /api/presign
        pdf_storage_path: str

    def _mcp_fetch_and_consume_user_key(db, job_id: str) -> str | None:
        """One-shot read + delete of review_secrets[review_id=job_id].

        Duplicates ``modal_worker._fetch_and_consume_user_key`` because
        Modal images don't cross-import between apps. Kept minimal — if
        this ever drifts from modal_worker's copy, the two apps will
        still behave consistently as long as the table schema is stable.
        """
        try:
            result = (
                db.table("review_secrets")
                .select("user_api_key")
                .eq("review_id", job_id)
                .maybe_single()
                .execute()
            )
        except Exception as exc:
            print(f"[{job_id}] review_secrets SELECT failed: {exc}")
            return None
        if result is None or not getattr(result, "data", None):
            return None
        key = result.data.get("user_api_key") if isinstance(result.data, dict) else None
        if not key:
            return None
        try:
            db.table("review_secrets").delete().eq("review_id", job_id).execute()
        except Exception as exc:
            print(f"[{job_id}] review_secrets DELETE failed (non-fatal): {exc}")
        return key

    @modal_app.function(
        image=_modal_image,
        # 10-minute ceiling. Extraction is much smaller than a full
        # review — Mistral OCR typically finishes in 30-90s, and even
        # the worst 10-retry backoff (~160s) + Docling fallback fits
        # well under 10 min.
        timeout=600,
        memory=1024,
        max_containers=20,
        # Explicit retries=0: _mcp_fetch_and_consume_user_key consumes
        # the review_secrets row on first read, so a retry would find
        # an empty row and 401 on the first LLM call. Mirrors the
        # do_review retry policy.
        retries=0,
        secrets=[
            modal.Secret.from_name("coarse-supabase"),
            modal.Secret.from_name("coarse-webhook"),
        ],
    )
    def do_extract(req_dict: dict):
        """Extract-only worker used by the web→MCP handoff flow.

        Downloads a PDF from the ``papers`` bucket (via Supabase service
        key from the ``coarse-supabase`` secret), runs coarse's
        ``extract_and_structure`` cascade (Mistral OCR → pdf-text →
        Docling), and writes the result as JSON to
        ``papers/<uuid>.mcp.json``. Also flips ``reviews.status`` to
        ``'extracted'`` so the browser's realtime subscription knows
        the handoff is ready to mint.

        The state blob shape matches what ``load_paper_state`` expects:

            {
              "title": str,
              "domain": str,
              "taxonomy": str,
              "abstract": str,
              "paper_markdown": str,
              "structure_json": PaperStructure.model_dump(),
            }

        The OpenRouter key is read from the ``review_secrets`` side
        table once (and immediately deleted), then scoped to this
        function's env for the duration of the extraction. It never
        rides through Modal's spawn() queue payload.

        The PDF is *not* deleted on success because the same upload may
        be reused by ``coarse-review``'s ``do_review`` if the user
        falls back to the OpenRouter path. The 24h cleanup cron in
        ``.github/workflows/cleanup_papers.yml`` sweeps all stale PDFs.
        """
        import json as _json
        import os
        import tempfile
        import time

        from supabase import create_client

        req = ExtractRequest(**req_dict)
        job_id = req.job_id
        pdf_storage_path = req.pdf_storage_path

        print(
            f"[{job_id}] mcp-extract starting — pdf={pdf_storage_path}",
            flush=True,
        )

        supabase_url = os.environ["SUPABASE_URL"]
        supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
        db = create_client(supabase_url, supabase_key)

        db.table("reviews").update({"status": "extracting"}).eq("id", job_id).execute()

        cleaned_user_key = (_mcp_fetch_and_consume_user_key(db, job_id) or "").strip()
        if not cleaned_user_key:
            error_msg = (
                "No OpenRouter key staged in review_secrets — "
                "/api/mcp-extract must insert the key before calling Modal."
            )
            db.table("reviews").update({"status": "failed", "error_message": error_msg}).eq(
                "id", job_id
            ).execute()
            raise ValueError(error_msg)

        original_key = (os.environ.get("OPENROUTER_API_KEY") or "").strip() or None
        os.environ["OPENROUTER_API_KEY"] = cleaned_user_key

        # Cut Mistral OCR retry count from the default 9 → 2 on the MCP
        # handoff path. Users are staring at a live spinner; we'd rather
        # fall through to the next extractor in the cascade in ~5s than
        # burn 160s+ on Mistral's exponential backoff on flaky-upstream
        # days. Read at call time by ``extraction._get_ocr_max_retries()``.
        # Restored in the ``finally`` block so a container reuse for a
        # later invocation sees a clean env. Prod do_review leaves the
        # var unset and keeps the 9-retry generosity.
        original_ocr_retries = os.environ.get("COARSE_OCR_MAX_RETRIES")
        os.environ["COARSE_OCR_MAX_RETRIES"] = "2"

        # Flip the extractor cascade to try pymupdf4llm FIRST. For the
        # ~95% of academic PDFs with embedded text (they come out of
        # LaTeX/Word pipelines), this means extraction takes 1-2s with
        # no network and no model downloads. Only scanned / image-only
        # PDFs fall through to the OCR cascade, where the retry-cap=2
        # setting above keeps each cascade step fast. Production
        # do_review leaves this var unset and keeps the Mistral-first
        # OCR priority. Read at call time by ``extraction.extract_text()``.
        original_extraction_fast = os.environ.get("COARSE_EXTRACTION_FAST")
        os.environ["COARSE_EXTRACTION_FAST"] = "1"

        pdf_bytes = db.storage.from_("papers").download(pdf_storage_path)
        if not pdf_bytes:
            raise ValueError(f"Storage download returned empty for {pdf_storage_path}")
        print(f"[{job_id}] downloaded {len(pdf_bytes)} bytes", flush=True)

        ext = Path(pdf_storage_path).suffix or ".pdf"
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
            f.write(pdf_bytes)
            pdf_path = f.name

        start = time.time()
        try:
            print(f"[{job_id}] importing coarse modules", flush=True)
            from coarse import extract_and_structure
            from coarse.config import CoarseConfig
            from coarse.llm import LLMClient

            config = CoarseConfig(extraction_qa=False)
            client = LLMClient(config=config)
            print(f"[{job_id}] running extract_and_structure", flush=True)
            paper_text, structure = extract_and_structure(
                pdf_path, client, config=config, run_qa=False
            )
            duration = int(time.time() - start)
            print(
                f"[{job_id}] extract complete in {duration}s — "
                f"{len(paper_text.full_markdown)} chars, "
                f"{len(structure.sections)} sections",
                flush=True,
            )

            state_blob = {
                "title": structure.title,
                "domain": structure.domain,
                "taxonomy": structure.taxonomy,
                "abstract": structure.abstract,
                "paper_markdown": paper_text.full_markdown,
                "structure_json": _json.loads(structure.model_dump_json()),
            }
            state_bytes = _json.dumps(state_blob).encode("utf-8")
            state_path = f"{job_id}.mcp.json"

            db.storage.from_("papers").upload(
                path=state_path,
                file=state_bytes,
                file_options={
                    "content-type": "application/json",
                    "upsert": "true",
                },
            )
            print(f"[{job_id}] wrote state blob to papers/{state_path}")

            db.table("reviews").update(
                {
                    "status": "extracted",
                    "paper_title": structure.title,
                    "domain": structure.domain,
                    "paper_markdown": paper_text.full_markdown,
                    "duration_seconds": duration,
                }
            ).eq("id", job_id).execute()
            print(f"[{job_id}] status → extracted")

        except BaseException as e:
            duration = int(time.time() - start)
            if isinstance(e, SystemExit):
                error_msg = "Extraction timed out"
            else:
                error_msg = str(e)[:500]
            db.table("reviews").update(
                {
                    "status": "failed",
                    "error_message": error_msg,
                    "duration_seconds": duration,
                }
            ).eq("id", job_id).execute()
            raise
        finally:
            os.environ.pop("OPENROUTER_API_KEY", None)
            if original_key is not None:
                os.environ["OPENROUTER_API_KEY"] = original_key
            # Restore the OCR retry env var so a later invocation in
            # the same container reuses whatever the default was.
            os.environ.pop("COARSE_OCR_MAX_RETRIES", None)
            if original_ocr_retries is not None:
                os.environ["COARSE_OCR_MAX_RETRIES"] = original_ocr_retries
            # Restore the fast-extraction env var for the same reason.
            os.environ.pop("COARSE_EXTRACTION_FAST", None)
            if original_extraction_fast is not None:
                os.environ["COARSE_EXTRACTION_FAST"] = original_extraction_fast
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)

    @modal_app.function(
        image=_modal_image,
        timeout=60,
        secrets=[
            modal.Secret.from_name("coarse-webhook"),
        ],
    )
    @modal.fastapi_endpoint(method="POST")
    def run_extract(request: Request, req: ExtractRequest):
        """Accept an extract-only request and spawn the background worker.

        Returns 202 immediately — extraction runs asynchronously on
        ``do_extract``. The browser subscribes to ``reviews.status``
        via Supabase realtime to learn when the state blob is ready.
        """
        import hmac as _hmac
        import os

        expected = os.environ.get("MODAL_WEBHOOK_SECRET", "")
        token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
        if not expected or not token or not _hmac.compare_digest(token, expected):
            raise HTTPException(status_code=401, detail="Unauthorized")

        do_extract.spawn(req.model_dump())
        return {"status": "accepted", "job_id": req.job_id}

except ImportError:
    logger.info("modal not installed — Modal deployment hooks disabled (local-only MCP server)")


# ---------------------------------------------------------------------------
# Local development entrypoint
# ---------------------------------------------------------------------------


def _unwrap_tool_fn(tool_or_fn):
    """Return the underlying callable for either a FastMCP tool wrapper or plain function."""
    return getattr(tool_or_fn, "fn", tool_or_fn)


# Preserve plain-callable module exports for tests and local helpers while the
# FastMCP registry keeps the wrapped FunctionTool instances.
upload_paper_url_tool = upload_paper_url
upload_paper_url = _unwrap_tool_fn(upload_paper_url_tool)
upload_paper_bytes_tool = upload_paper_bytes
upload_paper_bytes = _unwrap_tool_fn(upload_paper_bytes_tool)
upload_paper_path_tool = upload_paper_path
upload_paper_path = _unwrap_tool_fn(upload_paper_path_tool)
load_paper_state_tool = load_paper_state
load_paper_state = _unwrap_tool_fn(load_paper_state_tool)
get_paper_section_tool = get_paper_section
get_paper_section = _unwrap_tool_fn(get_paper_section_tool)
get_review_prompt_tool = get_review_prompt
get_review_prompt = _unwrap_tool_fn(get_review_prompt_tool)
verify_quotes_tool = verify_quotes
verify_quotes = _unwrap_tool_fn(verify_quotes_tool)
finalize_review_tool = finalize_review
finalize_review = _unwrap_tool_fn(finalize_review_tool)


async def _compat_list_tools():
    """Compatibility wrapper for older tests/callers expecting FastMCP.list_tools()."""
    return list((await mcp._tool_manager.get_tools()).values())


if not hasattr(mcp, "list_tools"):
    mcp.list_tools = _compat_list_tools  # type: ignore[attr-defined]


if __name__ == "__main__":
    # Run a local streamable-HTTP server for MCP Inspector / Claude Code
    # development. Bind to localhost only.
    import argparse

    parser = argparse.ArgumentParser(description="coarse MCP server (local)")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument(
        "--transport",
        default="http",
        choices=("http", "stdio", "sse"),
        help="'http' for remote-style streamable HTTP (recommended); "
        "'stdio' for Claude Code / Gemini CLI local; 'sse' legacy.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger.info(
        "starting coarse MCP server transport=%s host=%s port=%s",
        args.transport,
        args.host,
        args.port,
    )
    if args.transport == "stdio":
        os.environ["COARSE_MCP_PUBLIC_HTTP"] = "0"
        mcp.run(transport="stdio")
    elif args.transport == "sse":
        os.environ["COARSE_MCP_PUBLIC_HTTP"] = "0"
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        import uvicorn

        os.environ["COARSE_MCP_PUBLIC_HTTP"] = "0"
        inner = mcp.http_app(transport="http")

        async def app(scope, receive, send):
            if scope["type"] == "http":
                method = scope.get("method", "")
                path = scope.get("path", "")
                headers = dict(scope.get("headers", []))
                accept = headers.get(b"accept", b"").decode()

                if path in ("/mcp/", "/", "/mcp/mcp", "/mcp/mcp/"):
                    scope = dict(scope, path="/mcp")

                if method == "GET" and path in ("/mcp", "/mcp/", "/", "/mcp/mcp", "/mcp/mcp/"):
                    if "text/event-stream" not in accept:
                        from starlette.responses import JSONResponse

                        resp = JSONResponse(
                            {
                                "status": "ok",
                                "server": "coarse-mcp",
                                "transport": "streamable-http",
                                "mcp_endpoint": "/mcp",
                            }
                        )
                        await resp(scope, receive, send)
                        return

                if method == "OPTIONS":
                    from starlette.responses import Response

                    resp = Response(
                        status_code=204,
                        headers={
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
                            "Access-Control-Allow-Headers": "*",
                            "Access-Control-Expose-Headers": "mcp-session-id",
                            "Access-Control-Max-Age": "86400",
                        },
                    )
                    await resp(scope, receive, send)
                    return

            await inner(scope, receive, send)

        uvicorn.run(app, host=args.host, port=args.port)
