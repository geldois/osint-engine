"""Shared IO for this project's Claude Code hooks.

Each hook reads the event JSON on stdin and, when it must act, writes a single
Claude Code hook-output object on stdout. Stdlib-only so the hooks run under
``uv run --no-project python`` with no project env, and OS-portable.

No hook here ever writes to a file the model may hold in context: a rewrite
leaves that copy silently wrong and forces a full re-read on the next edit.
Fixers belong in the pre-commit ``fix`` step, which runs once.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import cast


def read_event() -> dict[str, object]:
    """Parse the hook event from stdin; an unreadable payload is an empty event."""
    try:
        raw: object = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return {}
    # ``isinstance`` narrows only to ``dict[Unknown, Unknown]``; the cast pins the
    # JSON-object shape so the value stays fully typed even under strict-plus modes.
    return cast("dict[str, object]", raw) if isinstance(raw, dict) else {}


def tool_input(event: dict[str, object], key: str) -> str:
    """Return a string field from the nested ``tool_input`` mapping, or ``""``."""
    raw = event.get("tool_input")
    if not isinstance(raw, dict):
        return ""
    value: object = cast("dict[str, object]", raw).get(key)
    return value if isinstance(value, str) else ""


def run(
    command: list[str], cwd: Path | None = None
) -> subprocess.CompletedProcess[str] | None:
    """Run a command, capturing output; ``None`` when the executable is absent.

    A hook must never break the session because a tool is missing from PATH —
    an unactivated version manager degrades the report to silence, not to a
    traceback. The commit gate is where a missing tool is a hard failure.
    """
    try:
        return subprocess.run(
            command, cwd=cwd, capture_output=True, text=True, check=False
        )
    except (FileNotFoundError, OSError):
        return None


def git_root(start: Path) -> Path | None:
    """Repo root for ``start`` (a file or directory), or ``None`` outside a repo.

    Checks ``CLAUDE_PROJECT_DIR`` first — every hook already runs with it set,
    so this avoids a subprocess in the common case; ``git rev-parse`` is the
    fallback for direct invocation (e.g. a test harness) with no such env.
    """
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if project_dir:
        return Path(project_dir)

    cwd = start if start.is_dir() else start.parent
    result = run(["git", "rev-parse", "--show-toplevel"], cwd)
    if result is None or result.returncode != 0:
        return None
    return Path(result.stdout.strip())


def deny(reason: str) -> None:
    """Emit a ``PreToolUse`` deny decision with the given reason."""
    _emit(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            },
        },
    )


def add_context(context: str) -> None:
    """Emit a ``PostToolUse`` additionalContext payload."""
    _emit(
        {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": context,
            },
        },
    )


def context(hook_event_name: str, text: str) -> None:
    """Emit an ``additionalContext`` payload for the given hook event."""
    _emit(
        {
            "hookSpecificOutput": {
                "hookEventName": hook_event_name,
                "additionalContext": text,
            },
        },
    )


def _emit(payload: dict[str, object]) -> None:
    json.dump(payload, sys.stdout)
    sys.stdout.write("\n")
