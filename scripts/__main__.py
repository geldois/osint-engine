from __future__ import annotations

from typing import Annotated

import typer

from scripts import fixtures
from scripts.fix import run_fix, run_precommit
from scripts.gates import run_check
from scripts.mutation import run_mutation
from scripts.sqlc import run_sqlc_generate

app = typer.Typer(no_args_is_help=True, add_completion=False)
fixtures_app = typer.Typer(no_args_is_help=True, add_completion=False)
app.add_typer(fixtures_app, name="fixtures")

_DEFAULT_MAX_SURVIVAL = 100.0


@app.command(help="Run the deterministic gate sequence.")
def check(*, full: bool = False) -> None:
    raise typer.Exit(run_check(full=full))


@app.command(help="Apply every safe, idempotent auto-fixer (run before check).")
def fix(paths: Annotated[list[str] | None, typer.Argument()] = None) -> None:
    raise typer.Exit(run_fix(tuple(paths or ())))


@app.command(help="Fix fully-staged files, re-stage them, then run the full gate.")
def precommit() -> None:
    raise typer.Exit(run_precommit())


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
