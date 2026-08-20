"""Comment-introduction nudge — ``PostToolUse(Edit|Write|MultiEdit)``.

Read-only: reports, never strips — see ``_comment_scan.py``'s header for why
the prior auto-stripping pipeline was removed. Flags a newly-introduced,
non-pragma comment or docstring inside a path CLAUDE.md forbids one from, so
the assistant removes it or renames instead of leaving it to a fixer that no
longer runs.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _comment_scan import new_comment_lines_python, new_comment_lines_sql
from _hook_io import add_context, git_root, read_event, run, tool_input

_ENFORCED_ROOTS = ("src/", "tests/", "scripts/", "migrations/")
_HUNK_HEADER = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def main() -> int:
    """Report the edited file's newly-introduced comment lines, if any."""
    file = tool_input(read_event(), "file_path")
    if not file:
        return 0

    target = _resolve_target(file)
    if target is None:
        return 0
    path, root, rel = target

    lines = _changed_lines(rel, root)
    if lines is not None and not lines:
        return 0

    source = path.read_text(encoding="utf-8")
    hits = (
        new_comment_lines_python(source, lines)
        if rel.endswith(".py")
        else new_comment_lines_sql(source, lines)
    )
    if hits:
        add_context(
            f"New comment on {rel} (no comments in enforced paths — CLAUDE.md). "
            f"Lines: {', '.join(str(n) for n in hits)}. Remove it, or make the "
            "name say what it says."
        )

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

    if not rel.startswith(_ENFORCED_ROOTS) or not rel.endswith((".py", ".sql")):
        return None

    return path, root, rel


def _changed_lines(rel: str, root: Path) -> frozenset[int] | None:
    """``None`` means every line counts (an untracked/new file has no HEAD
    version for ``git diff`` to compare against). Empty means a tracked file
    with no actual diff, so nothing to scan."""
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
