from __future__ import annotations

import ast
import tokenize
from io import StringIO

from hypothesis import given
from hypothesis import strategies as st

from scripts._comments import is_pragma_comment, strip_python

_IDENTIFIER = st.from_regex(r"[a-z][a-z0-9_]{0,8}", fullmatch=True)
_COMMENT_TEXT = st.from_regex(r"[a-zA-Z0-9 _.,!?-]{0,20}", fullmatch=True)
_DOC_TEXT = st.from_regex(r"[a-zA-Z0-9 _.,!?-]{0,20}", fullmatch=True)


def _non_allowlisted_comment_tokens(source: str) -> list[str]:
    tokens = tokenize.generate_tokens(StringIO(source).readline)
    return [
        token.string
        for token in tokens
        if token.type == tokenize.COMMENT
        and not token.string.startswith("#!")
        and not is_pragma_comment(token.string)
    ]


@given(
    name=_IDENTIFIER,
    docstring=_DOC_TEXT,
    comment=_COMMENT_TEXT,
    has_body_statement=st.booleans(),
    has_leading_comment=st.booleans(),
)
def test_stripped_python_always_reparses_with_no_stray_comments(
    name: str,
    docstring: str,
    comment: str,
    *,
    has_body_statement: bool,
    has_leading_comment: bool,
) -> None:
    lines = [f"def {name}():"]
    if has_leading_comment:
        lines.insert(0, f"# {comment}")
    lines.append(f'    """{docstring}"""  # {comment}')
    if has_body_statement:
        lines.append(f"    {name} = 1  # {comment}")
    source = "\n".join(lines) + "\n"

    ast.parse(source)

    stripped = strip_python(source)

    ast.parse(stripped)
    assert not _non_allowlisted_comment_tokens(stripped)


@given(
    name=_IDENTIFIER,
    docstring=_DOC_TEXT,
)
def test_stripped_sole_docstring_function_still_parses(
    name: str, docstring: str
) -> None:
    source = f'def {name}():\n    """{docstring}"""\n'

    stripped = strip_python(source)

    tree = ast.parse(stripped)
    function = tree.body[0]
    assert isinstance(function, ast.FunctionDef)
    assert ast.get_docstring(function) is None
