from __future__ import annotations

import re
import tomllib
from importlib import metadata
from typing import TYPE_CHECKING, cast

from test_scripts.tools import BIN, PYPROJECT, run, write

from scripts.check import _GATES, _UV_RUN  # pyright: ignore[reportPrivateUsage]

if TYPE_CHECKING:
    import subprocess
    from pathlib import Path

_TOOL_INDEX = len(_UV_RUN)
_WIDTH = 120
_WORDS_PER_LONG_LINE = 60


def _dev_dependencies() -> list[str]:
    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    groups = cast("dict[str, list[str]]", project["dependency-groups"])
    return groups["dev"]


def _normalized(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _declared_packages() -> set[str]:
    return {
        _normalized(re.split(r"[<>=!~\[ ]", spec, maxsplit=1)[0])
        for spec in _dev_dependencies()
    }


def _package_installing(tool: str) -> str | None:
    for distribution in metadata.distributions():
        for file in distribution.files or ():
            if file.name == tool and file.parent.name == "bin":
                return _normalized(distribution.metadata["Name"])

    return None


def _gate_tools() -> list[str]:
    return [gate.command[_TOOL_INDEX] for gate in _GATES]


def _rumdl(command: str, target: Path) -> subprocess.CompletedProcess[str]:
    return run(
        [str(BIN / "rumdl"), command, "--config", str(PYPROJECT), str(target)],
        cwd=target.parent,
    )


def _tombi(command: str, *flags: str, target: Path) -> subprocess.CompletedProcess[str]:
    return run(
        [str(BIN / "tombi"), command, "--offline", *flags, str(target)],
        cwd=target.parent,
    )


def test_every_gate_runs_through_the_project_environment() -> None:
    for gate in _GATES:
        assert gate.command[:_TOOL_INDEX] == _UV_RUN, gate.name


def test_every_gate_tool_is_a_declared_dev_dependency() -> None:
    declared = _declared_packages()

    for tool in _gate_tools():
        if tool == "python":
            continue
        owner = _package_installing(tool)
        assert owner is not None, tool
        assert owner in declared, tool


def test_the_gates_whose_tool_keeps_a_cache_never_read_it() -> None:
    cached = {"ruff-format", "ruff-check", "import-linter", "rumdl"}
    gates = {gate.name: gate for gate in _GATES}

    assert cached <= set(gates)
    assert all("--no-cache" in gates[name].command for name in cached)


def test_the_markdown_and_toml_linters_are_gates() -> None:
    tools = _gate_tools()

    assert "rumdl" in tools
    assert tools.count("tombi") == 2


def test_a_line_over_the_width_fails_the_markdown_check(tmp_path: Path) -> None:
    long_line = " ".join(["word"] * _WORDS_PER_LONG_LINE)
    target = write(tmp_path, "probe.md", f"# Title\n\n{long_line}\n")

    result = _rumdl("check", target)

    assert result.returncode == 1
    assert "MD013" in result.stdout


def test_the_markdown_formatter_reflows_a_long_paragraph_to_the_width(
    tmp_path: Path,
) -> None:
    words = ["word"] * _WORDS_PER_LONG_LINE
    target = write(tmp_path, "probe.md", f"# Title\n\n{' '.join(words)}\n")

    formatted = _rumdl("fmt", target)

    lines = target.read_text(encoding="utf-8").splitlines()
    assert formatted.returncode == 0, formatted.stdout
    assert all(len(line) <= _WIDTH for line in lines)
    assert " ".join(lines[2:]).split() == words
    assert _rumdl("check", target).returncode == 0


def test_a_fenced_block_without_a_language_fails(tmp_path: Path) -> None:
    target = write(tmp_path, "probe.md", "# Title\n\n```\nx\n```\n")

    result = _rumdl("check", target)

    assert result.returncode == 1
    assert "MD040" in result.stdout


def test_the_toml_formatter_rewrites_what_the_check_rejects(tmp_path: Path) -> None:
    target = write(tmp_path, "probe.toml", "key   =  1\n")

    assert _tombi("format", "--check", target=target).returncode == 1
    assert _tombi("format", target=target).returncode == 0
    assert target.read_text(encoding="utf-8") == "key = 1\n"
    assert _tombi("format", "--check", target=target).returncode == 0


def test_the_toml_linter_fails_on_tables_out_of_order(tmp_path: Path) -> None:
    target = write(tmp_path, "probe.toml", "[a]\nx = 1\n\n[b]\ny = 1\n\n[a.c]\nz = 1\n")

    result = run(
        [str(BIN / "tombi"), "lint", "--offline", str(target)], cwd=PYPROJECT.parent
    )

    assert result.returncode == 1
    assert "out-of-order" in result.stderr + result.stdout
