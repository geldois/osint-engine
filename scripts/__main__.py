from __future__ import annotations

import typer

from scripts import fixtures
from scripts.check import run_check
from scripts.comments import run_comments
from scripts.fix import run_fix
from scripts.mutation import run_mutation
from scripts.sqlc import run_sqlc_generate

app = typer.Typer(no_args_is_help=True, add_completion=False)
fixtures_app = typer.Typer(no_args_is_help=True, add_completion=False)
app.add_typer(fixtures_app, name="fixtures")

_DEFAULT_MAX_SURVIVAL = 100.0


@app.command(help="Run every gate on the working tree, tests included.")
def check() -> None:
    raise typer.Exit(run_check())


@app.command(help="Apply every safe, idempotent auto-fixer to the whole repo.")
def fix() -> None:
    raise typer.Exit(run_fix())


@app.command(help="Fail on any comment or docstring outside a linter pragma.")
def comments() -> None:
    raise typer.Exit(run_comments())


@app.command(help="Run the cosmic-ray mutation gate (periodic; never a hook).")
def mutation(*, max_survival: float = _DEFAULT_MAX_SURVIVAL) -> None:
    raise typer.Exit(run_mutation(max_survival=max_survival))


@app.command(
    "sqlc-generate",
    help="Regenerate sqlc models, discarding the unused generated querier.",
)
def sqlc_generate() -> None:
    raise typer.Exit(run_sqlc_generate())


@fixtures_app.command("refresh", help="Regenerate live-API golden snapshots.")
def fixtures_refresh() -> None:
    fixtures.main()


@fixtures_app.command(
    "verify",
    help=(
        "Refresh live-API snapshots, then run the real_api_snapshot contract "
        "tests (periodic; never a hook)."
    ),
)
def fixtures_verify() -> None:
    raise typer.Exit(fixtures.run_verify())


if __name__ == "__main__":
    app()
