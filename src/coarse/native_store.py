"""Private, atomic checkpoints for the opt-in native review pilot."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from contextlib import contextmanager
from importlib.metadata import version
from pathlib import Path

FORMAT_VERSION = 1


def digest(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def engine_digest() -> str:
    root = Path(__file__).parent
    # Refuse to replay old checkpoints against changed prompts, schemas or code.
    paths = sorted(
        p
        for p in root.rglob("*")
        if p.suffix in {".py", ".json", ".j2", ".jinja2", ".yaml", ".toml"}
    )
    files = {p.relative_to(root).as_posix(): file_digest(p) for p in paths}
    return digest({"files": files, "pydantic": version("pydantic")})


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, value) -> None:
    atomic_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def atomic_text(path: Path, text: str) -> None:
    if path.is_symlink():
        raise ValueError("Checkpoint files must not be symlinks")
    fd, tmp = tempfile.mkstemp(prefix=".native-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        Path(tmp).unlink(missing_ok=True)


@contextmanager
def workspace_lock(workspace: Path):
    """OS lock releases even if a coordinator process crashes."""
    path = workspace / ".lock"
    if path.is_symlink():
        raise ValueError("Workspace lock must not be a symlink")
    with open(path, "a+b") as stream:
        os.chmod(path, 0o600)
        if os.name == "nt":
            import msvcrt

            stream.write(b"\0")
            stream.flush()
            stream.seek(0)
            try:
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise ValueError("Another coordinator is updating this workspace") from exc
        else:
            import fcntl

            try:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise ValueError("Another coordinator is updating this workspace") from exc
        try:
            yield
        finally:
            if os.name == "nt":
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


def load_run(workspace: Path) -> dict:
    for name in ["run.json", "paper.md", "tasks", "results"]:
        if (workspace / name).is_symlink():
            raise ValueError(f"Workspace {name} must not be a symlink")
    run = read_json(workspace / "run.json")
    if run["format_version"] != FORMAT_VERSION or run["engine_digest"] != engine_digest():
        raise ValueError(
            "This run requires the original Coarse code version; start a new workspace"
        )
    if file_digest(workspace / "paper.md") != run["paper_digest"]:
        raise ValueError("Prepared paper changed; start a new workspace")
    source = workspace / run["source_file"]
    if source.is_symlink() or file_digest(source) != run["source_digest"]:
        raise ValueError("Original source changed; start a new workspace")
    return run
