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

_SHELL_FILES = (
    ".githooks/pre-commit",
    ".githooks/pre-merge-commit",
    "cloud-init.sh",
    "docker-entrypoint.sh",
)
_WORKFLOW_FILES = (
    ".github/workflows/publish-image.yml",
    ".github/workflows/release.yml",
    ".github/workflows/test.yml",
)
_PRE_SYNC: tuple[Gate, ...] = (
    Gate("lock-check", ("uv", "lock", "--check")),
    Gate("dprint", ("mise", "exec", "--", "dprint", "check")),
    Gate("sqruff", ("mise", "exec", "--", "sqruff", "lint", "migrations", "src")),
    Gate("shellcheck", ("mise", "exec", "--", "shellcheck", *_SHELL_FILES)),
    Gate("shfmt", ("mise", "exec", "--", "shfmt", "-d", *_SHELL_FILES)),
    Gate("actionlint", ("mise", "exec", "--", "actionlint", *_WORKFLOW_FILES)),
)
_ENV_SYNC = Gate("env-sync", ("uv", "sync", "--quiet"))
_POST_SYNC: tuple[Gate, ...] = (
    Gate("ruff-format", (*_UV_RUN, "ruff", "format", "--check", ".")),
    Gate("ruff-check", (*_UV_RUN, "ruff", "check", ".")),
    Gate(
        "import-linter",
        (*_UV_RUN, "lint-imports", "--cache-dir", ".cache/import-linter"),
    ),
    Gate("basedpyright", (*_UV_RUN, "basedpyright")),
)
_SUITE = Gate(
    "pytest",
    (
        *_UV_RUN,
        "pytest",
        "-q",
        "--no-header",
        "--tb=short",
        "--cov",
        "--cov-branch",
        "--cov-report=xml:.cache/coverage/coverage.xml",
    ),
)


def run_check(*, full: bool, staged: bool) -> int:
    mode = f"{'full' if full else 'fast'}{'/staged' if staged else ''}"

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
    env = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    env = {**overlay, **env}
    outcomes = [_run_gate(gate, workdir, env) for gate in _PRE_SYNC]

    sync = _run_gate(_ENV_SYNC, workdir, env)
    outcomes.append(sync)
    if not sync.passed:
        return outcomes

    outcomes.extend(_run_gate(gate, workdir, env) for gate in _POST_SYNC)
    if not full:
        return outcomes

    outcomes.append(_run_gate(_SUITE, workdir, env))

    return outcomes
