from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from scripts._report import REPORT_PATH
from scripts.fix import run_precommit

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def _git(*args: str, cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    )
    return result.stdout


def _fake_check_ok(*, full: bool) -> int:
    del full
    return 0


def test_run_precommit_keeps_a_rewritten_file_fully_staged(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = git_repo / "a.py"
    target.write_text("x=1\n", encoding="utf-8")
    _git("add", "a.py", cwd=git_repo)

    def _fake_run_fix(paths: tuple[str, ...] = ()) -> int:
        del paths
        target.write_text("x = 1\n", encoding="utf-8")
        return 0

    monkeypatch.setattr("scripts.fix.run_fix", _fake_run_fix)
    monkeypatch.setattr("scripts.fix.run_check", _fake_check_ok)

    run_precommit()

    assert _git("show", ":a.py", cwd=git_repo) == "x = 1\n"
    assert _git("diff", "--", "a.py", cwd=git_repo) == ""


def test_run_precommit_leaves_an_unstaged_rewrite_unstaged(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (git_repo / "seed.txt").write_text("seed\n", encoding="utf-8")

    def _fake_run_fix(paths: tuple[str, ...] = ()) -> int:
        del paths
        (git_repo / "seed.txt").write_text("rewritten\n", encoding="utf-8")
        return 0

    monkeypatch.setattr("scripts.fix.run_fix", _fake_run_fix)
    monkeypatch.setattr("scripts.fix.run_check", _fake_check_ok)

    run_precommit()

    assert _git("diff", "--cached", "--name-only", cwd=git_repo) == ""


def test_run_precommit_skips_check_when_the_tree_is_unchanged(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    del git_repo

    def _fake_run_fix(paths: tuple[str, ...] = ()) -> int:
        del paths
        return 0

    calls: list[bool] = []

    def _fake_check(*, full: bool) -> int:
        calls.append(full)
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(
            '{"generated_at": "x", "passed": true, "gates": []}', encoding="utf-8"
        )
        return 0

    monkeypatch.setattr("scripts.fix.run_fix", _fake_run_fix)
    monkeypatch.setattr("scripts.fix.run_check", _fake_check)

    assert run_precommit() == 0
    assert run_precommit() == 0

    assert calls == [True]
