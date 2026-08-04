from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from scripts._comments import strip_python, strip_sql
from scripts.gates import run_check

if TYPE_CHECKING:
    from collections.abc import Callable

    _Stripper = Callable[[str, "frozenset[int] | None"], str]

_UV_RUN = ("uv", "run", "--no-sync")
_DPRINT_EXTENSIONS = (".md", ".json", ".jsonc", ".toml", ".yaml", ".yml")
_FIX_EXTENSIONS = (".py", ".sql", *_DPRINT_EXTENSIONS)
_SQL_DIRS = ("migrations", "src")

_STRIP_ROOTS = ("src/", "tests/", "scripts/", "migrations/")
_STRIPPERS: tuple[tuple[str, _Stripper], ...] = (
    (".py", strip_python),
    (".sql", strip_sql),
)
_HUNK_HEADER = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def run_fix(paths: tuple[str, ...] = ()) -> int:
    if not paths:
        subprocess.run([*_UV_RUN, "ruff", "format", "."], check=False)
        subprocess.run([*_UV_RUN, "ruff", "check", "--fix", "."], check=False)
        subprocess.run(["mise", "exec", "--", "dprint", "fmt"], check=False)
        subprocess.run(["mise", "exec", "--", "sqruff", "fix", *_SQL_DIRS], check=False)
        return 0

    strip_new_comments(paths)
    _fix_group([p for p in paths if p.endswith(".py")], _ruff)
    _fix_group([p for p in paths if p.endswith(_DPRINT_EXTENSIONS)], _dprint)
    _fix_group([p for p in paths if p.endswith(".sql")], _sqruff)

    return 0


def strip_new_comments(paths: tuple[str, ...]) -> None:
    for path in paths:
        strip = _stripper_for(path)
        if strip is None:
            continue

        changed = _changed_lines(path)
        if not changed:
            continue

        file = Path(path)
        original = file.read_text(encoding="utf-8")
        stripped = strip(original, changed)
        if stripped != original:
            file.write_text(stripped, encoding="utf-8")


def _stripper_for(path: str) -> _Stripper | None:
    if not path.startswith(_STRIP_ROOTS):
        return None
    for suffix, strip in _STRIPPERS:
        if path.endswith(suffix):
            return strip
    return None


def _changed_lines(path: str) -> frozenset[int]:
    result = subprocess.run(
        ["git", "diff", "HEAD", "--no-color", "--no-ext-diff", "-U0", "--", path],
        capture_output=True,
        text=True,
        check=False,
    )
    lines: set[int] = set()
    for diff_line in result.stdout.splitlines():
        match = _HUNK_HEADER.match(diff_line)
        if not match:
            continue
        start = int(match.group(1))
        count = int(match.group(2)) if match.group(2) is not None else 1
        if count > 0:
            lines.update(range(start, start + count))
    return frozenset(lines)


def _fix_group(targets: list[str], run: Callable[[list[str]], None]) -> None:
    if targets:
        run(targets)


def _ruff(targets: list[str]) -> None:
    subprocess.run([*_UV_RUN, "ruff", "format", *targets], check=False)
    subprocess.run([*_UV_RUN, "ruff", "check", "--fix", *targets], check=False)


def _dprint(targets: list[str]) -> None:
    subprocess.run(["mise", "exec", "--", "dprint", "fmt", *targets], check=False)


def _sqruff(targets: list[str]) -> None:
    subprocess.run(["mise", "exec", "--", "sqruff", "fix", *targets], check=False)


def run_precommit() -> int:
    fixable = _fully_staged_files()
    if fixable:
        run_fix(tuple(fixable))
        subprocess.run(["git", "add", "--", *fixable], check=True)

    return run_check(full=True, staged=True)


def _fully_staged_files() -> list[str]:
    staged = _git_lines("diff", "--cached", "--name-only", "--diff-filter=ACM")
    unstaged = set(_git_lines("diff", "--name-only"))

    return [
        path
        for path in staged
        if path.endswith(_FIX_EXTENSIONS)
        and path not in unstaged
        and Path(path).is_file()
    ]


def _git_lines(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
    )

    return [line for line in result.stdout.splitlines() if line]
