"""Nudge a docs/architecture/ judgement once per message — ``Stop``.

Advisory only: consumes the per-session, per-area markers
``mark_architecture_area_touched.py`` sets, firing at most one nudge per
assistant message naming every area touched, no matter how many files were
edited. Deliberately does NOT read or write any docs/architecture/*.md
itself — a mechanical rename/refactor is ignored, and only a genuinely
semantic change (business/flow logic, not symbols) earns the update.
"""

from __future__ import annotations

import sys

from _hook_io import context, field, marker_dir, read_event

_MARKER_PREFIX = "architecture-touched"

_NUDGE = (
    "Area(s) touched this message: {areas}. Judge, don't act reflexively: was "
    "the change semantic (business/flow logic) or purely mechanical (rename, "
    "typing, refactor)? If semantic, read and update the matching "
    "docs/architecture/<area>.md in natural language — never cite a function, "
    "class, or type name. If mechanical, skip."
)


def main() -> int:
    """Fire the docs/architecture nudge once if any area was touched this message."""
    session = field(read_event(), "session_id")
    if not session:
        return 0

    directory = marker_dir()
    prefix = f"{_MARKER_PREFIX}-{session}-"
    markers = sorted(directory.glob(f"{prefix}*"))
    if not markers:
        return 0

    areas = sorted({marker.name.removeprefix(prefix) for marker in markers})
    for marker in markers:
        marker.unlink(missing_ok=True)

    context("Stop", _NUDGE.format(areas=", ".join(areas)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
