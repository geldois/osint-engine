from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from scripts._isolation import detached_worktree, materialized_snapshot

if TYPE_CHECKING:
    from pathlib import Path


def _git(*args: str, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def test_snapshot_reflects_the_staged_index_not_the_working_tree(
    git_repo: Path,
) -> None:
    (git_repo / "a.txt").write_text("staged\n", encoding="utf-8")
    _git("add", "a.txt", cwd=git_repo)
    (git_repo / "a.txt").write_text("working\n", encoding="utf-8")

    with materialized_snapshot() as snapshot:
        assert (snapshot / "a.txt").read_text(encoding="utf-8") == "staged\n"


def test_snapshot_excludes_untracked_files(git_repo: Path) -> None:
    (git_repo / "untracked.txt").write_text("nope\n", encoding="utf-8")

    with materialized_snapshot() as snapshot:
        assert not (snapshot / "untracked.txt").exists()


def test_snapshot_directory_is_removed_after_the_context(git_repo: Path) -> None:
    del git_repo
    with materialized_snapshot() as snapshot:
        path = snapshot

    assert not path.exists()


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
