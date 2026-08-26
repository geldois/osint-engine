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
    r"|cosmic-ray|cr-rate|lint-imports|sqruff)\b",
)
_TARGETED_FILE = re.compile(r"\s\S+\.(?:py|sql)(?:\s|$)")
_FACADE_PREFIX_LEN = 2
_FACADE_SUBCOMMANDS = frozenset({"check", "precommit"})

_REASON = (
    "Don't self-verify — `pre-commit` already runs the full gate (`scripts "
    "precommit`) on every commit and reports any failure inline. Just "
    "commit: if it fails, fix what's reported and commit again. Targeted "
    "single-file/single-test runs (e.g. pytest path/to/test.py::test_name, "
    "ruff check path/to/file.py) are still fine for quick iteration while "
    "writing code. `scripts fix` and `scripts mutation` (periodic, never a "
    "hook) are unaffected. This applies regardless of runner prefix (uv "
    "run, uv run --no-sync, python -m, etc)."
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

        if _is_facade_run(normalized):
            context("PreToolUse", _REASON)
            return 0

        if not _TOOL.match(normalized):
            continue
        if "::" in normalized or _TARGETED_FILE.search(normalized):
            continue

        context("PreToolUse", _REASON)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
