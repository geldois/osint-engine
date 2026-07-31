"""Per-turn reset for the graph-before-Explore gate (ADR 0025).

Runs on ``Stop`` (end of the assistant's turn) rather than
``UserPromptSubmit``, so a mid-turn user interjection doesn't wipe the
"already used the graph" marker before the task is done — only a completed turn
clears it.
"""

from __future__ import annotations

import sys

from _hook_io import field, marker_dir, read_event


def main() -> int:
    """Remove this session's graph-used marker at the end of the turn."""
    event = read_event()
    session = field(event, "session_id")
    if session:
        (marker_dir() / f"graph-used-{session}").unlink(missing_ok=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
