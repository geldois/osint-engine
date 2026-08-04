from __future__ import annotations

import pytest
from typer.testing import CliRunner

from osint_engine.interface.cli.typer import typer_app


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner()


class TestCLIWiring:
    def test_serve_command_is_registered(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(typer_app.typer_app, ["serve", "--help"])

        assert result.exit_code == 0

    def test_migrate_up_command_is_registered(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(typer_app.typer_app, ["migrate", "up", "--help"])

        assert result.exit_code == 0

    def test_migrate_down_command_is_registered(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(typer_app.typer_app, ["migrate", "down", "--help"])

        assert result.exit_code == 0

    def test_wait_db_command_is_registered(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(typer_app.typer_app, ["wait-db", "--help"])

        assert result.exit_code == 0

    def test_main_invokes_typer_app(self, monkeypatch: pytest.MonkeyPatch) -> None:
        calls: list[None] = []

        def typer_app_call() -> None:
            calls.append(None)

        monkeypatch.setattr(typer_app, "typer_app", typer_app_call)

        typer_app.main()

        assert calls == [None]
