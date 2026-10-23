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
_RUMDL = Path(sys.executable).parent / "rumdl"
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
}
_TOOL_INDEX = len(_UV_RUN)
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


def _run_rumdl(tmp_path: Path, markdown: str) -> subprocess.CompletedProcess[str]:
    target = tmp_path / "probe.md"
    target.write_text(markdown, encoding="utf-8")

    return subprocess.run(
        [str(_RUMDL), "check", "--config", str(_PYPROJECT), str(target)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )


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


def test_the_markdown_linter_is_pinned_to_one_exact_version() -> None:
    pins = [spec for spec in _dev_dependencies() if spec.startswith("rumdl")]

    assert len(pins) == 1
    assert re.fullmatch(r"rumdl==\d+\.\d+\.\d+", pins[0])


def test_the_markdown_linter_is_one_of_the_gates() -> None:
    assert "rumdl" in _gate_tools()


def test_line_width_is_left_to_the_formatter(tmp_path: Path) -> None:
    long_line = " ".join(["word"] * _WORDS_PER_LONG_LINE)

    result = _run_rumdl(tmp_path, f"# Title\n\n{long_line}\n")

    assert result.returncode == 0, result.stdout


def test_a_fenced_block_without_a_language_still_fails(tmp_path: Path) -> None:
    result = _run_rumdl(tmp_path, "# Title\n\n```\nx\n```\n")

    assert result.returncode == 1
    assert "MD040" in result.stdout
