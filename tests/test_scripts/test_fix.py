from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from scripts._report import REPORT_PATH
from scripts.fix import run_fix, run_precommit

if TYPE_CHECKING:
    import pytest

_POST_COMMIT = Path(__file__).parents[2] / ".githooks" / "post-commit"


def _git(*args: str, cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    )
    return result.stdout


def _fake_shfmt(targets: list[str]) -> None:
    for target in targets:
        Path(target).write_text('echo "fixed"\n', encoding="utf-8")


def test_run_fix_keeps_a_rewritten_staged_file_fully_staged(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("scripts.fix.SHELL_FILES", ("a.sh",))
    monkeypatch.setattr("scripts.fix._shfmt", _fake_shfmt)

    target = git_repo / "a.sh"
    target.write_text("echo hi\n", encoding="utf-8")
    _git("add", "a.sh", cwd=git_repo)
    sha = _git("hash-object", "a.sh", cwd=git_repo).strip()

    run_fix()

    assert _git("show", ":a.sh", cwd=git_repo) == 'echo "fixed"\n'
    assert _git("diff", "--", "a.sh", cwd=git_repo) == ""
    assert (git_repo / "build" / ".gate-fixed-paths").read_text() == f"a.sh\t{sha}\n"


def test_run_fix_leaves_an_unstaged_rewrite_unstaged(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("scripts.fix.SHELL_FILES", ("seed.sh",))
    monkeypatch.setattr("scripts.fix._shfmt", _fake_shfmt)

    (git_repo / "seed.sh").write_text("echo seed\n", encoding="utf-8")
    _git("add", "seed.sh", cwd=git_repo)
    _git("commit", "-m", "seed", cwd=git_repo)

    run_fix()

    assert _git("diff", "--cached", "--name-only", cwd=git_repo) == ""
    assert (git_repo / "seed.sh").read_text(encoding="utf-8") == 'echo "fixed"\n'


def test_post_commit_syncs_the_index_only_for_a_stale_rewrite(
    git_repo: Path,
) -> None:
    target = git_repo / "a.sh"
    target.write_text('echo "fixed"\n', encoding="utf-8")
    _git("add", "a.sh", cwd=git_repo)
    _git("commit", "-m", "fixed", cwd=git_repo)

    target.write_text("echo stale\n", encoding="utf-8")
    _git("add", "a.sh", cwd=git_repo)
    sha = _git("hash-object", "a.sh", cwd=git_repo).strip()
    _git("restore", "--source=HEAD", "--", "a.sh", cwd=git_repo)
    (git_repo / "build").mkdir()
    (git_repo / "build" / ".gate-fixed-paths").write_text(
        f"a.sh\t{sha}\n", encoding="utf-8"
    )

    subprocess.run(["sh", str(_POST_COMMIT)], cwd=git_repo, check=True)

    assert _git("diff", "--cached", "--name-only", cwd=git_repo) == ""


def test_post_commit_leaves_a_staged_next_version_alone(
    git_repo: Path,
) -> None:
    target = git_repo / "a.sh"
    target.write_text('echo "fixed"\n', encoding="utf-8")
    _git("add", "a.sh", cwd=git_repo)
    _git("commit", "-m", "fixed", cwd=git_repo)

    target.write_text("echo next\n", encoding="utf-8")
    _git("add", "a.sh", cwd=git_repo)
    (git_repo / "build").mkdir()
    (git_repo / "build" / ".gate-fixed-paths").write_text(
        "a.sh\t0000\n", encoding="utf-8"
    )

    subprocess.run(["sh", str(_POST_COMMIT)], cwd=git_repo, check=True)

    assert _git("diff", "--cached", "--name-only", cwd=git_repo) == "a.sh\n"


def test_post_commit_does_not_touch_a_staged_then_reverted_file(
    git_repo: Path,
) -> None:
    target = git_repo / "a.sh"
    target.write_text('echo "fixed"\n', encoding="utf-8")
    _git("add", "a.sh", cwd=git_repo)
    _git("commit", "-m", "fixed", cwd=git_repo)

    target.write_text("echo stale\n", encoding="utf-8")
    _git("add", "a.sh", cwd=git_repo)
    _git("restore", "--source=HEAD", "--", "a.sh", cwd=git_repo)
    (git_repo / "build").mkdir()
    (git_repo / "build" / ".gate-fixed-paths").write_text(
        "b.sh\t0000\n", encoding="utf-8"
    )

    subprocess.run(["sh", str(_POST_COMMIT)], cwd=git_repo, check=True)

    assert _git("diff", "--cached", "--name-only", cwd=git_repo) == "a.sh\n"


def test_run_fix_writes_no_marker_when_nothing_was_rewritten(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("scripts.fix.SHELL_FILES", ())

    target = git_repo / "a.sh"
    target.write_text("echo hi\n", encoding="utf-8")
    _git("add", "a.sh", cwd=git_repo)

    run_fix()

    assert not (git_repo / "build" / ".gate-fixed-paths").exists()


def test_run_precommit_unstages_a_rewritten_file_when_check_fails(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("scripts.fix.SHELL_FILES", ("a.sh",))
    monkeypatch.setattr("scripts.fix._shfmt", _fake_shfmt)

    calls: list[bool] = []

    def _fake_check(*, full: bool) -> int:
        calls.append(full)
        return 1

    monkeypatch.setattr("scripts.fix.run_check", _fake_check)

    target = git_repo / "a.sh"
    target.write_text("echo hi\n", encoding="utf-8")
    _git("add", "a.sh", cwd=git_repo)

    assert run_precommit() == 1
    assert calls == [True]
    assert _git("diff", "--cached", "--name-only", cwd=git_repo) == ""
    assert (git_repo / "a.sh").read_text(encoding="utf-8") == 'echo "fixed"\n'


def test_run_precommit_skips_check_when_the_tree_is_unchanged(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (git_repo / ".gitignore").write_text("build/\n", encoding="utf-8")

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
