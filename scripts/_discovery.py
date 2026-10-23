from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def tracked(*pathspecs: str) -> tuple[str, ...]:
    listed = subprocess.run(
        ["git", "ls-files", "--", *pathspecs],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    return tuple(sorted(listed.stdout.splitlines()))
