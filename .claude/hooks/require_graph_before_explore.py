"""Graph-before-Explore gate (ADR 0025) — ``PreToolUse(Grep|Glob|Agent)``.

Deny ``Grep``/``Glob``/``Explore`` until the code-review-graph MCP has been
consulted at least once this turn (marker set by ``mark_graph_used.py``, cleared
on Stop by ``reset_graph_gate.py``) — but only when this repo actually has a
graph. Local to this project: the graph is a local concern.
"""

from __future__ import annotations

import sys
from pathlib import Path

from _hook_io import deny, field, marker_dir, read_event, tool_input

_ANCESTOR_LEVELS = 3

_REASON = (
    "This repo has a .code-review-graph/graph.db. Per this repo CLAUDE.md (Code "
    "Review Graph): consult the code-review-graph MCP tools "
    "(mcp__code-review-graph__*: query_graph_tool, semantic_search_nodes_tool, "
    "get_impact_radius_tool, get_architecture_overview_tool, detect_changes_tool, "
    "etc.) at least once this turn before Grep/Glob/Explore. If the graph is "
    "stale or inconsistent, update/fix it — do not fall back. Fall back to "
    "Grep/Glob/Explore only for what is genuinely outside the graph scope "
    "(non-code files, logs, config text). Once you have used the graph, this "
    "unblocks for the rest of the turn."
)


def main() -> int:
    """Deny the search tool when a graph exists and has not been used this turn."""
    event = read_event()
    tool_name = field(event, "tool_name")

    if tool_name == "Agent":
        if tool_input(event, "subagent_type") != "Explore":
            return 0
    elif tool_name not in {"Grep", "Glob"}:
        return 0

    session = field(event, "session_id")
    if session and (marker_dir() / f"graph-used-{session}").exists():
        return 0

    cwd = field(event, "cwd")
    if not cwd:
        return 0

    directory = Path(cwd)
    for _ in range(_ANCESTOR_LEVELS):
        if (directory / ".code-review-graph" / "graph.db").is_file():
            deny(_REASON)
            return 0
        directory = directory.parent

    return 0


if __name__ == "__main__":
    sys.exit(main())
