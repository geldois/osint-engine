"""Shared IO for this project's Claude Code hooks (ADR 0025).

Each hook reads the event JSON on stdin and, when it must act, writes a single
Claude Code hook-output object on stdout. Stdlib-only so the hooks run under
``uv run --no-project python`` with no project env, and OS-portable (the marker
directory comes from ``tempfile``, never a hardcoded ``/tmp``).
"""

from __future__ import annotations

import json
import sys
import tempfile
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


def field(event: dict[str, object], key: str) -> str:
    """Return a top-level string field, or ``""`` when absent or non-string."""
    value = event.get(key)
    return value if isinstance(value, str) else ""


def tool_input(event: dict[str, object], key: str) -> str:
    """Return a string field from the nested ``tool_input`` mapping, or ``""``."""
    raw = event.get("tool_input")
    if not isinstance(raw, dict):
        return ""
    value: object = cast("dict[str, object]", raw).get(key)
    return value if isinstance(value, str) else ""


def marker_dir() -> Path:
    """Per-session marker directory, OS-portable (never a hardcoded ``/tmp``)."""
    return Path(tempfile.gettempdir()) / "claude-hooks"


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


def _emit(payload: dict[str, object]) -> None:
    json.dump(payload, sys.stdout)
    sys.stdout.write("\n")
