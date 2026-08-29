from __future__ import annotations

import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator


def sync(workdir: Path) -> None:
    subprocess.run(
        ["uv", "sync", "--quiet"],
        cwd=workdir,
        check=True,
    )


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
