from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_MODULE_PATH = Path(__file__).parents[2] / ".claude" / "hooks" / "_comment_scan.py"
_spec = importlib.util.spec_from_file_location("_comment_scan", _MODULE_PATH)
assert _spec is not None
assert _spec.loader is not None
_comment_scan = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_comment_scan)

new_comment_lines_python = _comment_scan.new_comment_lines_python
new_comment_lines_sql = _comment_scan.new_comment_lines_sql
new_comment_lines_hash = _comment_scan.new_comment_lines_hash
is_pragma_comment = _comment_scan.is_pragma_comment

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
    "typer_command_docstring_survives": (
        '@app.command()\ndef check() -> None:\n    """Run the gate."""\n    pass\n',
        [],
    ),
    "non_typer_decorator_docstring_flagged": (
        '@app.other()\ndef check() -> None:\n    """Not exempt."""\n    pass\n',
        [3],
    ),
    "syntax_error_yields_nothing": ("def f(:\n", []),
}


@pytest.mark.parametrize(
    ("source", "expected"), _PYTHON_CASES.values(), ids=_PYTHON_CASES.keys()
)
def test_new_comment_lines_python(source: str, expected: list[int]) -> None:
    assert new_comment_lines_python(source, None) == expected


def test_new_comment_lines_python_respects_changed_lines() -> None:
    source = "x = 1  # keep me (not in changed_lines)\ny = 2  # flag me\n"

    assert new_comment_lines_python(source, frozenset({2})) == [2]


def test_new_comment_lines_python_changed_lines_empty_set_flags_nothing() -> None:
    source = "x = 1  # untouched\n"

    assert new_comment_lines_python(source, frozenset()) == []


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
def test_new_comment_lines_sql(source: str, expected: list[int]) -> None:
    assert new_comment_lines_sql(source, None) == expected


def test_new_comment_lines_sql_respects_changed_lines() -> None:
    source = "SELECT 1; -- keep\nSELECT 2; -- flag\n"

    assert new_comment_lines_sql(source, frozenset({2})) == [2]


def test_is_pragma_comment_rejects_ordinary_comment_mentioning_pragma_word() -> None:
    comment = "# this used to have a noqa word in it, not a pragma"
    assert is_pragma_comment(comment) is False


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
    "escaped_double_quote_inside_string_handled": (
        'echo "she said \\"hi\\" # still a string"\n',
        [],
    ),
}


@pytest.mark.parametrize(
    ("source", "expected"), _HASH_CASES.values(), ids=_HASH_CASES.keys()
)
def test_new_comment_lines_hash(source: str, expected: list[int]) -> None:
    assert new_comment_lines_hash(source, None) == expected


def test_new_comment_lines_hash_respects_changed_lines() -> None:
    source = "echo hi  # keep\necho bye  # flag\n"

    assert new_comment_lines_hash(source, frozenset({2})) == [2]
