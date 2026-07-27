from __future__ import annotations

from typer import Typer

from osint_engine.interface.cli.commands.migrate import migrate_down, migrate_up
from osint_engine.interface.cli.commands.refresh_fixtures import (
    refresh_fixtures_command,
)
from osint_engine.interface.cli.commands.serve import serve_command
from osint_engine.interface.cli.commands.wait_db import wait_db_command

typer_app = Typer(no_args_is_help=True)
typer_app.command("serve")(serve_command)
typer_app.command("wait-db")(wait_db_command)
typer_app.command("refresh-fixtures")(refresh_fixtures_command)

typer_migrate_app = Typer(no_args_is_help=True)
typer_migrate_app.command("up")(migrate_up)
typer_migrate_app.command("down")(migrate_down)

typer_app.add_typer(typer_migrate_app, name="migrate")


def main() -> None:
    typer_app()
