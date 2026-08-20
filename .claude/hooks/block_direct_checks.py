"""Direct-run enforcement — ``PreToolUse(Bash)``.

``pre-commit`` already runs the full gate (``scripts precommit``, itself
``scripts check --full`` after fixing and re-staging) on every commit and
reports any failure inline — every commit is born green by construction.
Running the gate facade yourself (``scripts check``, ``scripts check
--full``, ``scripts precommit``) or a bare full-suite lint/type/test tool is
pure duplication of a guarantee ``pre-commit`` already gives; block those and
redirect to just committing. A targeted single-file or single-test run stays
allowed, for fast local feedback while writing code — ``scripts fix`` and the
periodic ``scripts mutation`` gate are unaffected.

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

# A heredoc body (a commit message passed via `<<'EOF' ... EOF`, the
# prescribed way to commit) is literal data, never a shell statement — but
# splitting on bare `(`/`)` above has no notion of that, so a conventional
# commit's own `(scope):` collides with a targetable name once split (e.g.
# `fix(pytest): ...` yields the bare statement `pytest`). Strip every
# heredoc down to its opening redirect before splitting, so its body and
# closing marker are never seen as statements at all.
_HEREDOC = re.compile(r"<<-?(['\"]?)(\w+)\1\n.*?\n\s*\2(?=\s|$)", re.DOTALL)


def _strip_heredocs(command: str) -> str:
    return _HEREDOC.sub(lambda m: f"<<{m.group(2)}", command)


# Strip every leading runner/flag token (uv run, uv run --no-sync, python -m,
# uvx, npx, mise exec --, stray -q/--flags) so wrapping the call cannot bypass
# the tool-name match below.
_LEADING = re.compile(r"^(?:uv|uvx|run|python3?|npx|mise|exec|--?\S+)\s+")
_TOOL = re.compile(
    r"^(?:pytest|ruff check|ruff format|basedpyright"
    r"|cosmic-ray|cr-rate|lint-imports|sqruff)\b",
)
_TARGETED_FILE = re.compile(r"\s\S+\.(?:py|sql)(?:\s|$)")
_FACADE_PREFIX_LEN = 2  # "scripts check" / "scripts precommit"
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
    """Deny a self-verifying full-gate or full-suite run; allow the rest."""
    command = tool_input(read_event(), "command")
    if not command:
        return 0

    for statement in _STATEMENT_SPLIT.split(_strip_heredocs(command)):
        normalized = statement.strip()
        while match := _LEADING.match(normalized):
            normalized = normalized[match.end() :]

        if _is_facade_run(normalized):
            deny(_REASON)
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
