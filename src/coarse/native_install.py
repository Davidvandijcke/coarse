"""Install the native pilot alongside existing headless review skills."""

from pathlib import Path

from coarse.native_store import atomic_text


def install_skill(host: str, *, force: bool = False, home: Path | None = None) -> dict:
    roots = {"codex": ".codex/skills", "claude": ".claude/skills"}
    if host not in roots:
        raise ValueError("Unsupported native host")
    destination = (home or Path.home()) / roots[host] / "coarse-native-review"
    if destination.is_symlink():
        raise ValueError("Native skill destination must not be a symlink")
    source = Path(__file__).parent / "_skills/native_review/SKILL.md"
    content = source.read_text(encoding="utf-8")
    target = destination / "SKILL.md"
    if target.exists() and target.read_text(encoding="utf-8") != content and not force:
        raise ValueError("Native skill differs; use --force to replace it deliberately")
    destination.mkdir(parents=True, exist_ok=True)
    atomic_text(target, content)
    return {"skill_file": str(target), "host": host, "pilot": True}
