from __future__ import annotations

import subprocess

from scripts.gates import SHELL_FILES

_UV_RUN = ("uv", "run", "--no-sync")


def run_fix() -> int:
    _run("ruff", "check", "--fix", ".")
    _run("ruff", "format", ".")
    _run("dprint", "fmt")
    _run("sqruff", "fix", "migrations", "src")
    _run("shfmt", "-w", *SHELL_FILES)

    return 0


def _run(*command: str) -> None:
    subprocess.run([*_UV_RUN, *command], check=False)
