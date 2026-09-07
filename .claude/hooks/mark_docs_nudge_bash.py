from __future__ import annotations

import sys
from pathlib import Path

from _docs_nudge import (
    changed_paths,
    is_relevant_change,
    parse_mtimes,
    path_mtimes,
    porcelain_paths,
)
from _hook_io import git_root, marker_value, read_event, run, session_id, set_marker


def main() -> int:
    event = read_event()
    if event.get("tool_name") != "Bash":
        return 0

    root = git_root(Path.cwd())
    if root is None:
        return 0

    status = run(["git", "status", "--porcelain", "-z", "--untracked-files=all"], root)
    if status is None or status.returncode != 0:
        return 0

    session = session_id(event)
    raw_previous = marker_value("bash-pre-state", session)
    if raw_previous is None:
        return 0

    previous = parse_mtimes(raw_previous)
    paths = set(porcelain_paths(status.stdout)) | previous.keys()
    current = path_mtimes(root, sorted(paths))

    if any(is_relevant_change(path) for path in changed_paths(current, previous)):
        set_marker("docs-nudge-pending", session)

    return 0


if __name__ == "__main__":
    sys.exit(main())
