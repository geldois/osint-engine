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
    subprocess.run(
        ["uv", "sync", "--quiet"],
        cwd=workdir,
        check=True,
    )


@contextmanager
def materialized_snapshot() -> Generator[Path]:
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
