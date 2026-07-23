from __future__ import annotations

from subprocess import CompletedProcess

import pytest
from typer.testing import CliRunner

from osint_engine.config.settings import Settings
from osint_engine.interface.cli import cli
from osint_engine.interface.cli.commands import migrate


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.mark.parametrize("direction", ["up", "down"])
def test_migrate_commands_invoke_golang_migrate(
    direction: str,
    settings: Settings,
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[list[str], bool]] = []

    def from_env(_settings_type: type[Settings]) -> Settings:
        return settings

    def run(command: list[str], *, check: bool) -> CompletedProcess[str]:
        calls.append((command, check))

        return CompletedProcess(args=command, returncode=0)

    monkeypatch.setattr(Settings, "from_env", classmethod(from_env))
    monkeypatch.setattr(migrate.subprocess, "run", run)

    result = cli_runner.invoke(cli.typer_app, ["migrate", direction])

    assert result.exit_code == 0
    assert calls == [
        (
            [
                "migrate",
                "-path",
                "migrations",
                "-database",
                settings.database_url,
                direction,
            ],
            True,
        )
    ]
