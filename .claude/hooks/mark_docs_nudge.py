from __future__ import annotations

import sys
from pathlib import Path

from _docs_nudge import is_relevant_change
from _hook_io import (
    git_root,
    marker_value,
    read_event,
    session_id,
    set_marker,
    tool_input,
)


def main() -> int:
    event = read_event()
    file = tool_input(event, "file_path")
    if not file:
        return 0

    path = Path(file)
    if not path.is_absolute():
        path = Path.cwd() / path

    root = git_root(path)
    if root is None:
        return 0
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        return 0

    if not is_relevant_change(rel):
        return 0

    session = session_id(event)
    touched = set((marker_value("docs-nudge-pending", session) or "").split("\0"))
    touched.discard("")
    touched.add(rel)
    set_marker("docs-nudge-pending", session, "\0".join(sorted(touched)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
