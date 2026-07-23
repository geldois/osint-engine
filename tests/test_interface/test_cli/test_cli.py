from __future__ import annotations

import pytest
from typer.testing import CliRunner

from osint_engine.interface.cli import cli


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner()


class TestCLIWiring:
    """cli.py only wires commands onto typer_app; per-command behavior is
    covered in test_commands/."""

    def test_serve_command_is_registered(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(cli.typer_app, ["serve", "--help"])

        assert result.exit_code == 0

    def test_migrate_up_command_is_registered(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(cli.typer_app, ["migrate", "up", "--help"])

        assert result.exit_code == 0

    def test_migrate_down_command_is_registered(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(cli.typer_app, ["migrate", "down", "--help"])

        assert result.exit_code == 0

    def test_main_invokes_typer_app(self, monkeypatch: pytest.MonkeyPatch) -> None:
        calls: list[None] = []

        def typer_app_call() -> None:
            calls.append(None)

        monkeypatch.setattr(cli, "typer_app", typer_app_call)

        cli.main()

        assert calls == [None]
