"""Per-edit lint report — ``PostToolUse(Edit|Write|MultiEdit)``.

Read-only by design. A hook that rewrites the edited file leaves the model's
in-context copy silently wrong and forces a full re-read on the next edit, so
this one only *reports*, and every fixer runs once at ``pre-commit`` instead.

Reports only the irreducible: violations ruff cannot fix itself (``fix`` is
null in its JSON output). Everything auto-fixable, and every formatting
concern, is resolved silently by the pre-commit ``fix`` step and never costs a
token here. Silent when there is nothing irreducible to say.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import cast

from _hook_io import add_context, git_root, read_event, run, tool_input

_RUFF = ("uv", "run", "--no-sync", "ruff")
_MAX_REPORTED = 20


def main() -> int:
    """Report the edited Python file's non-auto-fixable ruff violations."""
    file = tool_input(read_event(), "file_path")
    if not file:
        return 0

    path = Path(file)
    if not path.is_absolute():
        path = Path.cwd() / path
    if path.suffix != ".py" or not path.is_file():
        return 0

    root = git_root(path)
    if root is None:
        return 0

    lines = _irreducible(path, root)
    if lines:
        add_context("\n".join(["── ruff (not auto-fixable) ──", *lines]))

    return 0


def _irreducible(path: Path, root: Path) -> list[str]:
    result = run(
        [*_RUFF, "check", "--output-format=json", "--force-exclude", str(path)], root
    )
    if result is None:
        return []
    try:
        raw: object = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    if not isinstance(raw, list):
        return []

    reported: list[str] = []
    for entry in cast("list[object]", raw):
        if not isinstance(entry, dict):
            continue
        violation = cast("dict[str, object]", entry)
        if violation.get("fix") is not None:
            continue
        reported.append(_format(violation))
        if len(reported) == _MAX_REPORTED:
            break
    return reported


def _format(violation: dict[str, object]) -> str:
    location = violation.get("location")
    row = ""
    if isinstance(location, dict):
        row = str(cast("dict[str, object]", location).get("row", ""))
    code = violation.get("code")
    message = violation.get("message")
    return f"  {row}: {code if isinstance(code, str) else '?'} {message}"


if __name__ == "__main__":
    sys.exit(main())
