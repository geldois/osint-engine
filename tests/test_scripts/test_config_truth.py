from __future__ import annotations

import configparser
import fnmatch
import json
import re
import subprocess
import tomllib
from pathlib import Path
from typing import cast

from test_scripts.tools import ROOT

_BRACES = re.compile(r"\{([^{}]*)\}")
_DOC_TYPES = "*.{json,md,toml,yaml,yml}"
_EDITOR_DIRECTORIES = {".idea", ".vscode", ".zed"}


def _expand(pattern: str) -> list[str]:
    match = _BRACES.search(pattern)
    if match is None:
        return [pattern]
    head, tail = pattern[: match.start()], pattern[match.end() :]

    return [
        expanded
        for option in match.group(1).split(",")
        for expanded in _expand(head + option + tail)
    ]


def _editorconfig() -> dict[str, dict[str, str]]:
    parser = configparser.ConfigParser(interpolation=None)
    parser.read_string(
        "[__root__]\n" + (ROOT / ".editorconfig").read_text(encoding="utf-8")
    )

    return {
        name: dict(parser[name]) for name in parser.sections() if name != "__root__"
    }


def _tracked() -> list[str]:
    listed = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    return listed.stdout.splitlines()


def _pyproject() -> object:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def _dprint() -> object:
    return json.loads((ROOT / "dprint.json").read_text(encoding="utf-8"))


def _get(data: object, *keys: str) -> object:
    for key in keys:
        data = cast("dict[str, object]", data)[key]

    return data


def test_every_editorconfig_section_matches_a_tracked_file() -> None:
    names = {Path(path).name for path in _tracked()}

    for section in _editorconfig():
        patterns = _expand(section)
        assert any(
            fnmatch.fnmatch(name, pattern) for name in names for pattern in patterns
        ), section


def test_python_line_width_has_one_value() -> None:
    mirrored = _editorconfig()["*.py"]["max_line_length"]

    assert mirrored == str(_get(_pyproject(), "tool", "ruff", "line-length"))


def test_sql_line_width_has_one_value() -> None:
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(ROOT / ".sqruff", encoding="utf-8")

    mirrored = _editorconfig()["*.sql"]["max_line_length"]

    assert mirrored == parser["sqruff"]["max_line_length"]


def test_document_line_width_has_one_value() -> None:
    mirrored = _editorconfig()[_DOC_TYPES]["max_line_length"]
    owners = {
        "rumdl": _get(_pyproject(), "tool", "rumdl", "line-length"),
        "tombi": _get(_pyproject(), "tool", "tombi", "format", "rules", "line-width"),
        "dprint": _get(_dprint(), "lineWidth"),
    }

    for owner, value in owners.items():
        assert str(value) == mirrored, owner


def test_document_indent_has_one_value() -> None:
    mirrored = _editorconfig()[_DOC_TYPES]["indent_size"]
    owners = {
        "tombi": _get(_pyproject(), "tool", "tombi", "format", "rules", "indent-width"),
        "dprint": _get(_dprint(), "indentWidth"),
    }

    for owner, value in owners.items():
        assert str(value) == mirrored, owner


def test_line_ending_has_one_value() -> None:
    mirrored = _editorconfig()["*"]["end_of_line"]

    assert _get(_dprint(), "newLineKind") == mirrored


def test_no_editor_specific_file_is_tracked() -> None:
    for path in _tracked():
        assert path.split("/")[0] not in _EDITOR_DIRECTORIES, path
        assert not Path(path).name.startswith(".markdownlint"), path
