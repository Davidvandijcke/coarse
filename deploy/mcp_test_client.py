"""End-to-end test client for the coarse MCP server.

Simulates a host LLM (Claude.ai, ChatGPT, Gemini CLI, etc.) driving the
full review pipeline against a running ``deploy/mcp_server.py`` instance.
Useful both as an integration test and as reference code for anyone who
wants to drive coarse from a custom MCP host without the coarse source
tree — the same tool-call sequence ported to any language works.

Usage::

    # 1. Start the MCP server in one terminal
    uv run python deploy/mcp_server.py --transport http --port 8765

    # 2. Run the harness in another terminal
    export OPENROUTER_API_KEY=sk-or-v1-...
    uv run python deploy/mcp_test_client.py \\
        https://arxiv.org/pdf/2301.00001.pdf

    # Optional flags:
    #   --server   URL of the running MCP server (default: local)
    #   --model    LiteLLM model for review reasoning (default: config default)
    #   --output   Write final markdown to a file
    #   --sections N  Limit to first N sections (for quick smoke tests)

Cost: $1-3 on OpenRouter for a typical 20-page paper. The extraction call
is charged through the same key; review reasoning is the bulk of the spend.
In real deployments the review reasoning happens on the host's own
subscription instead, but this harness uses one key for both so it can
run CI-style without any special setup.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

from pydantic import BaseModel, Field

# Put src/ on sys.path so we can reuse coarse's own Pydantic types and
# LLMClient. A production host that doesn't have coarse checked out would
# instead parse JSON according to the ``response_schema`` field that
# ``get_review_prompt`` returns.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from coarse.llm import LLMClient  # noqa: E402
from coarse.types import (  # noqa: E402
    DetailedComment,
    OverviewFeedback,
)

logger = logging.getLogger("mcp_test_client")


# ---------------------------------------------------------------------------
# Response envelopes — mirror the ones in src/coarse/agents/
# ---------------------------------------------------------------------------


class _SectionComments(BaseModel):
    comments: list[DetailedComment] = Field(min_length=1)


class _ConsolidatedComments(BaseModel):
    comments: list[DetailedComment]


# ---------------------------------------------------------------------------
# MCP client helpers
# ---------------------------------------------------------------------------


async def _call(client, name: str, args: dict) -> dict:
    """Call an MCP tool through a fastmcp Client and unwrap the result dict.

    fastmcp 3.x returns a ``CallToolResult`` whose ``.data`` field holds the
    tool's return value after structured-content parsing. When the server
    emits only a text content block (tool errors, etc.) we fall back to
    parsing ``.content[0].text`` as JSON so the caller still sees a dict.
    """
    result = await client.call_tool(name, args)
    data = getattr(result, "data", None)
    if data is not None:
        return data
    content = getattr(result, "content", None) or []
    if content:
        first = content[0]
        text = getattr(first, "text", None)
        if text is not None:
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                raise RuntimeError(f"tool {name!r} returned non-JSON text: {text[:200]}")
    raise RuntimeError(f"tool {name!r} returned unexpected shape: {result!r}")


def _execute_prompt(
    llm: LLMClient,
    stage: str,
    system: str,
    user: str,
    response_model: type[BaseModel],
    *,
    max_tokens: int,
    temperature: float = 0.3,
) -> BaseModel:
    """Run a coarse stage prompt through a real LLM via instructor.

    This is the piece a host LLM does implicitly: when Claude.ai drives the
    coarse MCP server, *Claude's own model* executes the returned prompts
    against its own conversational context. For a local end-to-end test we
    drive litellm ourselves and parse via instructor, which is exactly
    what the section/crossref/critique agents do in ``src/coarse/agents/``.
    """
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    logger.info("stage=%s executing prompt (%d chars user)", stage, len(user))
    return llm.complete(
        messages,
        response_model=response_model,
        max_tokens=max_tokens,
        temperature=temperature,
    )


# ---------------------------------------------------------------------------
# The review loop
# ---------------------------------------------------------------------------


async def run_review(
    *,
    paper_url: str | None,
    paper_path: Path | None,
    server_url: str,
    model: str | None,
    openrouter_key: str,
    output: Path | None,
    section_limit: int | None,
) -> int:
    """Drive the full MCP review pipeline and print the final markdown.

    Returns 0 on success, non-zero on fatal errors.
    """
    from fastmcp import Client

    llm = LLMClient(model=model) if model else LLMClient()
    resolved_model = llm.model
    print(f"host-simulation model: {resolved_model}")
    print(f"MCP server URL:        {server_url}")

    async with Client(server_url) as client:
        # --- 1. Upload ---
        if paper_path is not None:
            print(f"[1/7] uploading {paper_path} via upload_paper_path")
            upload = await _call(
                client,
                "upload_paper_path",
                {"path": str(paper_path), "openrouter_key": openrouter_key},
            )
        else:
            assert paper_url is not None
            print(f"[1/7] uploading {paper_url} via upload_paper_url")
            upload = await _call(
                client,
                "upload_paper_url",
                {"url": paper_url, "openrouter_key": openrouter_key},
            )

        paper_id = upload["paper_id"]
        title = upload.get("title") or "Untitled"
        sections = upload.get("sections") or []
        print(f"       paper_id={paper_id}")
        print(f"       title={title!r}")
        print(f"       {len(sections)} sections")
        if section_limit is not None:
            sections = sections[:section_limit]
            print(f"       (limited to first {len(sections)} for this run)")

        # --- 2. Overview ---
        print("[2/7] running overview stage")
        overview_prompt = await _call(
            client,
            "get_review_prompt",
            {"paper_id": paper_id, "stage": "overview"},
        )
        overview = _execute_prompt(
            llm,
            "overview",
            overview_prompt["system"],
            overview_prompt["user"],
            OverviewFeedback,
            max_tokens=8192,
            temperature=0.5,
        )
        assert isinstance(overview, OverviewFeedback)
        print(f"       {len(overview.issues)} overview issues")

        # --- 3. Per-section comments ---
        print(f"[3/7] running section agent on {len(sections)} sections")
        all_comments: list[DetailedComment] = []
        for sec in sections:
            sec_id = sec["id"]
            sec_title = sec.get("title", "?")
            try:
                sec_prompt = await _call(
                    client,
                    "get_review_prompt",
                    {
                        "paper_id": paper_id,
                        "stage": "section",
                        "section_id": sec_id,
                        "overview": overview.model_dump(),
                    },
                )
                result = _execute_prompt(
                    llm,
                    "section",
                    sec_prompt["system"],
                    sec_prompt["user"],
                    _SectionComments,
                    max_tokens=16384,
                )
                assert isinstance(result, _SectionComments)
                all_comments.extend(result.comments)
                print(
                    f"       section {sec_id} ({sec_title[:40]}): {len(result.comments)} comments"
                )
            except Exception as exc:
                print(f"       section {sec_id} skipped: {exc}")

        if not all_comments:
            print("ERROR: no section comments produced — aborting", file=sys.stderr)
            return 1
        print(f"       total {len(all_comments)} draft comments")

        # --- 4. Crossref dedup ---
        print("[4/7] running crossref stage (dedup)")
        cr_prompt = await _call(
            client,
            "get_review_prompt",
            {
                "paper_id": paper_id,
                "stage": "crossref",
                "overview": overview.model_dump(),
                "comments": [c.model_dump() for c in all_comments],
            },
        )
        try:
            crossrefed = _execute_prompt(
                llm,
                "crossref",
                cr_prompt["system"],
                cr_prompt["user"],
                _ConsolidatedComments,
                max_tokens=32768,
                temperature=0.1,
            )
            assert isinstance(crossrefed, _ConsolidatedComments)
            crossref_comments = crossrefed.comments
        except Exception as exc:
            print(f"       crossref failed, using raw comments: {exc}")
            crossref_comments = all_comments
        print(f"       {len(crossref_comments)} after dedup")

        # --- 5. Quote verification (server-side, deterministic) ---
        print("[5/7] verifying quotes")
        verified = await _call(
            client,
            "verify_quotes",
            {
                "paper_id": paper_id,
                "comments": [c.model_dump() for c in crossref_comments],
            },
        )
        kept_dicts = verified["verified"]
        print(f"       kept {verified['kept_count']} / dropped {verified['dropped_count']}")

        # --- 6. Critique polish (optional but included for completeness) ---
        print("[6/7] running critique stage")
        try:
            cq_prompt = await _call(
                client,
                "get_review_prompt",
                {
                    "paper_id": paper_id,
                    "stage": "critique",
                    "overview": overview.model_dump(),
                    "comments": kept_dicts,
                },
            )
            critiqued = _execute_prompt(
                llm,
                "critique",
                cq_prompt["system"],
                cq_prompt["user"],
                _ConsolidatedComments,
                max_tokens=16384,
                temperature=0.1,
            )
            final_comments = [c.model_dump() for c in critiqued.comments]
            print(f"       {len(final_comments)} after critique")
        except Exception as exc:
            print(f"       critique failed, using verified comments: {exc}")
            final_comments = kept_dicts

        # --- 7. Finalize ---
        print("[7/7] finalizing review")
        final = await _call(
            client,
            "finalize_review",
            {
                "paper_id": paper_id,
                "overview": overview.model_dump(),
                "comments": final_comments,
            },
        )
        print(f"       review_id={final['review_id']}")
        print(f"       review_url={final['review_url']}")
        print(f"       comment_count={final['comment_count']}")
        print(f"       host-simulation cost: ${llm.cost_usd:.4f}")

        markdown = final.get("markdown") or ""
        if output is not None:
            output.write_text(markdown, encoding="utf-8")
            print(f"       markdown written to {output}")
        else:
            print("\n--- review markdown ---\n")
            print(markdown)

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="coarse MCP end-to-end test client / reference host",
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument(
        "paper",
        nargs="?",
        help="Paper URL (http/https) or absolute local path",
    )
    src.add_argument(
        "--url",
        help="Paper URL (explicit form; overrides positional)",
    )
    src.add_argument(
        "--path",
        type=Path,
        help="Absolute local path to a paper file",
    )
    parser.add_argument(
        "--server",
        default="http://127.0.0.1:8765/mcp",
        help="MCP server URL (default: %(default)s)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="LiteLLM model string for host-simulation reasoning "
        "(default: coarse config default, usually OpenRouter-routed)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write the final review markdown to this path",
    )
    parser.add_argument(
        "--sections",
        type=int,
        default=None,
        metavar="N",
        help="Only review the first N sections (faster smoke test)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable INFO logs")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )

    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        print(
            "ERROR: set OPENROUTER_API_KEY in the environment",
            file=sys.stderr,
        )
        return 1

    # Resolve paper source: --url wins, then --path, then positional.
    paper_url: str | None = None
    paper_path: Path | None = None
    if args.url:
        paper_url = args.url
    elif args.path:
        paper_path = args.path.expanduser().resolve()
    elif args.paper:
        if args.paper.startswith(("http://", "https://")):
            paper_url = args.paper
        else:
            paper_path = Path(args.paper).expanduser().resolve()
    if paper_url is None and paper_path is None:
        print("ERROR: provide a paper URL or path", file=sys.stderr)
        return 1

    return asyncio.run(
        run_review(
            paper_url=paper_url,
            paper_path=paper_path,
            server_url=args.server,
            model=args.model,
            openrouter_key=key,
            output=args.output,
            section_limit=args.sections,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
