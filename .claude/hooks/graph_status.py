"""Print code-review-graph status at session start — ``SessionStart``.

No-op unless the repo has an initialized ``.code-review-graph``. Uses the
project-installed CLI via ``uv run --no-sync`` (the hook runs under
``--no-project``; the inner call re-resolves the project env).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from _hook_io import read_event


def main() -> int:
    """Show graph status for the current repo when it has a graph."""
    read_event()  # consume stdin so the hook never blocks on it
    root = _git_root()
    if root is None or not (root / ".code-review-graph").is_dir():
        return 0

    subprocess.run(
        ["uv", "run", "--no-sync", "code-review-graph", "status", "--repo", str(root)],
        cwd=root,
        check=False,
    )
    return 0


def _git_root() -> Path | None:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    root = result.stdout.strip()
    return Path(root) if root else None


if __name__ == "__main__":
    sys.exit(main())
