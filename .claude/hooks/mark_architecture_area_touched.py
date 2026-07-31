"""Mark a docs/architecture/ macro area as touched this message — ``PostToolUse``.

Paired with ``nudge_architecture_docs.py`` (``Stop``), which consumes these
markers to nudge a docs/architecture/<area>.md judgement once per assistant
message, naming every area touched. One marker file per (session, area) —
not a single boolean — so multiple areas touched in the same message all
surface in the one nudge. Stale markers (>30 min) are swept on each run so an
old edit never nudges a later, unrelated message.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from _hook_io import field, git_root, marker_dir, read_event, tool_input

_STALE_SECONDS = 30 * 60
_MARKER_PREFIX = "architecture-touched"

_SRC_AREAS = frozenset(
    {"domain", "application", "infrastructure", "interface", "config", "observability"},
)
_ROOT_AREAS = frozenset({"scripts", "tests", "migrations"})
_SRC_AREA_DEPTH = 3  # src/osint_engine/<area>/...


def main() -> int:
    """Touch the per-session, per-area marker when the edited file maps to one."""
    directory = marker_dir()
    directory.mkdir(parents=True, exist_ok=True)
    _sweep_stale(directory)

    event = read_event()
    session = field(event, "session_id")
    file = tool_input(event, "file_path")
    area = _area_for(file)
    if session and area:
        (directory / f"{_MARKER_PREFIX}-{session}-{area}").touch()
    return 0


def _area_for(file: str) -> str | None:
    if not file:
        return None
    path = Path(file)
    if not path.is_absolute():
        path = Path.cwd() / path
    root = git_root(path)
    if root is None:
        return None
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return None

    if (
        len(parts) >= _SRC_AREA_DEPTH
        and parts[0] == "src"
        and parts[1] == "osint_engine"
    ):
        candidate = parts[2]
        return candidate if candidate in _SRC_AREAS else None
    if parts and parts[0] in _ROOT_AREAS:
        return parts[0]
    return None


def _sweep_stale(directory: Path) -> None:
    cutoff = time.time() - _STALE_SECONDS
    for marker in directory.glob(f"{_MARKER_PREFIX}-*"):
        try:
            if marker.stat().st_mtime < cutoff:
                marker.unlink(missing_ok=True)
        except OSError:
            continue


if __name__ == "__main__":
    sys.exit(main())
