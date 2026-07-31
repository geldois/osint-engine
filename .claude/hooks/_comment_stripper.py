"""Pure comment/docstring removal for Python and SQL source.

Distinguishes a real comment/docstring from a linter-suppression pragma via a
closed, tool-documented allowlist (ruff noqa, basedpyright pyright:ignore and
the PEP 484 type:ignore form, coverage.py pragma, sqruff/sqlfluff noqa) —
never by guessing intent. Python
removal walks ``tokenize`` for comments and ``ast`` for docstring statements so
a ``#`` inside a string/f-string is never misread as a comment, and a
docstring that is the sole statement in a function/class body is replaced
with ``pass`` so the result stays syntactically valid.

Both entry points take an optional ``changed_lines`` set restricting removal
to those line numbers — the caller (the hook wrapper) passes the file's
current git-diff-vs-HEAD line set, so a comment that predates this edit (the
agent's or a human's) is never touched, only what this edit actually changed.
``None`` means unrestricted, used by tests exercising the pure logic.
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
_SQL_PRAGMA = re.compile(r"^--\s*noqa\b.*$")


class _Span(NamedTuple):
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    replace_with_pass: bool


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
    sole_statement = len(body) == 1 and not isinstance(container, ast.Module)
    return _Span(
        first.lineno,
        first.col_offset,
        first.end_lineno or first.lineno,
        first.end_col_offset or first.col_offset,
        replace_with_pass=sole_statement,
    )


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
        spans.append(
            _Span(
                token.start[0],
                token.start[1],
                token.end[0],
                token.end[1],
                replace_with_pass=False,
            )
        )
    return spans


def _line_ending(line: str) -> str:
    if line.endswith("\r\n"):
        return "\r\n"
    if line.endswith("\n"):
        return "\n"
    return ""


def _apply_span(lines: list[str], span: _Span) -> None:
    ending = _line_ending(lines[span.end_line - 1])
    if span.replace_with_pass:
        lines[span.start_line - 1 : span.end_line] = [
            f"{' ' * span.start_col}pass{ending}"
        ]
        return

    start_line_text = lines[span.start_line - 1]
    if start_line_text[: span.start_col].strip() == "":
        del lines[span.start_line - 1 : span.end_line]
        return

    # Trailing comment/docstring sharing a line with real code: trim from the
    # span's start onward instead of deleting the whole line.
    prefix = start_line_text[: span.start_col].rstrip()
    lines[span.start_line - 1 : span.end_line] = [f"{prefix}{ending}"]


def _in_changed_lines(span: _Span, changed_lines: frozenset[int] | None) -> bool:
    if changed_lines is None:
        return True
    return all(
        line in changed_lines for line in range(span.start_line, span.end_line + 1)
    )


def strip_python(source: str, changed_lines: frozenset[int] | None = None) -> str:
    """Remove every non-pragma comment/docstring within ``changed_lines``.

    Unchanged on a syntax error. ``changed_lines=None`` strips the whole file.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source

    spans = [
        span
        for span in (*_docstring_spans(tree), *_comment_spans(source))
        if _in_changed_lines(span, changed_lines)
    ]
    if not spans:
        return source

    lines = source.splitlines(keepends=True)
    # Bottom-to-top so an earlier (higher-line-number) edit never invalidates
    # the line numbers a later (lower-line-number) edit still relies on.
    for span in sorted(spans, key=lambda s: (s.start_line, s.start_col), reverse=True):
        _apply_span(lines, span)
    return "".join(lines)


def _split_sql_ending(line: str) -> tuple[str, str]:
    if line.endswith("\r\n"):
        return line[:-2], "\r\n"
    if line.endswith("\n"):
        return line[:-1], "\n"
    return line, ""


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


def _strip_sql_line(line: str) -> str | None:
    content, ending = _split_sql_ending(line)
    index = _unquoted_comment_index(content)
    if index is None or _SQL_PRAGMA.match(content[index:].strip()):
        return line
    prefix = content[:index]
    return None if prefix.strip() == "" else f"{prefix.rstrip()}{ending}"


def strip_sql(source: str, changed_lines: frozenset[int] | None = None) -> str:
    """Remove every non-pragma ``--`` comment line within ``changed_lines``.

    Quote-aware. ``changed_lines=None`` strips the whole file.
    """
    result: list[str] = []
    for line_number, line in enumerate(source.splitlines(keepends=True), start=1):
        if changed_lines is not None and line_number not in changed_lines:
            result.append(line)
            continue
        stripped = _strip_sql_line(line)
        if stripped is not None:
            result.append(stripped)
    return "".join(result)
