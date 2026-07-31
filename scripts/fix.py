"""Safe, idempotent auto-fixers, and the pre-commit orchestration (ADR 0025).

``fix`` runs every safe formatter/auto-fixer over the working tree (or explicit
paths), routed by extension: ruff (format + safe lint fixes) for ``.py``, dprint
for json/toml/yaml/markdown, sqruff for ``.sql``. All are idempotent and only
apply changes a tool can make deterministically, so running ``fix`` twice is a
no-op the second time.

``precommit`` is what the pre-commit hook runs: it auto-fixes only the files that
are *fully* staged (no unstaged changes), re-stages those fixes, then runs the
full gate against the materialised snapshot. A partially-staged file is never
touched — fixing it would drag its unstaged half into the commit — so no commit
can ever be left in a partial or corrupted state by this path. The set of fixed
extensions mirrors the per-edit autofix hook exactly, so nothing a safe fixer
could resolve silently is left to fail the gate.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from scripts.gates import run_check

if TYPE_CHECKING:
    from collections.abc import Callable

_UV_RUN = ("uv", "run", "--no-sync")
# dprint owns json/toml/yaml/markdown; sqruff owns sql; ruff owns python. The
# pre-commit auto-fixer must cover exactly what the per-edit autofix hook covers,
# or a fully-staged file of a type it misses fails the gate on something a safe
# fixer could have silently resolved.
_DPRINT_EXTENSIONS = (".md", ".json", ".jsonc", ".toml", ".yaml", ".yml")
_FIX_EXTENSIONS = (".py", ".sql", *_DPRINT_EXTENSIONS)
_SQL_DIRS = ("migrations", "src")


def run_fix(paths: tuple[str, ...] = ()) -> int:
    """Apply every safe, idempotent fixer to ``paths`` (or the whole tree)."""
    if not paths:
        # Whole-tree: each fixer over its own configured scope.
        subprocess.run([*_UV_RUN, "ruff", "format", "."], check=False)
        subprocess.run([*_UV_RUN, "ruff", "check", "--fix", "."], check=False)
        subprocess.run(["mise", "exec", "--", "dprint", "fmt"], check=False)
        subprocess.run(["mise", "exec", "--", "sqruff", "fix", *_SQL_DIRS], check=False)
        return 0

    _fix_group([p for p in paths if p.endswith(".py")], _ruff)
    _fix_group([p for p in paths if p.endswith(_DPRINT_EXTENSIONS)], _dprint)
    _fix_group([p for p in paths if p.endswith(".sql")], _sqruff)

    return 0


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
    """Fix fully-staged files, re-stage them, then run the full gate."""
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
