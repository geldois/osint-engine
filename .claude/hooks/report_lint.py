from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import cast

from _hook_io import add_context, git_root, read_event, run, tool_input

_RUFF = ("uv", "run", "--no-sync", "ruff")
_MAX_REPORTED = 20


def main() -> int:
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

    violations = _irreducible(path, root)
    if violations is None:
        return 0
    if violations:
        add_context("\n".join(["── ruff (not auto-fixable) ──", *violations]))
    else:
        label = path if not path.is_relative_to(root) else path.relative_to(root)
        add_context(f"linting: ok ({label})")

    return 0


def _irreducible(path: Path, root: Path) -> list[str] | None:
    result = run(
        [*_RUFF, "check", "--output-format=json", "--force-exclude", str(path)], root
    )
    if result is None:
        return None
    try:
        raw: object = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    if not isinstance(raw, list):
        return None

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
