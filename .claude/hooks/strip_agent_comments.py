"""Strip agent-authored comments/docstrings in repo-scope code — ``PostToolUse``.

Runs right after ``autofix_edited_file.py`` and before ``update_graph.py`` in
the ``Edit|Write|MultiEdit`` chain: after autofix so it strips the
already-formatted file (never fighting ruff's own reflow), and before the
graph update so the graph is built from the file's final, post-strip state
rather than going stale the moment this hook runs. Scoped to ``src/``,
``tests/``, ``scripts/``, ``migrations/`` — never ``.claude/`` or any
dotfolder, which are harness, not project content, and stay free for the
agent to comment/document normally.
"""

from __future__ import annotations

import re
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from _comment_stripper import strip_python, strip_sql
from _hook_io import git_root, read_event, tool_input

_Stripper = Callable[[str, "frozenset[int] | None"], str]

_SCOPED_ROOTS = ("src", "tests", "scripts", "migrations")
_HUNK_HEADER = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def main() -> int:
    """Strip the edited file in place when it's in-scope; silent otherwise."""
    file = tool_input(event=read_event(), key="file_path")
    if not file:
        return 0

    path = Path(file)
    if not path.is_absolute():
        path = Path.cwd() / path
    if not path.is_file():
        return 0

    root = git_root(path.parent)
    if root is None or not _in_scope(path, root):
        return 0

    changed_lines = _changed_lines(path, root)
    if changed_lines is not None and not changed_lines:
        return 0

    if path.suffix == ".py":
        _rewrite(path, strip_python, changed_lines)
    elif path.suffix == ".sql":
        _rewrite(path, strip_sql, changed_lines)

    return 0


def _in_scope(path: Path, root: Path) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return False
    return relative.parts[:1] in {(scoped,) for scoped in _SCOPED_ROOTS}


def _rewrite(
    path: Path, strip: _Stripper, changed_lines: frozenset[int] | None
) -> None:
    original = path.read_text(encoding="utf-8")
    stripped = strip(original, changed_lines)
    if stripped != original:
        path.write_text(stripped, encoding="utf-8")


def _changed_lines(path: Path, root: Path) -> frozenset[int] | None:
    """Line numbers added/modified vs HEAD; ``None`` if the file is untracked."""
    relative = path.relative_to(root)
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(relative)],
        cwd=root,
        capture_output=True,
        check=False,
    )
    if tracked.returncode != 0:
        return None

    diff = subprocess.run(
        [
            "git",
            "diff",
            "HEAD",
            "--no-color",
            "--no-ext-diff",
            "-U0",
            "--",
            str(relative),
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    lines: set[int] = set()
    for diff_line in diff.stdout.splitlines():
        match = _HUNK_HEADER.match(diff_line)
        if not match:
            continue
        start = int(match.group(1))
        count = int(match.group(2)) if match.group(2) is not None else 1
        if count > 0:
            lines.update(range(start, start + count))
    return frozenset(lines)


if __name__ == "__main__":
    sys.exit(main())
