from __future__ import annotations

import pytest
from _comment_stripper import strip_python, strip_sql

_PYTHON_CASES: dict[str, tuple[str, str]] = {
    "plain_comment_own_line": (
        "x = 1\n# just a comment\ny = 2\n",
        "x = 1\ny = 2\n",
    ),
    "plain_trailing_comment": (
        "x = 1  # trailing\n",
        "x = 1\n",
    ),
    "noqa_bare_survives": (
        "x = 1  # noqa\n",
        "x = 1  # noqa\n",
    ),
    "noqa_with_code_survives": (
        "x = 1  # noqa: F841\n",
        "x = 1  # noqa: F841\n",
    ),
    "noqa_multiple_codes_survive": (
        "i = 1  # noqa: E741, F841\n",
        "i = 1  # noqa: E741, F841\n",
    ),
    "ruff_file_level_noqa_survives": (
        "# ruff: noqa: UP035\nfrom typing import Iterable\n",
        "# ruff: noqa: UP035\nfrom typing import Iterable\n",
    ),
    "pyright_ignore_bare_survives": (
        "x: int = risky()  # pyright: ignore\n",
        "x: int = risky()  # pyright: ignore\n",
    ),
    "pyright_ignore_with_code_survives": (
        "x: int = risky()  # pyright: ignore[reportArgumentType]\n",
        "x: int = risky()  # pyright: ignore[reportArgumentType]\n",
    ),
    "type_ignore_survives": (
        "x: int = risky()  # type: ignore\n",
        "x: int = risky()  # type: ignore\n",
    ),
    "type_ignore_with_code_survives": (
        "x: int = risky()  # type: ignore[assignment]\n",
        "x: int = risky()  # type: ignore[assignment]\n",
    ),
    "chained_noqa_and_pyright_ignore_survives": (
        "x._private()  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]\n",
        "x._private()  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]\n",
    ),
    "chained_pragma_with_real_comment_is_stripped": (
        "x = 1  # noqa: F841  # actually explains nothing\n",
        "x = 1\n",
    ),
    "pragma_no_cover_survives": (
        "if x:  # pragma: no cover\n    y = 1\n",
        "if x:  # pragma: no cover\n    y = 1\n",
    ),
    "shebang_survives": (
        "#!/usr/bin/env python3\nx = 1\n",
        "#!/usr/bin/env python3\nx = 1\n",
    ),
    "hash_inside_plain_string_survives": (
        'x = "not a # comment"\n',
        'x = "not a # comment"\n',
    ),
    "hash_inside_non_docstring_triple_quote_survives": (
        'x = """text with # not a comment"""\n',
        'x = """text with # not a comment"""\n',
    ),
    "hash_inside_fstring_literal_survives": (
        'x = f"value: {y} # not a comment"\n',
        'x = f"value: {y} # not a comment"\n',
    ),
    "module_docstring_removed": (
        '"""Module doc."""\n\nx = 1\n',
        "\nx = 1\n",
    ),
    "module_docstring_as_sole_statement_empties_file": (
        '"""Just a module doc."""\n',
        "",
    ),
    "function_docstring_removed_keeps_body": (
        'def f():\n    """Doc."""\n    return 1\n',
        "def f():\n    return 1\n",
    ),
    "function_docstring_sole_statement_becomes_pass": (
        'def f():\n    """Doc only."""\n',
        "def f():\n    pass\n",
    ),
    "class_docstring_sole_statement_becomes_pass": (
        'class Foo:\n    """Doc only."""\n',
        "class Foo:\n    pass\n",
    ),
    "multiline_docstring_removed": (
        'def f():\n    """\n    Multi-line doc.\n    """\n    return 1\n',
        "def f():\n    return 1\n",
    ),
    "typer_command_docstring_survives": (
        '@app.command()\ndef check() -> None:\n    """Run the gate."""\n    pass\n',
        '@app.command()\ndef check() -> None:\n    """Run the gate."""\n    pass\n',
    ),
    "non_typer_decorator_docstring_removed": (
        '@app.other()\ndef check() -> None:\n    """Not exempt."""\n    pass\n',
        "@app.other()\ndef check() -> None:\n    pass\n",
    ),
    "syntax_error_returned_unchanged": (
        "def f(:\n",
        "def f(:\n",
    ),
}


@pytest.mark.parametrize(
    ("source", "expected"), _PYTHON_CASES.values(), ids=_PYTHON_CASES.keys()
)
def test_strip_python(source: str, expected: str) -> None:
    assert strip_python(source) == expected


def test_strip_python_respects_changed_lines() -> None:
    source = "x = 1  # keep me (not in changed_lines)\ny = 2  # strip me\n"
    expected = "x = 1  # keep me (not in changed_lines)\ny = 2\n"

    assert strip_python(source, changed_lines=frozenset({2})) == expected


def test_strip_python_changed_lines_empty_set_strips_nothing() -> None:
    source = "x = 1  # untouched\n"

    assert strip_python(source, changed_lines=frozenset()) == source


_SQL_CASES: dict[str, tuple[str, str]] = {
    "plain_comment_own_line": (
        "SELECT 1;\n-- just a comment\nSELECT 2;\n",
        "SELECT 1;\nSELECT 2;\n",
    ),
    "plain_trailing_comment": (
        "SELECT 1; -- trailing\n",
        "SELECT 1;\n",
    ),
    "noqa_bare_survives": (
        "SELECT 1; -- noqa\n",
        "SELECT 1; -- noqa\n",
    ),
    "noqa_with_code_survives": (
        "SELECT 1; -- noqa: LT01\n",
        "SELECT 1; -- noqa: LT01\n",
    ),
    "noqa_disable_all_survives": (
        "SELECT 1; -- noqa: disable=all\n",
        "SELECT 1; -- noqa: disable=all\n",
    ),
    "dashes_inside_single_quoted_string_survive": (
        "SELECT '--not a comment';\n",
        "SELECT '--not a comment';\n",
    ),
    "dashes_inside_double_quoted_identifier_survive": (
        'SELECT "col--name" FROM t;\n',
        'SELECT "col--name" FROM t;\n',
    ),
    "escaped_single_quote_inside_string_handled": (
        "SELECT 'it''s -- fine';\n",
        "SELECT 'it''s -- fine';\n",
    ),
}


@pytest.mark.parametrize(
    ("source", "expected"), _SQL_CASES.values(), ids=_SQL_CASES.keys()
)
def test_strip_sql(source: str, expected: str) -> None:
    assert strip_sql(source) == expected


def test_strip_sql_respects_changed_lines() -> None:
    source = "SELECT 1; -- keep\nSELECT 2; -- strip\n"
    expected = "SELECT 1; -- keep\nSELECT 2;\n"

    assert strip_sql(source, changed_lines=frozenset({2})) == expected
