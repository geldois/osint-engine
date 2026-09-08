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
    take_marker_value,
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

    raw = take_marker_value("docs-nudge-pending", session_id(event))
    if raw is None:
        return 0

    all_areas = sorted(path.stem for path in architecture_dir.glob("*.md"))
    touched_dirs = {
        part for rel in raw.split("\0") if rel for part in Path(rel).parts[:-1]
    }
    areas = sorted(area for area in all_areas if area in touched_dirs) or all_areas

    context("Stop", docs_nudge_text(areas))

    return 0


if __name__ == "__main__":
    sys.exit(main())
