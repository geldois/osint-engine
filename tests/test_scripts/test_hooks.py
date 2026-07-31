from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

from scripts import hooks

if TYPE_CHECKING:
    from pathlib import Path

_MANAGED = ("pre-commit", "pre-merge-commit")


def _hooks_dir(git_repo: Path) -> Path:
    return git_repo / ".git" / "hooks"


def test_install_writes_the_three_managed_hooks_executable(git_repo: Path) -> None:
    hooks.install()

    for name in _MANAGED:
        hook = _hooks_dir(git_repo) / name
        assert hook.exists()
        assert os.access(hook, os.X_OK)
        assert "python -m scripts" in hook.read_text(encoding="utf-8")


def test_install_is_idempotent(git_repo: Path) -> None:
    hooks.install()
    first = {
        n: (_hooks_dir(git_repo) / n).read_text(encoding="utf-8") for n in _MANAGED
    }

    hooks.install()
    second = {
        n: (_hooks_dir(git_repo) / n).read_text(encoding="utf-8") for n in _MANAGED
    }

    assert first == second


def test_install_does_not_clobber_a_foreign_hook(git_repo: Path) -> None:
    foreign = "#!/bin/sh\necho mine\n"
    (_hooks_dir(git_repo) / "pre-commit").write_text(foreign, encoding="utf-8")

    hooks.install()

    assert (_hooks_dir(git_repo) / "pre-commit").read_text(encoding="utf-8") == foreign


def test_install_outside_a_git_repository_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(hooks.NotAGitRepositoryError):
        hooks.install()
