from __future__ import annotations

import re
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import cast

from scripts.check import _GATES, _UV_RUN  # pyright: ignore[reportPrivateUsage]

_ROOT = Path(__file__).resolve().parents[2]
_PYPROJECT = _ROOT / "pyproject.toml"
_BIN = Path(sys.executable).parent
_PACKAGE_OF_TOOL = {
    "basedpyright": "basedpyright",
    "dprint": "dprint-py",
    "lint-imports": "import-linter",
    "pytest": "pytest",
    "ruff": "ruff",
    "rumdl": "rumdl",
    "shellcheck": "shellcheck-py",
    "shfmt": "shfmt-py",
    "sqruff": "sqruff",
    "tombi": "tombi",
}
_TOOL_INDEX = len(_UV_RUN)
_WIDTH = 120
_WORDS_PER_LONG_LINE = 60


def _dev_dependencies() -> list[str]:
    project = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    groups = cast("dict[str, list[str]]", project["dependency-groups"])
    return groups["dev"]


def _declared_packages() -> set[str]:
    return {
        re.split(r"[<>=!~\[ ]", spec, maxsplit=1)[0] for spec in _dev_dependencies()
    }


def _gate_tools() -> list[str]:
    return [gate.command[_TOOL_INDEX] for gate in _GATES]


def _run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


def _rumdl(command: str, target: Path) -> subprocess.CompletedProcess[str]:
    return _run(
        [str(_BIN / "rumdl"), command, "--config", str(_PYPROJECT), str(target)],
        cwd=target.parent,
    )


def _tombi(command: str, *flags: str, target: Path) -> subprocess.CompletedProcess[str]:
    return _run(
        [str(_BIN / "tombi"), command, "--offline", *flags, str(target)],
        cwd=target.parent,
    )


def _markdown(tmp_path: Path, text: str) -> Path:
    target = tmp_path / "probe.md"
    target.write_text(text, encoding="utf-8")

    return target


def _toml(tmp_path: Path, text: str) -> Path:
    target = tmp_path / "probe.toml"
    target.write_text(text, encoding="utf-8")

    return target


def test_every_gate_runs_through_the_project_environment() -> None:
    for gate in _GATES:
        assert gate.command[:_TOOL_INDEX] == _UV_RUN, gate.name


def test_every_gate_tool_is_a_declared_dev_dependency() -> None:
    declared = _declared_packages()

    for tool in _gate_tools():
        if tool == "python":
            continue
        assert tool in _PACKAGE_OF_TOOL, tool
        assert _PACKAGE_OF_TOOL[tool] in declared, tool


def test_the_document_tools_are_pinned_to_one_exact_version() -> None:
    exact = {
        spec.split("==", maxsplit=1)[0] for spec in _dev_dependencies() if "==" in spec
    }

    assert {"dprint-py", "rumdl", "tombi"} <= exact


def test_the_markdown_and_toml_linters_are_gates() -> None:
    tools = _gate_tools()

    assert "rumdl" in tools
    assert tools.count("tombi") == 2


def test_a_line_over_the_width_fails_the_markdown_check(tmp_path: Path) -> None:
    long_line = " ".join(["word"] * _WORDS_PER_LONG_LINE)
    target = _markdown(tmp_path, f"# Title\n\n{long_line}\n")

    result = _rumdl("check", target)

    assert result.returncode == 1
    assert "MD013" in result.stdout


def test_the_markdown_formatter_reflows_a_long_paragraph_to_the_width(
    tmp_path: Path,
) -> None:
    words = ["word"] * _WORDS_PER_LONG_LINE
    target = _markdown(tmp_path, f"# Title\n\n{' '.join(words)}\n")

    formatted = _rumdl("fmt", target)

    lines = target.read_text(encoding="utf-8").splitlines()
    assert formatted.returncode == 0, formatted.stdout
    assert all(len(line) <= _WIDTH for line in lines)
    assert " ".join(lines[2:]).split() == words
    assert _rumdl("check", target).returncode == 0


def test_a_fenced_block_without_a_language_fails(tmp_path: Path) -> None:
    result = _rumdl("check", _markdown(tmp_path, "# Title\n\n```\nx\n```\n"))

    assert result.returncode == 1
    assert "MD040" in result.stdout


def test_the_toml_formatter_rewrites_what_the_check_rejects(tmp_path: Path) -> None:
    target = _toml(tmp_path, "key   =  1\n")

    assert _tombi("format", "--check", target=target).returncode == 1
    assert _tombi("format", target=target).returncode == 0
    assert target.read_text(encoding="utf-8") == "key = 1\n"
    assert _tombi("format", "--check", target=target).returncode == 0


def test_the_toml_linter_fails_on_tables_out_of_order(tmp_path: Path) -> None:
    target = _toml(tmp_path, "[a]\nx = 1\n\n[b]\ny = 1\n\n[a.c]\nz = 1\n")

    result = _tombi("lint", "--error-on-warnings", target=target)

    assert result.returncode == 1
    assert "out-of-order" in result.stderr + result.stdout
