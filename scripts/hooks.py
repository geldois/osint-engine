from __future__ import annotations

import stat
import subprocess
import sys
from pathlib import Path

_SENTINEL = "# managed by osint-engine scripts.hooks (ADR 0025)"

_HOOKS: dict[str, str] = {
    "pre-commit": "uv run python -m scripts precommit",
    "pre-merge-commit": "uv run python -m scripts check --staged --full",
    "post-commit": "uv run --no-sync code-review-graph update",
}


class NotAGitRepositoryError(RuntimeError):
    pass


def install() -> int:
    hooks_dir = _hooks_dir()
    hooks_dir.mkdir(parents=True, exist_ok=True)

    for name, command in _HOOKS.items():
        _install_one(hooks_dir / name, command)

    return 0


def _hooks_dir() -> Path:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-path", "hooks"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        message = "not a git repository — run inside a repo with a .git directory"
        raise NotAGitRepositoryError(message) from exc

    return Path(result.stdout.strip())


_PREFLIGHT = (
    "command -v uv >/dev/null 2>&1 || { echo \"osint-engine: 'uv' not found on "
    "PATH — install uv and activate mise (see README: Setup), or bypass once "
    "with 'git commit --no-verify'.\" >&2; exit 1; }"
)


def _install_one(path: Path, command: str) -> None:
    content = f"#!/bin/sh\n{_SENTINEL}\n{_PREFLIGHT}\nexec {command}\n"

    if path.exists() and _SENTINEL not in path.read_text(encoding="utf-8"):
        sys.stderr.write(f"  {path.name:<18}skip    foreign hook, not overwritten\n")
        return

    if path.exists() and path.read_text(encoding="utf-8") == content:
        sys.stderr.write(f"  {path.name:<18}ok      unchanged\n")
        return

    path.write_text(content, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    sys.stderr.write(f"  {path.name:<18}ok      installed\n")
