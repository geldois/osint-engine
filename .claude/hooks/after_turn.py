from __future__ import annotations

import sys
from pathlib import Path

from _docs_nudge import docs_nudge_text
from _hook_io import (
    context,
    git_root,
    read_event,
    session_id,
    stop_reinvoked,
    take_marker,
)


def main() -> int:
    event = read_event()
    if stop_reinvoked(event):
        return 0

    root = git_root(Path.cwd())
    if root is None:
        return 0

    architecture_dir = root / "docs" / "architecture"
    if not architecture_dir.is_dir():
        return 0

    if not take_marker("docs-nudge-pending", session_id(event)):
        return 0

    areas = sorted(path.stem for path in architecture_dir.glob("*.md"))
    context("Stop", docs_nudge_text(areas))

    return 0


if __name__ == "__main__":
    sys.exit(main())
