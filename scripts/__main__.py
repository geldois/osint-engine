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


@app.command()
def check(*, full: bool = False) -> None:
    """Run the deterministic gate sequence."""
    raise typer.Exit(run_check(full=full))


@app.command()
def fix(paths: Annotated[list[str] | None, typer.Argument()] = None) -> None:
    """Apply every safe, idempotent auto-fixer (run before check)."""
    raise typer.Exit(run_fix(tuple(paths or ())))


@app.command()
def precommit() -> None:
    """Fix fully-staged files, re-stage them, then run the full gate."""
    raise typer.Exit(run_precommit())


@app.command()
def mutation(*, max_survival: float = _DEFAULT_MAX_SURVIVAL) -> None:
    """Run the cosmic-ray mutation gate (periodic; never a hook)."""
    raise typer.Exit(run_mutation(max_survival=max_survival))


@app.command("sqlc-generate")
def sqlc_generate() -> None:
    """Regenerate sqlc models, discarding the unused generated querier."""
    raise typer.Exit(run_sqlc_generate())


@fixtures_app.command("refresh")
def fixtures_refresh() -> None:
    """Regenerate live-API golden snapshots."""
    fixtures.main()


@fixtures_app.command("verify")
def fixtures_verify() -> None:
    """Refresh live-API snapshots, then run the real_api_snapshot contract tests (periodic; never a hook)."""  # noqa: E501
    raise typer.Exit(fixtures.run_verify())


if __name__ == "__main__":
    app()
