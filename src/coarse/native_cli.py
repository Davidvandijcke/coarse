"""Coordinator tools for the opt-in native-app review pilot."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from coarse.cli_review import _scrub_url
from coarse.handoff_url import handoff_url_argument
from coarse.native_install import install_skill
from coarse.native_review import advance, confirm_extraction, prepare, publish, status, submit


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="coarse-native", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    install = commands.add_parser("install-skill")
    install.add_argument("--host", choices=["codex", "claude"], required=True)
    install.add_argument("--force", action="store_true")
    prep = commands.add_parser("prepare", help="Prepare a paper and emit native-agent tasks")
    source = prep.add_mutually_exclusive_group(required=True)
    source.add_argument("--paper", type=Path)
    source.add_argument("--handoff", type=handoff_url_argument)
    prep.add_argument("--host", choices=["codex", "claude"], required=True)
    prep.add_argument("--model", default="inherit")
    prep.add_argument(
        "--effort",
        choices=["inherit", "low", "medium", "high", "xhigh", "max", "ultra"],
        default="inherit",
    )
    prep.add_argument("--language")
    prep.add_argument("--author-notes")
    prep.add_argument("--pre-extracted", type=Path)
    for name in ["next", "status", "submit", "publish", "confirm-extraction"]:
        command = commands.add_parser(name)
        command.add_argument("--workspace", type=Path, required=True)
        if name == "confirm-extraction":
            command.add_argument("--agent-id", required=True)
            command.add_argument("--notes", required=True)
        if name == "submit":
            command.add_argument("--task", required=True)
            command.add_argument("--response", type=Path, required=True)
            command.add_argument("--agent-id", required=True)
            command.add_argument("--model")
            command.add_argument("--effort")
    prep.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "install-skill":
        try:
            print(json.dumps(install_skill(args.host, force=args.force), indent=2))
            return 0
        except Exception as exc:
            print("ERROR: " + str(exc), file=sys.stderr)
            return 2
    workspace = args.workspace.expanduser().resolve()
    try:
        if args.command == "prepare":
            result = prepare(
                workspace,
                paper=args.paper,
                handoff=args.handoff,
                host=args.host,
                model=args.model,
                effort=args.effort,
                pre_extracted=args.pre_extracted,
                language=args.language,
                author_notes=args.author_notes,
            )
        elif args.command == "next":
            result = advance(workspace)
        elif args.command == "status":
            result = status(workspace)
        elif args.command == "confirm-extraction":
            result = confirm_extraction(workspace, agent_id=args.agent_id, notes=args.notes)
        elif args.command == "publish":
            result = publish(workspace)
        else:
            if args.response.stat().st_size > 4_000_000:
                raise ValueError("Response exceeds the 4 MB pilot limit")
            response = json.loads(args.response.read_text(encoding="utf-8"))
            result = submit(
                workspace,
                args.task,
                response,
                agent_id=args.agent_id,
                reported_model=args.model,
                reported_effort=args.effort,
            )
    except Exception as exc:
        print("ERROR: " + _scrub_url(str(exc)), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
