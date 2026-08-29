from __future__ import annotations

import sys
from pathlib import Path

from _hook_io import context, git_root, read_event, run

_SRC_AREAS = frozenset(
    {"domain", "application", "infrastructure", "interface", "config", "observability"},
)
_ROOT_AREAS = frozenset({"scripts", "tests", "migrations"})
_SRC_AREA_DEPTH = 3
_PATH_START = 3

_DOCS_NUDGE = (
    "Area(s) touched: {areas}. Judge, don't act reflexively: was the change "
    "semantic (business/flow logic) or purely mechanical (rename, typing, "
    "refactor)? If semantic, update the matching docs/architecture/<area>.md in "
    "natural language — never cite a function, class, or type name — and check "
    "whether the Mermaid architecture diagram in README.md still represents the "
    "truth. If mechanical, skip."
)


def main() -> int:
    event = read_event()
    if event.get("stop_hook_active") is True:
        return 0

    root = git_root(Path.cwd())
    if root is None:
        return 0

    changed = _changed_files(root)
    if not changed:
        return 0

    nudge = _docs_nudge(changed)
    if nudge:
        context("Stop", nudge)

    return 0


def _changed_files(root: Path) -> list[str]:
    result = run(["git", "status", "--porcelain", "--untracked-files=all"], root)
    if result is None or result.returncode != 0:
        return []

    paths: list[str] = []
    for line in result.stdout.splitlines():
        if len(line) <= _PATH_START or line[0] == "D" or line[1] == "D":
            continue
        path = line[_PATH_START:].split(" -> ")[-1].strip('"')
        if (root / path).is_file():
            paths.append(path)
    return paths


def _docs_nudge(changed: list[str]) -> str:
    areas = sorted({area for path in changed if (area := _area_for(path))})
    return _DOCS_NUDGE.format(areas=", ".join(areas)) if areas else ""


def _area_for(path: str) -> str | None:
    parts = Path(path).parts
    if (
        len(parts) >= _SRC_AREA_DEPTH
        and parts[0] == "src"
        and parts[1] == "osint_engine"
    ):
        return parts[2] if parts[2] in _SRC_AREAS else None
    return parts[0] if parts and parts[0] in _ROOT_AREAS else None


if __name__ == "__main__":
    sys.exit(main())
