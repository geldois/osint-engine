from __future__ import annotations

import subprocess

from scripts._isolation import detached_worktree, sync

_CONFIG = "cosmic-ray.toml"
_SESSION = "build/mutation/session.sqlite"


def run_mutation(*, max_survival: float) -> int:
    with detached_worktree("HEAD") as worktree:
        sync(worktree)
        (worktree / "build" / "mutation").mkdir(parents=True, exist_ok=True)

        steps: tuple[tuple[str, ...], ...] = (
            ("cosmic-ray", "init", _CONFIG, _SESSION),
            ("cosmic-ray", "baseline", _CONFIG),
            ("cosmic-ray", "exec", _CONFIG, _SESSION),
        )
        for step in steps:
            result = subprocess.run(
                ["uv", "run", "--no-sync", *step],
                cwd=worktree,
                check=False,
            )
            if result.returncode != 0:
                return result.returncode

        rate = subprocess.run(
            [
                "uv",
                "run",
                "--no-sync",
                "cr-rate",
                _SESSION,
                "--fail-over",
                str(max_survival),
            ],
            cwd=worktree,
            check=False,
        )

    return rate.returncode
