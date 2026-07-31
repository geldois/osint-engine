"""Direct-run enforcement (ADR 0025) — ``PreToolUse(Bash)``.

A bare full-suite lint/type/test run bypasses the gate façade
(``uv run python -m scripts check [--full]``) that materialises the staged
snapshot, orders the gates, and writes the report. Block those and redirect;
still allow a targeted single-file or single-test run for fast local feedback.
Language-specific (this project's tools), so it lives local.
"""

from __future__ import annotations

import re
import sys

from _hook_io import deny, field, read_event, tool_input

# Strip every leading runner/flag token (uv run, uv run --no-sync, python -m,
# uvx, npx, mise exec --, stray -q/--flags) so wrapping the call cannot bypass
# the tool-name match below.
_LEADING = re.compile(r"^(?:uv|uvx|run|python3?|npx|mise|exec|--?\S+)\s+")
_TOOL = re.compile(
    r"^(?:pytest|ruff check|ruff format|basedpyright"
    r"|cosmic-ray|cr-rate|lint-imports|sqruff)\b",
)
_TARGETED_FILE = re.compile(r"\s\S+\.(?:py|sql)(?:\s|$)")

_REASON = (
    "Full lint/type/test/mutation runs go through the gate facade, not raw "
    "tools: `uv run python -m scripts check` (fast) or `check --full`. It "
    "materialises the staged snapshot, orders every gate, fails on a missing "
    "tool, and writes build/reports/gates.json. Targeted single-file/single-test "
    "runs (e.g. pytest path/to/test.py::test_name, ruff check path/to/file.py) "
    "are not blocked. This applies regardless of runner prefix (uv run, uv run "
    "--no-sync, python -m, etc)."
)


def main() -> int:
    """Deny a bypassing full-suite run; allow targeted runs and non-matches."""
    event = read_event()
    # The gate runner itself shells out to these tools inside its snapshot —
    # never block the runner's own children.
    if field(event, "agent_type") == "checks-triager":
        return 0

    command = tool_input(event, "command")
    if not command:
        return 0

    normalized = command
    while match := _LEADING.match(normalized):
        normalized = normalized[match.end() :]

    if not _TOOL.match(normalized):
        return 0
    # A specific test node ("::") or a single source file is a targeted run.
    if "::" in normalized or _TARGETED_FILE.search(normalized):
        return 0

    deny(_REASON)
    return 0


if __name__ == "__main__":
    sys.exit(main())
