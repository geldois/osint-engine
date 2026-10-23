from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from scripts import fix
from scripts.check import (
    _UV_RUN,  # pyright: ignore[reportPrivateUsage]
    SHELL_FILES,
)

if TYPE_CHECKING:
    import pytest

_TOOL_INDEX = len(_UV_RUN)


def _recorded_commands(monkeypatch: pytest.MonkeyPatch) -> list[list[str]]:
    commands: list[list[str]] = []

    def record(command: list[str], *, check: bool) -> subprocess.CompletedProcess[str]:
        assert check is False
        commands.append(command)

        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(fix.subprocess, "run", record)

    return commands


def test_every_fixer_runs_through_the_project_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    commands = _recorded_commands(monkeypatch)

    assert fix.run_fix() == 0

    assert commands
    assert all(command[:_TOOL_INDEX] == list(_UV_RUN) for command in commands)


def test_the_fixers_run_in_order_and_each_document_type_has_its_own(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    commands = _recorded_commands(monkeypatch)

    fix.run_fix()

    assert [command[_TOOL_INDEX:] for command in commands] == [
        ["ruff", "check", "--fix", "."],
        ["ruff", "format", "."],
        ["rumdl", "fmt", "--quiet", "."],
        ["tombi", "format", "--offline", "--quiet"],
        ["dprint", "fmt"],
        ["sqruff", "fix", "migrations", "src"],
        ["shfmt", "-w", *SHELL_FILES],
    ]
