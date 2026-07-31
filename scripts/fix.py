"""Safe, idempotent auto-fixers, and the pre-commit orchestration (ADR 0025).

``fix`` runs every safe formatter/auto-fixer over the working tree (or explicit
paths): ruff format, ruff's safe lint fixes, and dprint's markdown reflow. All
three are idempotent and only apply changes a tool can make deterministically,
so running ``fix`` twice is a no-op the second time.

``precommit`` is what the pre-commit hook runs: it auto-fixes only the files that
are *fully* staged (no unstaged changes), re-stages those fixes, then runs the
full gate against the materialised snapshot. A partially-staged file is never
touched — fixing it would drag its unstaged half into the commit — so no commit
can ever be left in a partial or corrupted state by this path.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from scripts.gates import run_check

_UV_RUN = ("uv", "run", "--no-sync")
_FIX_EXTENSIONS = (".py", ".md")


def run_fix(paths: tuple[str, ...] = ()) -> int:
    """Apply every safe, idempotent fixer to ``paths`` (or the whole tree)."""
    targets = list(paths) if paths else ["."]
    py_targets = [p for p in targets if p == "." or p.endswith(".py")]

    if py_targets:
        subprocess.run([*_UV_RUN, "ruff", "format", *py_targets], check=False)
        subprocess.run([*_UV_RUN, "ruff", "check", "--fix", *py_targets], check=False)

    # dprint with no explicit path formats its own configured includes; with
    # paths it formats exactly those. Either way its scope is dprint.json.
    md_targets = [p for p in paths if p.endswith(".md")]
    if paths and not md_targets:
        return 0
    subprocess.run(["mise", "exec", "--", "dprint", "fmt", *md_targets], check=False)

    return 0


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
