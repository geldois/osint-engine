from __future__ import annotations

import shutil
import subprocess
from typing import TYPE_CHECKING

from scripts._isolation import detached_worktree

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_a_worktree_left_behind_by_a_killed_run_is_pruned(
    git_repo: Path, tmp_path_factory: pytest.TempPathFactory
) -> None:
    stale = tmp_path_factory.mktemp("stale") / "tree"
    subprocess.run(
        ["git", "worktree", "add", "--quiet", "--detach", str(stale), "HEAD"],
        cwd=git_repo,
        check=True,
    )
    shutil.rmtree(stale)

    with detached_worktree("HEAD"):
        pass

    listed = subprocess.run(
        ["git", "worktree", "list"],
        cwd=git_repo,
        check=True,
        capture_output=True,
        text=True,
    )
    assert str(stale) not in listed.stdout


def test_detached_worktree_checks_out_the_commit_and_cleans_up(
    git_repo: Path,
) -> None:
    with detached_worktree("HEAD") as worktree:
        assert (worktree / "seed.txt").read_text(encoding="utf-8") == "seed\n"
        path = worktree

    assert not path.exists()
    listed = subprocess.run(
        ["git", "worktree", "list"],
        cwd=git_repo,
        check=True,
        capture_output=True,
        text=True,
    )
    assert str(path) not in listed.stdout
