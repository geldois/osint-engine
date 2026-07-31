"""Isolation primitives for maximum-integrity gate runs (ADR 0025, Option 2).

The staged snapshot is the exact tree ``git write-tree`` produces, extracted
into a throwaway directory and synced into its own ``.venv`` so the editable
install points at the *snapshot* source — import-linter, basedpyright and
pytest see precisely what would be committed, never the working tree. The real
repository, its untracked files, and its staged index are never modified: the
snapshot is read out of the object database, and verify-history replays commits
in a detached worktree. Both are disposable and cleaned up unconditionally.
"""

from __future__ import annotations

import io
import shutil
import subprocess
import tarfile
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator


def git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
    )

    return result.stdout.strip()


def sync(workdir: Path) -> None:
    """Build ``workdir/.venv`` from its own pyproject/lock, editable on its src."""
    subprocess.run(
        ["uv", "sync", "--quiet"],
        cwd=workdir,
        check=True,
    )


@contextmanager
def materialized_snapshot() -> Generator[Path]:
    """Extract the staged index into a disposable directory (no sync yet)."""
    tree = git_output("write-tree")
    archive = subprocess.run(
        ["git", "archive", "--format=tar", tree],
        check=True,
        capture_output=True,
    )

    tmp = Path(tempfile.mkdtemp(prefix="oe-gates-"))
    try:
        with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
            tar.extractall(tmp, filter="data")
        yield tmp
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@contextmanager
def detached_worktree(commit: str) -> Generator[Path]:
    """Add a detached worktree at ``commit``; remove it unconditionally."""
    tmp = Path(tempfile.mkdtemp(prefix="oe-history-"))
    worktree = tmp / "tree"
    subprocess.run(
        ["git", "worktree", "add", "--detach", str(worktree), commit],
        check=True,
        capture_output=True,
    )
    try:
        yield worktree
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(worktree)],
            check=False,
            capture_output=True,
        )
        shutil.rmtree(tmp, ignore_errors=True)
