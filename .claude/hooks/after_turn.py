"""End-of-turn type check and docs nudge — ``Stop``.

One process, one injection, read-only. Runs at the end of the turn rather than
per edit for two reasons: the code is finally complete (mid-refactor a
type-checker reports cascading errors from code not yet written, and the model
chases them), and one run costs a fraction of one run per edit.

Both signals derive from ``git status --porcelain`` — no marker files, no
temp-directory sweep, and accurate even across a session restart.
"""

from __future__ import annotations

import sys
from pathlib import Path

from _hook_io import context, git_root, read_event, run

_BASEDPYRIGHT = ("uv", "run", "--no-sync", "basedpyright", "--level", "error")
_MAX_FILES = 40
_MAX_OUTPUT_LINES = 40

_TYPED_ROOTS = ("src", "tests", "scripts", ".claude/hooks")
_SRC_AREAS = frozenset(
    {"domain", "application", "infrastructure", "interface", "config", "observability"},
)
_ROOT_AREAS = frozenset({"scripts", "tests", "migrations"})
_SRC_AREA_DEPTH = 3  # src/osint_engine/<area>/...
_PATH_START = 3  # porcelain line is "XY <path>"

_DOCS_NUDGE = (
    "Area(s) touched: {areas}. Judge, don't act reflexively: was the change "
    "semantic (business/flow logic) or purely mechanical (rename, typing, "
    "refactor)? If semantic, update the matching docs/architecture/<area>.md in "
    "natural language — never cite a function, class, or type name — and check "
    "whether the Mermaid architecture diagram in README.md still represents the "
    "truth. If mechanical, skip."
)


def main() -> int:
    """Report end-of-turn type errors and nudge the architecture docs, once."""
    event = read_event()
    # Claude Code sets this when the turn was itself resumed by a Stop hook.
    # Without the guard, an unfixable type error would loop forever.
    if event.get("stop_hook_active") is True:
        return 0

    root = git_root(Path.cwd())
    if root is None:
        return 0

    changed = _changed_files(root)
    if not changed:
        return 0

    sections = [
        section
        for section in (_type_errors(changed, root), _docs_nudge(changed))
        if section
    ]
    if sections:
        context("Stop", "\n\n".join(sections))

    return 0


def _changed_files(root: Path) -> list[str]:
    """Paths changed vs HEAD, staged, unstaged or untracked; repo-relative."""
    result = run(["git", "status", "--porcelain", "--untracked-files=all"], root)
    if result is None or result.returncode != 0:
        return []

    paths: list[str] = []
    for line in result.stdout.splitlines():
        if len(line) <= _PATH_START or line[0] == "D" or line[1] == "D":
            continue
        # A rename entry is "R  old -> new"; only the destination exists.
        path = line[_PATH_START:].split(" -> ")[-1].strip('"')
        if (root / path).is_file():
            paths.append(path)
    return paths


def _type_errors(changed: list[str], root: Path) -> str:
    targets = [
        path
        for path in changed
        if path.endswith(".py") and path.startswith(_TYPED_ROOTS)
    ]
    if not targets or len(targets) > _MAX_FILES:
        return ""

    result = run([*_BASEDPYRIGHT, *targets], root)
    if result is None or result.returncode == 0:
        return ""

    lines = (result.stdout or result.stderr).splitlines()[:_MAX_OUTPUT_LINES]
    return "── basedpyright ──\n" + "\n".join(lines)


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
