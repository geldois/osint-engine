from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

from scripts._report import Gate, GateOutcome, print_header, print_verdict

_UV_RUN = ("uv", "run", "--no-sync")
_ACTIONLINT_IMAGE = "rhysd/actionlint:1.7.12"

SHELL_FILES = (
    ".githooks/pre-commit",
    "cloud-init.sh",
    "docker-entrypoint.sh",
)
WORKFLOW_FILES = (
    ".github/workflows/publish-image.yml",
    ".github/workflows/release.yml",
    ".github/workflows/test.yml",
)
_LOCK_CHECK = Gate("lock-check", ("uv", "lock", "--check", "--quiet"))
_ENV_SYNC = Gate("env-sync", ("uv", "sync", "--quiet"))
_GATES: tuple[Gate, ...] = (
    Gate("comments", (*_UV_RUN, "python", "-m", "scripts", "comments")),
    Gate("ruff-format", (*_UV_RUN, "ruff", "format", "--check", "--quiet", ".")),
    Gate(
        "ruff-check",
        (*_UV_RUN, "ruff", "check", "--output-format", "concise", "--quiet", "."),
    ),
    Gate(
        "import-linter",
        (*_UV_RUN, "lint-imports", "--cache-dir", ".cache/import-linter"),
    ),
    Gate("basedpyright", (*_UV_RUN, "basedpyright")),
    Gate("dprint", (*_UV_RUN, "dprint", "check")),
    Gate("sqruff", (*_UV_RUN, "sqruff", "lint", "migrations", "src")),
    Gate("shellcheck", (*_UV_RUN, "shellcheck", "--format=gcc", *SHELL_FILES)),
    Gate("shfmt", (*_UV_RUN, "shfmt", "-d", *SHELL_FILES)),
    Gate(
        "actionlint",
        (
            "docker",
            "run",
            "--rm",
            "--volume",
            f"{Path.cwd()}:/repo:ro",
            "--workdir",
            "/repo",
            _ACTIONLINT_IMAGE,
            *WORKFLOW_FILES,
        ),
    ),
    Gate(
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
    ),
)


def run_check() -> int:
    sys.stderr.write("running quality gates…\n")
    outcomes = _run_sequence(Path.cwd())
    print_verdict(outcomes)

    return 0 if all(o.passed for o in outcomes) else 1


def _run_gate(gate: Gate, cwd: Path, env: dict[str, str]) -> GateOutcome:
    print_header(gate.name)
    start = time.monotonic()
    try:
        result = subprocess.run(gate.command, cwd=cwd, env=env, check=False)
    except FileNotFoundError:
        sys.stderr.write(
            f"{gate.command[0]} not found — required tool missing from the "
            f"environment; install it so this gate can run\n"
        )
        return GateOutcome(
            name=gate.name, passed=False, duration_s=time.monotonic() - start
        )

    return GateOutcome(
        name=gate.name,
        passed=result.returncode == 0,
        duration_s=time.monotonic() - start,
    )


def _run_sequence(workdir: Path) -> list[GateOutcome]:
    env = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    outcomes = [_run_gate(_LOCK_CHECK, workdir, env)]

    sync = _run_gate(_ENV_SYNC, workdir, env)
    outcomes.append(sync)
    if not sync.passed:
        return outcomes

    outcomes.extend(_run_gate(gate, workdir, env) for gate in _GATES)

    return outcomes
