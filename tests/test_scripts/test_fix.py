from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from scripts.fix import strip_new_comments

if TYPE_CHECKING:
    from pathlib import Path


def _git(*args: str, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def _write(repo: Path, name: str, body: str) -> Path:
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def test_strips_a_comment_the_change_introduced(git_repo: Path) -> None:
    path = _write(git_repo, "src/mod.py", "x = 1\n")
    _git("add", "src/mod.py", cwd=git_repo)
    _git("commit", "-m", "base", cwd=git_repo)
    path.write_text("x = 1\n# noise\ny = 2\n", encoding="utf-8")

    strip_new_comments(("src/mod.py",))

    assert path.read_text(encoding="utf-8") == "x = 1\ny = 2\n"


def test_leaves_a_comment_that_predates_the_change(git_repo: Path) -> None:
    path = _write(git_repo, "src/mod.py", "# kept\nx = 1\n")
    _git("add", "src/mod.py", cwd=git_repo)
    _git("commit", "-m", "base", cwd=git_repo)
    path.write_text("# kept\nx = 1\ny = 2\n", encoding="utf-8")

    strip_new_comments(("src/mod.py",))

    assert path.read_text(encoding="utf-8") == "# kept\nx = 1\ny = 2\n"


def test_keeps_a_linter_suppression_pragma(git_repo: Path) -> None:
    path = _write(git_repo, "src/mod.py", "x = 1\n")
    _git("add", "src/mod.py", cwd=git_repo)
    _git("commit", "-m", "base", cwd=git_repo)
    path.write_text("x = 1\nimport os  # noqa: E402\n", encoding="utf-8")

    strip_new_comments(("src/mod.py",))

    assert path.read_text(encoding="utf-8") == "x = 1\nimport os  # noqa: E402\n"


def test_never_touches_the_harness_outside_project_roots(git_repo: Path) -> None:
    body = "x = 1\n# harness comments are allowed\n"
    path = _write(git_repo, ".claude/hooks/thing.py", body)
    _git("add", ".claude/hooks/thing.py", cwd=git_repo)

    strip_new_comments((".claude/hooks/thing.py",))

    assert path.read_text(encoding="utf-8") == body


def test_ignores_a_path_with_no_diff_against_head(git_repo: Path) -> None:
    body = "x = 1\n# committed already\n"
    path = _write(git_repo, "src/mod.py", body)
    _git("add", "src/mod.py", cwd=git_repo)
    _git("commit", "-m", "base", cwd=git_repo)

    strip_new_comments(("src/mod.py",))

    assert path.read_text(encoding="utf-8") == body


def test_strips_every_line_of_a_newly_added_staged_file(git_repo: Path) -> None:
    path = _write(git_repo, "src/new.py", "# brand new\nx = 1\n")
    _git("add", "src/new.py", cwd=git_repo)

    strip_new_comments(("src/new.py",))

    assert path.read_text(encoding="utf-8") == "x = 1\n"


def test_strips_sql_the_change_introduced(git_repo: Path) -> None:
    path = _write(git_repo, "migrations/001.sql", "SELECT 1;\n")
    _git("add", "migrations/001.sql", cwd=git_repo)
    _git("commit", "-m", "base", cwd=git_repo)
    path.write_text("SELECT 1;\n-- noise\nSELECT 2;\n", encoding="utf-8")

    strip_new_comments(("migrations/001.sql",))

    assert path.read_text(encoding="utf-8") == "SELECT 1;\nSELECT 2;\n"


def test_skips_a_file_type_with_no_stripper(git_repo: Path) -> None:
    body = "# heading\n"
    path = _write(git_repo, "src/notes.md", body)
    _git("add", "src/notes.md", cwd=git_repo)

    strip_new_comments(("src/notes.md",))

    assert path.read_text(encoding="utf-8") == body
