"""The deterministic gate sequence and its orchestrator (ADR 0025).

``check`` runs the fast gates; ``check --full`` adds the pytest suite with
branch coverage. ``--staged`` materialises the git index into an isolated,
freshly-synced snapshot and runs the gates there (the pre-commit / pre-merge
path); without it the gates run in the current directory (CI, manual runs).

Ordering is fixed: gates that need no virtualenv (``lock-check``, ``dprint``,
``sqruff``) run against the pristine snapshot *before* ``env-sync`` can rewrite
its lockfile or add a ``.venv``, then the environment is built, then the
import/type/test gates run against it.
"""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

from dotenv import dotenv_values

from scripts._isolation import materialized_snapshot
from scripts._report import (
    Gate,
    GateOutcome,
    print_verdict,
    running_ticker,
    write_report,
)

_UV_RUN = ("uv", "run", "--no-sync")

# No virtualenv required — run against the pristine snapshot before env-sync.
_PRE_SYNC: tuple[Gate, ...] = (
    Gate("lock-check", ("uv", "lock", "--check")),
    # Deterministic markdown formatter as a gate: `dprint check` fails if any
    # canonical doc is not in its canonical 120-col form. Scope/config in
    # dprint.json; the per-edit hook runs `dprint fmt` so this is born green.
    Gate("dprint", ("mise", "exec", "--", "dprint", "check")),
    # Deterministic SQL linter/formatter (Rust, sqlfluff-compatible). Postgres
    # dialect with the colon-placeholder templater so `:name` bind params are
    # not misread as operators; config in .sqruff. The per-edit hook runs
    # `sqruff fix` so committed migrations/queries are born green.
    Gate("sqruff", ("mise", "exec", "--", "sqruff", "lint", "migrations", "src")),
)
_ENV_SYNC = Gate("env-sync", ("uv", "sync", "--quiet"))
# Need the snapshot's own venv (editable on the snapshot source).
_POST_SYNC: tuple[Gate, ...] = (
    Gate("ruff-format", (*_UV_RUN, "ruff", "format", "--check", ".")),
    Gate("ruff-check", (*_UV_RUN, "ruff", "check", ".")),
    Gate("import-linter", (*_UV_RUN, "lint-imports")),
    Gate("basedpyright", (*_UV_RUN, "basedpyright")),
)
_SUITE = Gate(
    "pytest",
    # -q --no-header --tb=short keep the captured output lean so a failure surfaces
    # the FAILURES block (file:line, assertion, values) without the verbose
    # per-test chatter — gate-scoped, so a dev's manual `pytest path::test` still
    # gets full tracebacks. Runner discards this entirely on success.
    (
        *_UV_RUN,
        "pytest",
        "-q",
        "--no-header",
        "--tb=short",
        "--cov",
        "--cov-branch",
        "--cov-report=xml",
    ),
)


def run_check(*, full: bool, staged: bool) -> int:
    """Run the gate sequence, write the report, print the verdict, return exit code."""
    mode = f"{'full' if full else 'fast'}{'/staged' if staged else ''}"

    # Read the local .env from the real project root before entering any snapshot,
    # so the full suite self-provisions its secrets (Portal key, DB URL) with no
    # manual sourcing. Local-only: the materialised snapshot excludes the
    # gitignored .env, and CI has no .env (it uses repo secrets), so this is a
    # no-op there. Never committed, never printed.
    overlay = _dotenv_overlay(Path.cwd())

    with running_ticker():
        if staged:
            with materialized_snapshot() as workdir:
                outcomes = _run_sequence(workdir, full=full, overlay=overlay)
        else:
            outcomes = _run_sequence(Path.cwd(), full=full, overlay=overlay)

    report_path = write_report(outcomes, mode=mode)
    print_verdict(outcomes, report_path)

    return 0 if all(o.passed for o in outcomes) else 1


def _dotenv_overlay(project_root: Path) -> dict[str, str]:
    """Local ``.env`` values as an env overlay, or empty when the file is absent."""
    env_file = project_root / ".env"
    if not env_file.is_file():
        return {}
    return {key: value for key, value in dotenv_values(env_file).items() if value}


def _run_gate(gate: Gate, cwd: Path, env: dict[str, str]) -> GateOutcome:
    start = time.monotonic()
    try:
        result = subprocess.run(
            gate.command,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        # A missing tool is a failure, never a skip: the environment is not set up
        # to enforce this gate, so no commit may pass it. Forces a correct setup.
        return GateOutcome(
            name=gate.name,
            passed=False,
            duration_s=time.monotonic() - start,
            output=(
                f"{gate.command[0]} not found — required tool missing from the "
                f"environment; install it so this gate can run"
            ),
        )

    return GateOutcome(
        name=gate.name,
        passed=result.returncode == 0,
        duration_s=time.monotonic() - start,
        output=(result.stdout or "") + (result.stderr or ""),
    )


def _run_sequence(
    workdir: Path, *, full: bool, overlay: dict[str, str]
) -> list[GateOutcome]:
    # Scrub git's hook-injected env (GIT_DIR, GIT_INDEX_FILE, GIT_WORK_TREE, …):
    # when the gates run from inside the pre-commit hook these point at the real
    # repo and leak into every gate subprocess, breaking any test that shells out
    # to git (it would resolve `.git` against the snapshot dir). The snapshot was
    # already materialised before this point, so the gates need no git context.
    env = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    # Overlay the local .env last so it fills secrets the snapshot lacks without
    # clobbering an already-exported value (an explicit shell export still wins).
    env = {**overlay, **env}
    outcomes = [_run_gate(gate, workdir, env) for gate in _PRE_SYNC]

    sync = _run_gate(_ENV_SYNC, workdir, env)
    outcomes.append(sync)
    if not sync.passed:
        # The environment could not be built — downstream gates literally cannot
        # run. Fail fast on env-sync rather than emit skips for the rest.
        return outcomes

    post = (*_POST_SYNC, _SUITE) if full else _POST_SYNC
    outcomes.extend(_run_gate(gate, workdir, env) for gate in post)

    return outcomes
