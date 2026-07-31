"""Mark the code-review-graph MCP as used this turn (ADR 0025).

Paired with ``reset_graph_gate.py`` (clears on Stop) and
``require_graph_before_explore.py`` (reads the marker). ``PostToolUse``, matcher
``mcp__code-review-graph.*``.
"""

from __future__ import annotations

import sys

from _hook_io import field, marker_dir, read_event

_PREFIX = "mcp__code-review-graph__"


def main() -> int:
    """Touch the per-session marker after a code-review-graph MCP call."""
    event = read_event()
    session = field(event, "session_id")
    if not session:
        return 0

    if field(event, "tool_name").startswith(_PREFIX):
        directory = marker_dir()
        directory.mkdir(parents=True, exist_ok=True)
        (directory / f"graph-used-{session}").touch()

    return 0


if __name__ == "__main__":
    sys.exit(main())
