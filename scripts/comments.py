from __future__ import annotations

import ast
import re
import subprocess
import sys
import tokenize
from io import StringIO
from pathlib import Path
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
_HASH_PRAGMA = re.compile(
    r"^#\s*(?:shellcheck\s+(?:disable|enable|source)=\S+|v\d+(?:\.\d+){1,2})\s*$"
)
_UNSCANNED_SUFFIXES = (".json", ".lock", ".md")
_UNSCANNED_NAMES = frozenset({".python-version", "LICENSE"})
_EXCLUDED_PARTS = frozenset({"generated"})
_MAX_REPORTED = 50


class _Span(NamedTuple):
    start_line: int
    end_line: int


def python_comment_lines(source: str) -> list[int]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    spans = (*_docstring_spans(tree), *_comment_spans(source))
    return sorted({span.start_line for span in spans})


def sql_comment_lines(source: str) -> list[int]:
    lines: list[int] = []
    for line_number, line in enumerate(source.splitlines(), start=1):
        index = _unquoted_index(line, "-", pair=True)
        if index is None:
            continue
        if _SQL_PRAGMA.match(line[index:].strip()):
            continue
        lines.append(line_number)
    return lines


def hash_comment_lines(source: str) -> list[int]:
    lines: list[int] = []
    for line_number, line in enumerate(source.splitlines(), start=1):
        if line_number == 1 and line.startswith("#!"):
            continue
        index = _unquoted_index(line, "#", pair=False)
        if index is None:
            continue
        if _HASH_PRAGMA.match(line[index:].strip()):
            continue
        lines.append(line_number)
    return lines


def comment_lines(rel: str, source: str) -> list[int]:
    if rel.endswith(".py"):
        return python_comment_lines(source)
    if rel.endswith(".sql"):
        return sql_comment_lines(source)
    return hash_comment_lines(source)


def is_scanned(rel: str) -> bool:
    path = Path(rel)
    if _EXCLUDED_PARTS & set(path.parts[:-1]):
        return False
    return path.name not in _UNSCANNED_NAMES and not rel.endswith(_UNSCANNED_SUFFIXES)


def run_comments() -> int:
    tracked = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True, check=True
    ).stdout.splitlines()

    hits: list[str] = []
    for rel in tracked:
        path = Path(rel)
        if not is_scanned(rel) or not path.is_file():
            continue
        try:
            source = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        hits.extend(f"{rel}:{line}" for line in comment_lines(rel, source))

    if not hits:
        return 0

    sys.stderr.write(
        "comments are forbidden everywhere (only linter-ignore pragmas are "
        "allowed); remove each, rename so the code says it, or move the "
        "decision into the docs:\n"
    )
    sys.stderr.write("\n".join(hits[:_MAX_REPORTED]) + "\n")
    if len(hits) > _MAX_REPORTED:
        sys.stderr.write(f"(+{len(hits) - _MAX_REPORTED} more)\n")
    return 1


def _is_shebang(line_number: int, text: str) -> bool:
    return line_number == 1 and text.startswith("#!")


def _is_pragma(text: str) -> bool:
    clauses = [clause.strip() for clause in re.split(r"(?=#)", text) if clause.strip()]
    return bool(clauses) and all(
        _PY_PRAGMA_CLAUSE.fullmatch(clause) for clause in clauses
    )


def _docstring_span(
    container: ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef,
) -> _Span | None:
    if not container.body:
        return None
    first = container.body[0]
    if not (
        isinstance(first, ast.Expr)
        and isinstance(first.value, ast.Constant)
        and isinstance(first.value.value, str)
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


def _comment_spans(source: str) -> list[_Span]:
    spans: list[_Span] = []
    for token in tokenize.generate_tokens(StringIO(source).readline):
        if token.type != tokenize.COMMENT:
            continue
        if _is_shebang(token.start[0], token.string) or _is_pragma(token.string):
            continue
        spans.append(_Span(token.start[0], token.end[0]))
    return spans


def _starts_comment(content: str, index: int, *, pair: bool) -> bool:
    if pair:
        return index + 1 < len(content) and content[index + 1] == content[index]
    return index == 0 or content[index - 1].isspace()


def _unquoted_index(content: str, marker: str, *, pair: bool) -> int | None:
    in_single = in_double = False
    i, n = 0, len(content)
    while i < n:
        char = content[i]
        if in_single:
            if char == "'" and pair and i + 1 < n and content[i + 1] == "'":
                i += 1
            elif char == "'":
                in_single = False
        elif in_double:
            if char == "\\" and not pair:
                i += 1
            else:
                in_double = char != '"'
        elif char == "'":
            in_single = True
        elif char == '"':
            in_double = True
        elif char == marker and _starts_comment(content, i, pair=pair):
            return i
        i += 1
    return None
