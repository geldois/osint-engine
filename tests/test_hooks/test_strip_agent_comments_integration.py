from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_HOOK = (
    Path(__file__).resolve().parent.parent.parent
    / ".claude"
    / "hooks"
    / "strip_agent_comments.py"
)


def _run_hook(*, file_path: Path, cwd: Path) -> None:
    event = json.dumps({"tool_input": {"file_path": str(file_path)}})
    subprocess.run(
        [sys.executable, str(_HOOK)],
        input=event,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=True,
    )


def _commit(*args: str, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def test_strips_newly_added_comment_in_scoped_python_file(git_repo: Path) -> None:
    target = git_repo / "src" / "foo.py"
    target.parent.mkdir(parents=True)
    target.write_text("x = 1\n", encoding="utf-8")
    _commit("add", "src/foo.py", cwd=git_repo)
    _commit("commit", "-m", "seed foo.py", cwd=git_repo)

    target.write_text(
        "x = 1  # a plain comment\ny = 2  # noqa: F841\n", encoding="utf-8"
    )

    _run_hook(file_path=target, cwd=git_repo)

    assert target.read_text(encoding="utf-8") == "x = 1\ny = 2  # noqa: F841\n"


def test_leaves_pre_existing_comment_untouched_when_unrelated_line_changes(
    git_repo: Path,
) -> None:
    target = git_repo / "src" / "bar.py"
    target.parent.mkdir(parents=True)
    target.write_text("x = 1  # pre-existing, human-written\ny = 2\n", encoding="utf-8")
    _commit("add", "src/bar.py", cwd=git_repo)
    _commit("commit", "-m", "seed bar.py", cwd=git_repo)

    target.write_text("x = 1  # pre-existing, human-written\ny = 3\n", encoding="utf-8")

    _run_hook(file_path=target, cwd=git_repo)

    assert target.read_text(encoding="utf-8") == (
        "x = 1  # pre-existing, human-written\ny = 3\n"
    )


def test_ignores_files_outside_scoped_roots(git_repo: Path) -> None:
    target = git_repo / "notes.py"
    target.write_text("x = 1  # untouched\n", encoding="utf-8")
    _commit("add", "notes.py", cwd=git_repo)
    _commit("commit", "-m", "seed notes.py", cwd=git_repo)

    target.write_text("x = 1  # untouched\ny = 2  # also untouched\n", encoding="utf-8")

    _run_hook(file_path=target, cwd=git_repo)

    assert target.read_text(encoding="utf-8") == (
        "x = 1  # untouched\ny = 2  # also untouched\n"
    )


def test_strips_sql_comment_under_migrations(git_repo: Path) -> None:
    target = git_repo / "migrations" / "0001_init.sql"
    target.parent.mkdir(parents=True)
    target.write_text("SELECT 1;\n", encoding="utf-8")
    _commit("add", "migrations/0001_init.sql", cwd=git_repo)
    _commit("commit", "-m", "seed migration", cwd=git_repo)

    target.write_text(
        "SELECT 1; -- plain comment\nSELECT 2; -- noqa: LT01\n", encoding="utf-8"
    )

    _run_hook(file_path=target, cwd=git_repo)

    assert target.read_text(encoding="utf-8") == "SELECT 1;\nSELECT 2; -- noqa: LT01\n"


def test_new_untracked_file_is_stripped_wholesale(git_repo: Path) -> None:
    target = git_repo / "scripts" / "new_thing.py"
    target.parent.mkdir(parents=True)
    target.write_text(
        '"""New module."""\nx = 1  # brand new comment\n', encoding="utf-8"
    )

    _run_hook(file_path=target, cwd=git_repo)

    assert target.read_text(encoding="utf-8") == "x = 1\n"
