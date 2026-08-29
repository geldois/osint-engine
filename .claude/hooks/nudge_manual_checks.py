from __future__ import annotations

import re
import sys

from _hook_io import context, read_event, tool_input

_STATEMENT_SPLIT = re.compile(r"&&|[;\n]|\|+|[()]")

_HEREDOC = re.compile(r"<<-?(['\"]?)(\w+)\1\n.*?\n\s*\2(?=\s|$)", re.DOTALL)


def _strip_heredocs(command: str) -> str:
    return _HEREDOC.sub(lambda m: f"<<{m.group(2)}", command)


_LEADING = re.compile(r"^(?:uv|uvx|run|python3?|npx|mise|exec|--?\S+)\s+")
_TOOL = re.compile(
    r"^(?:pytest|ruff check|ruff format|basedpyright"
    r"|cosmic-ray|cr-rate|lint-imports|sqruff|dprint|shellcheck|shfmt)\b",
)
_FACADE_PREFIX_LEN = 2
_FACADE_SUBCOMMANDS = frozenset({"check", "fix", "precommit"})

_REASON = (
    "Never run a linter, formatter, type-checker, or test by hand — not on "
    "one file, not on the whole repo. `pre-commit` and `pre-merge-commit` "
    "both run `scripts precommit` (fix, then check) on the whole repo, "
    "automatically, on every commit and merge attempt. Edit what needs "
    "editing and try to commit; iterate on the gate's own failure output if "
    "it blocks. `scripts mutation`, `scripts sqlc-generate`, and `scripts "
    "fixtures` stay periodic and manual — unaffected."
)


def _is_facade_run(normalized: str) -> bool:
    tokens = normalized.split()
    return (
        len(tokens) >= _FACADE_PREFIX_LEN
        and tokens[0] == "scripts"
        and tokens[1] in _FACADE_SUBCOMMANDS
    )


def main() -> int:
    command = tool_input(read_event(), "command")
    if not command:
        return 0

    for statement in _STATEMENT_SPLIT.split(_strip_heredocs(command)):
        normalized = statement.strip()
        while match := _LEADING.match(normalized):
            normalized = normalized[match.end() :]

        if _is_facade_run(normalized) or _TOOL.match(normalized):
            context("PreToolUse", _REASON)
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
