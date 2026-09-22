from __future__ import annotations

import sys

from _docs_nudge import SIBLING_REPO_NAME, docs_nudge_text
from _hook_io import (
    context,
    project_root,
    read_event,
    session_id,
    stop_reinvoked,
    take_marker,
)


def main() -> int:
    event = read_event()
    if stop_reinvoked(event):
        return 0

    root = project_root()
    if root is None:
        return 0

    architecture_dir = root / "docs" / "architecture"
    if not architecture_dir.is_dir():
        return 0

    if not take_marker("docs-nudge-pending", session_id(event)):
        return 0

    sibling_dir = root.parent / SIBLING_REPO_NAME
    sibling_path = str(sibling_dir) if sibling_dir.is_dir() else None

    context("Stop", docs_nudge_text(sibling_path))

    return 0


if __name__ == "__main__":
    sys.exit(main())
