"""Direct-run enforcement — ``PreToolUse(Bash)``.

A bare full-suite lint/type/test run bypasses the gate façade
(``uv run python -m scripts check [--full]``) that materialises the staged
snapshot, orders the gates, and writes the report. Block those and redirect;
still allow a targeted single-file or single-test run for fast local feedback.

Also blocks the agent from invoking the façade's own ``check --full`` directly
via Bash: ``pre-commit`` already runs ``check --staged --full`` on every
commit and reports failures inline, so pre-running it first is pure
duplication (manage-harness/SKILL.md, "born-full-green git hooks"). Plain
``check`` (fast) stays allowed for quick iteration.

Language-specific (this project's tools), so it lives local.
"""

from __future__ import annotations

import re
import sys

from _hook_io import deny, read_event, tool_input

# A Bash tool call is routinely a whole shell script (leading `cd`, chained
# `&&`/`;`/`|`, subshell parens), not one bare invocation — every check below
# must run per statement, never against the raw string's start, or a leading
# `cd project && uv run ...` (or a plain `cd project\n...`) walks straight
# past every anchor.
_STATEMENT_SPLIT = re.compile(r"&&|[;\n]|\|+|[()]")

# Strip every leading runner/flag token (uv run, uv run --no-sync, python -m,
# uvx, npx, mise exec --, stray -q/--flags) so wrapping the call cannot bypass
# the tool-name match below.
_LEADING = re.compile(r"^(?:uv|uvx|run|python3?|npx|mise|exec|--?\S+)\s+")
_TOOL = re.compile(
    r"^(?:pytest|ruff check|ruff format|basedpyright"
    r"|cosmic-ray|cr-rate|lint-imports|sqruff)\b",
)
_TARGETED_FILE = re.compile(r"\s\S+\.(?:py|sql)(?:\s|$)")
_FACADE_PREFIX_LEN = 2  # "scripts check"

_REASON = (
    "Full lint/type/test/mutation runs go through the gate facade, not raw "
    "tools: `uv run python -m scripts check` (fast) or `check --full`. It "
    "materialises the staged snapshot, orders every gate, fails on a missing "
    "tool, and writes build/reports/gates.json. Targeted single-file/single-test "
    "runs (e.g. pytest path/to/test.py::test_name, ruff check path/to/file.py) "
    "are not blocked. This applies regardless of runner prefix (uv run, uv run "
    "--no-sync, python -m, etc)."
)

_FULL_REASON = (
    "Don't pre-run `check --full` yourself — `pre-commit` already runs "
    "`check --staged --full` on a materialised snapshot for every commit and "
    "surfaces any failure inline. Just commit: if it fails, fix what's "
    "reported and commit again. Plain `check` (fast) and targeted single-"
    "file/single-test runs are still allowed."
)


def _is_full_facade_run(normalized: str) -> bool:
    tokens = normalized.split()
    return (
        len(tokens) >= _FACADE_PREFIX_LEN
        and tokens[0] == "scripts"
        and tokens[1] == "check"
        and "--full" in tokens[_FACADE_PREFIX_LEN:]
    )


def main() -> int:
    """Deny a bypassing full-suite run; allow targeted runs and non-matches."""
    command = tool_input(read_event(), "command")
    if not command:
        return 0

    for statement in _STATEMENT_SPLIT.split(command):
        normalized = statement.strip()
        while match := _LEADING.match(normalized):
            normalized = normalized[match.end() :]

        if _is_full_facade_run(normalized):
            deny(_FULL_REASON)
            return 0

        if not _TOOL.match(normalized):
            continue
        # A specific test node ("::") or a single source file is a targeted run.
        if "::" in normalized or _TARGETED_FILE.search(normalized):
            continue

        deny(_REASON)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
