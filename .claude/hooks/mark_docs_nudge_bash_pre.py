from __future__ import annotations

import sys
from pathlib import Path

from _docs_nudge import path_mtimes, porcelain_paths, serialize_mtimes
from _hook_io import git_root, read_event, run, session_id, set_marker, take_marker


def main() -> int:
    root = git_root(Path.cwd())
    if root is None:
        return 0

    session = session_id(read_event())
    status = run(["git", "status", "--porcelain", "-z", "--untracked-files=all"], root)
    if status is None or status.returncode != 0:
        take_marker("bash-pre-state", session)
        return 0

    mtimes = path_mtimes(root, porcelain_paths(status.stdout))
    set_marker("bash-pre-state", session, serialize_mtimes(mtimes))

    return 0


if __name__ == "__main__":
    sys.exit(main())
