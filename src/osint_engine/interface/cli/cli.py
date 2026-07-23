from __future__ import annotations

from typer import Typer

from osint_engine.interface.cli.commands.migrate import migrate_down, migrate_up
from osint_engine.interface.cli.commands.serve import serve_command

typer_app = Typer(no_args_is_help=True)

migrate_app = Typer(no_args_is_help=True)

typer_app.add_typer(migrate_app, name="migrate")

typer_app.command("serve")(serve_command)

migrate_app.command("up")(migrate_up)
migrate_app.command("down")(migrate_down)


def main() -> None:
    typer_app()
