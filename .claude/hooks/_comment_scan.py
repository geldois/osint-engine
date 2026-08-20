"""Comment/docstring detection — read-only, never a rewrite.

A prior version of this pipeline auto-stripped new comments and docstrings at
pre-commit; removed because its edge cases (typer-command exemption, f-string
false positives) could silently mismatch what the model still holds in
context. ``report_comments.py`` nudges instead, so a misparse here costs an
extra reminder, never a corrupted file.

Distinguishes a real comment/docstring from a linter-suppression pragma via a
closed, tool-documented allowlist (ruff noqa, basedpyright pyright:ignore and
the PEP 484 type:ignore form, coverage.py pragma, sqruff/sqlfluff noqa) —
never by guessing intent. Python detection walks ``tokenize`` for comments and
``ast`` for docstring statements so a ``#`` inside a string/f-string is never
misread as a comment.
"""

from __future__ import annotations

import ast
import re
import tokenize
from io import StringIO
from typing import NamedTuple

_PY_PRAGMA_CLAUSE = re.compile(
    r"#\s*(?:"
    r"noqa(?::\s*[A-Z0-9]+(?:,\s*[A-Z0-9]+)*)?"
    r"|ruff:\s*noqa(?::\s*[A-Z0-9]+(?:,\s*[A-Z0-9]+)*)?"
    r"|pyright:\s*ignore(?:\[[a-zA-Z0-9_, ]+\])?"
    r"|type:\s*ignore(?:\[[a-zA-Z0-9_, ]+\])?"
    r"|pragma:\s*no cover"
    r")\s*",
)
_SQL_PRAGMA = re.compile(r"^--\s*(?:noqa\b.*|name:\s*\S+\s+:\S+\s*)$")


class _Span(NamedTuple):
    start_line: int
    end_line: int


def _is_shebang(line_number: int, text: str) -> bool:
    return line_number == 1 and text.startswith("#!")


def _is_typer_command(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(
        isinstance(decorator, ast.Call)
        and isinstance(decorator.func, ast.Attribute)
        and decorator.func.attr == "command"
        for decorator in node.decorator_list
    )


def _docstring_span(
    container: ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef,
) -> _Span | None:
    body = container.body
    if not body:
        return None
    first = body[0]
    if not (
        isinstance(first, ast.Expr)
        and isinstance(first.value, ast.Constant)
        and isinstance(first.value.value, str)
    ):
        return None
    if isinstance(
        container, ast.FunctionDef | ast.AsyncFunctionDef
    ) and _is_typer_command(
        container,
    ):
        return None
    return _Span(first.lineno, first.end_lineno or first.lineno)


def _docstring_spans(tree: ast.Module) -> list[_Span]:
    spans: list[_Span] = []
    for candidate in ast.walk(tree):
        if not isinstance(
            candidate,
            ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef,
        ):
            continue
        span = _docstring_span(candidate)
        if span is not None:
            spans.append(span)
    return spans


def is_pragma_comment(text: str) -> bool:
    """Whether every ``#``-clause chained in ``text`` is an allowlisted pragma.

    A single trailing comment can chain more than one directive on one line
    (``# noqa: SLF001  # pyright: ignore[reportPrivateUsage]``) — tokenize
    yields that as one COMMENT token, so each clause is checked individually.
    """
    clauses = [clause.strip() for clause in re.split(r"(?=#)", text) if clause.strip()]
    return bool(clauses) and all(
        _PY_PRAGMA_CLAUSE.fullmatch(clause) for clause in clauses
    )


def _comment_spans(source: str) -> list[_Span]:
    spans: list[_Span] = []
    for token in tokenize.generate_tokens(StringIO(source).readline):
        if token.type != tokenize.COMMENT:
            continue
        if _is_shebang(token.start[0], token.string) or is_pragma_comment(token.string):
            continue
        spans.append(_Span(token.start[0], token.end[0]))
    return spans


def _in_changed_lines(span: _Span, changed_lines: frozenset[int] | None) -> bool:
    if changed_lines is None:
        return True
    return all(
        line in changed_lines for line in range(span.start_line, span.end_line + 1)
    )


def new_comment_lines_python(
    source: str, changed_lines: frozenset[int] | None
) -> list[int]:
    """Line numbers of every non-pragma comment/docstring inside ``changed_lines``.

    ``changed_lines=None`` means every line counts. Unchanged (empty) on a
    syntax error — a file that doesn't parse has nothing safe to scan.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    spans = (*_docstring_spans(tree), *_comment_spans(source))
    lines = {
        span.start_line for span in spans if _in_changed_lines(span, changed_lines)
    }
    return sorted(lines)


def new_comment_lines_sql(
    source: str, changed_lines: frozenset[int] | None
) -> list[int]:
    """Line numbers of every non-pragma ``--`` comment inside ``changed_lines``."""
    lines: list[int] = []
    for line_number, line in enumerate(source.splitlines(), start=1):
        if changed_lines is not None and line_number not in changed_lines:
            continue
        index = _unquoted_comment_index(line)
        if index is None:
            continue
        if _SQL_PRAGMA.match(line[index:].strip()):
            continue
        lines.append(line_number)
    return lines


def _unquoted_comment_index(content: str) -> int | None:
    """Index of an unquoted ``--`` in ``content``, or ``None`` if there isn't one."""
    in_single = in_double = False
    i, n = 0, len(content)
    while i < n:
        char = content[i]
        if in_single:
            if char == "'" and not (i + 1 < n and content[i + 1] == "'"):
                in_single = False
            elif char == "'":
                i += 1
        elif in_double:
            in_double = char != '"'
        elif char == "'":
            in_single = True
        elif char == '"':
            in_double = True
        elif char == "-" and i + 1 < n and content[i + 1] == "-":
            return i
        i += 1
    return None
