from __future__ import annotations

import re
import sys
from pathlib import Path

from _comment_scan import (
    new_comment_lines_hash,
    new_comment_lines_python,
    new_comment_lines_sql,
)
from _hook_io import add_context, git_root, read_event, run, tool_input

_HASH_EXTENSIONS = (".sh", ".yml", ".yaml", ".toml")
_HASH_FILENAMES = frozenset(
    {
        "Dockerfile",
        "Caddyfile",
        ".gitconfig",
        ".gitignore",
        ".dockerignore",
        ".editorconfig",
        ".actrc",
    }
)
_HUNK_HEADER = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
_EXCLUDED_DIRS = frozenset(
    {".venv", ".cache", "build", ".hypothesis", ".import_linter_cache", "__pycache__"}
)
_MAX_REPORTED_LINES = 20


def main() -> int:
    event = read_event()
    file = tool_input(event, "file_path")
    if not file:
        return 0

    target = _resolve_target(file)
    if target is None:
        return 0
    path, root, rel = target

    if event.get("tool_name") == "Read":
        lines: frozenset[int] | None = None
        preexisting = True
    else:
        lines = _changed_lines(rel, root)
        if lines is not None and not lines:
            return 0
        preexisting = False

    source = path.read_text(encoding="utf-8")
    hits = _scan(rel, source, lines)
    if hits:
        _report(rel, hits, preexisting=preexisting)

    return 0


def _resolve_target(file: str) -> tuple[Path, Path, str] | None:
    path = Path(file)
    if not path.is_absolute():
        path = Path.cwd() / path
    if not path.is_file():
        return None

    root = git_root(path)
    if root is None:
        return None
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        return None

    if Path(rel).name not in _HASH_FILENAMES and not rel.endswith(
        (".py", ".sql", *_HASH_EXTENSIONS)
    ):
        return None

    if _EXCLUDED_DIRS & set(Path(rel).parts[:-1]):
        return None

    return path, root, rel


def _scan(rel: str, source: str, lines: frozenset[int] | None) -> list[int]:
    if rel.endswith(".py"):
        return new_comment_lines_python(source, lines)
    if rel.endswith(".sql"):
        return new_comment_lines_sql(source, lines)
    return new_comment_lines_hash(source, lines)


def _report(rel: str, hits: list[int], *, preexisting: bool) -> None:
    shown = hits[:_MAX_REPORTED_LINES]
    numbers = ", ".join(str(n) for n in shown)
    extra = len(hits) - len(shown)
    if extra:
        numbers += f" (+{extra} mais)"
    lead = "Pre-existing comment(s) in" if preexisting else "New comment on"
    add_context(
        f"{lead} {rel} (this repo allows none, anywhere, except a linter-ignore "
        f"pragma — CLAUDE.md). Lines: {numbers}. Remove it, make the name say "
        "what it says, or move the decision into README/TO-DO/docs/architecture/"
        "CLAUDE/CONTEXT."
    )


def _changed_lines(rel: str, root: Path) -> frozenset[int] | None:
    status = run(["git", "status", "--porcelain", "--", rel], root)
    if status is not None and status.stdout.startswith("??"):
        return None

    diff = run(
        ["git", "diff", "HEAD", "--no-color", "--no-ext-diff", "-U0", "--", rel],
        root,
    )
    if diff is None or diff.returncode != 0:
        return frozenset()

    lines: set[int] = set()
    for line in diff.stdout.splitlines():
        match = _HUNK_HEADER.match(line)
        if not match:
            continue
        start = int(match.group(1))
        count = int(match.group(2)) if match.group(2) is not None else 1
        lines.update(range(start, start + count))
    return frozenset(lines)


if __name__ == "__main__":
    sys.exit(main())
