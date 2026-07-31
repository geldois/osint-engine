"""Block destructive code-review-graph config writes — ``PreToolUse(Bash)``.

The harness (`.claude/`, `.mcp.json`, `CLAUDE.md`, the git hooks) is committed and
hand-tuned. ``code-review-graph install|init|uninstall`` regenerate/overwrite all
of it (backing the old up to ``*.bak`` and littering per-tool configs), which
would clobber this setup. Only data commands (``build``, ``update``, ``serve``,
``status``, ``watch``, ``embed``, ``postprocess``) are allowed — they never touch
configs. The crg subcommand is always the first argument, so the match is exact.
"""

from __future__ import annotations

import re
import sys

from _hook_io import deny, read_event, tool_input

_DESTRUCTIVE = re.compile(r"\bcode-review-graph\s+(?:install|init|uninstall)\b")

_REASON = (
    "Blocked: `code-review-graph install|init|uninstall` regenerate and "
    "overwrite the committed harness (.claude/, .mcp.json, CLAUDE.md, the git "
    "pre-commit hook) and litter per-tool configs — they are first-time-setup "
    "only, never re-run. The harness is already committed. Use only data "
    "commands: `code-review-graph build` (first build), `update` (incremental), "
    "`serve` (the MCP server .mcp.json runs), `status`. If a config was already "
    "clobbered, restore it with `git restore` — everything crg overwrites is "
    "version-controlled."
)


def main() -> int:
    """Deny a config-regenerating code-review-graph subcommand."""
    command = tool_input(read_event(), "command")
    if command and _DESTRUCTIVE.search(command):
        deny(_REASON)
    return 0


if __name__ == "__main__":
    sys.exit(main())
