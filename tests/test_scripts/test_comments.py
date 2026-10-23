from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

import pytest

from scripts.comments import (
    hash_comment_lines,
    is_scanned,
    python_comment_lines,
    run_comments,
    sql_comment_lines,
)

if TYPE_CHECKING:
    from pathlib import Path

_PYTHON_CASES: dict[str, tuple[str, list[int]]] = {
    "plain_comment_own_line": ("x = 1\n# just a comment\ny = 2\n", [2]),
    "plain_trailing_comment": ("x = 1  # trailing\n", [1]),
    "noqa_bare_survives": ("x = 1  # noqa\n", []),
    "noqa_with_code_survives": ("x = 1  # noqa: F841\n", []),
    "noqa_multiple_codes_survive": ("i = 1  # noqa: E741, F841\n", []),
    "ruff_file_level_noqa_survives": (
        "# ruff: noqa: UP035\nfrom typing import Iterable\n",
        [],
    ),
    "pyright_ignore_bare_survives": ("x: int = risky()  # pyright: ignore\n", []),
    "pyright_ignore_with_code_survives": (
        "x: int = risky()  # pyright: ignore[reportArgumentType]\n",
        [],
    ),
    "type_ignore_survives": ("x: int = risky()  # type: ignore\n", []),
    "type_ignore_with_code_survives": (
        "x: int = risky()  # type: ignore[assignment]\n",
        [],
    ),
    "chained_noqa_and_pyright_ignore_survives": (
        "x._private()  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]\n",
        [],
    ),
    "chained_pragma_with_real_comment_is_flagged": (
        "x = 1  # noqa: F841  # actually explains nothing\n",
        [1],
    ),
    "pragma_no_cover_survives": ("if x:  # pragma: no cover\n    y = 1\n", []),
    "shebang_survives": ("#!/usr/bin/env python3\nx = 1\n", []),
    "hash_inside_plain_string_survives": ('x = "not a # comment"\n', []),
    "hash_inside_non_docstring_triple_quote_survives": (
        'x = """text with # not a comment"""\n',
        [],
    ),
    "hash_inside_fstring_literal_survives": (
        'x = f"value: {y} # not a comment"\n',
        [],
    ),
    "module_docstring_flagged": ('"""Module doc."""\n\nx = 1\n', [1]),
    "function_docstring_flagged": (
        'def f():\n    """Doc."""\n    return 1\n',
        [2],
    ),
    "class_docstring_flagged": ('class Foo:\n    """Doc only."""\n', [2]),
    "multiline_docstring_flagged": (
        'def f():\n    """\n    Multi-line doc.\n    """\n    return 1\n',
        [2],
    ),
    "typer_command_docstring_flagged": (
        '@app.command()\ndef check() -> None:\n    """Run the gate."""\n    pass\n',
        [3],
    ),
    "syntax_error_yields_nothing": ("def f(:\n", []),
}


@pytest.mark.parametrize(
    ("source", "expected"), _PYTHON_CASES.values(), ids=_PYTHON_CASES.keys()
)
def test_python(source: str, expected: list[int]) -> None:
    assert python_comment_lines(source) == expected


_SQL_CASES: dict[str, tuple[str, list[int]]] = {
    "plain_comment_own_line": ("SELECT 1;\n-- just a comment\nSELECT 2;\n", [2]),
    "plain_trailing_comment": ("SELECT 1; -- trailing\n", [1]),
    "noqa_bare_survives": ("SELECT 1; -- noqa\n", []),
    "noqa_with_code_survives": ("SELECT 1; -- noqa: LT01\n", []),
    "noqa_disable_all_survives": ("SELECT 1; -- noqa: disable=all\n", []),
    "sqlc_name_annotation_survives": (
        "-- name: FindByUsernameAndProvider :one\nSELECT 1;\n",
        [],
    ),
    "dashes_inside_single_quoted_string_survive": ("SELECT '--not a comment';\n", []),
    "dashes_inside_double_quoted_identifier_survive": (
        'SELECT "col--name" FROM t;\n',
        [],
    ),
    "escaped_single_quote_inside_string_handled": ("SELECT 'it''s -- fine';\n", []),
}


@pytest.mark.parametrize(
    ("source", "expected"), _SQL_CASES.values(), ids=_SQL_CASES.keys()
)
def test_sql(source: str, expected: list[int]) -> None:
    assert sql_comment_lines(source) == expected


_HASH_CASES: dict[str, tuple[str, list[int]]] = {
    "plain_comment_own_line": ("set -e\n# just a comment\necho hi\n", [2]),
    "plain_trailing_comment": ("echo hi  # trailing\n", [1]),
    "shebang_survives": ("#!/bin/sh\necho hi\n", []),
    "shellcheck_disable_survives": (
        "# shellcheck disable=SC2034\nx=1\n",
        [],
    ),
    "shellcheck_source_survives": (
        "# shellcheck source=/dev/null\n. ./lib.sh\n",
        [],
    ),
    "shellcheck_enable_survives": ("# shellcheck enable=all\n", []),
    "pinned_action_version_comment_survives": (
        "  - uses: actions/checkout@abc123 # v7.0.0\n",
        [],
    ),
    "hash_inside_single_quoted_string_survives": ("echo 'not # a comment'\n", []),
    "hash_inside_double_quoted_string_survives": ('echo "not # a comment"\n', []),
    "shell_argument_count_survives": ("echo $#\n", []),
    "shell_length_expansion_survives": ('echo "${#name}"\n', []),
    "escaped_double_quote_inside_string_handled": (
        'echo "she said \\"hi\\" # still a string"\n',
        [],
    ),
}


@pytest.mark.parametrize(
    ("source", "expected"), _HASH_CASES.values(), ids=_HASH_CASES.keys()
)
def test_hash(source: str, expected: list[int]) -> None:
    assert hash_comment_lines(source) == expected


def test_pragma_word_inside_ordinary_comment_is_still_flagged() -> None:
    source = "x = 1  # this used to have a noqa word in it, not a pragma\n"

    assert python_comment_lines(source) == [1]


@pytest.mark.parametrize(
    "rel",
    [
        "src/osint_engine/x.py",
        "migrations/001.sql",
        ".githooks/pre-commit",
        "pyproject.toml",
        "Dockerfile",
        ".env.example",
        ".gitattributes",
        ".sqruff",
        ".yamllint",
        "a-file-type-nobody-listed.cfg",
        "tools/Makefile",
    ],
)
def test_is_scanned_covers_every_file_not_excluded(rel: str) -> None:
    assert is_scanned(rel)


@pytest.mark.parametrize(
    "rel",
    [
        "src/osint_engine/infrastructure/persistence/pg/generated/models.py",
        "README.md",
        "dprint.json",
        "uv.lock",
        "LICENSE",
        ".python-version",
    ],
)
def test_is_scanned_skips_generated_data_and_prose(rel: str) -> None:
    assert not is_scanned(rel)


def test_run_comments_reports_offending_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "bad.py").write_text("x = 1  # why\n", encoding="utf-8")
    (tmp_path / "good.py").write_text("x = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    monkeypatch.chdir(tmp_path)

    assert run_comments() == 1
    assert "bad.py:1" in capsys.readouterr().err


def test_run_comments_passes_on_a_clean_repo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "good.py").write_text("x = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    monkeypatch.chdir(tmp_path)

    assert run_comments() == 0
