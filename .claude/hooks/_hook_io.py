from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import cast

_EVENT: list[dict[str, object] | None] = [None]


def read_event() -> dict[str, object]:
    if _EVENT[0] is not None:
        return _EVENT[0]
    try:
        raw: object = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return {}
    _EVENT[0] = cast("dict[str, object]", raw) if isinstance(raw, dict) else {}
    return _EVENT[0]


def tool_input(event: dict[str, object], key: str) -> str:
    raw = event.get("tool_input")
    if not isinstance(raw, dict):
        return ""
    value: object = cast("dict[str, object]", raw).get(key)
    return value if isinstance(value, str) else ""


def tool_response(event: dict[str, object]) -> dict[str, object]:
    raw = event.get("tool_response")
    return cast("dict[str, object]", raw) if isinstance(raw, dict) else {}


def run(
    command: list[str], cwd: Path | None = None
) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            command, cwd=cwd, capture_output=True, text=True, check=False
        )
    except (FileNotFoundError, OSError):
        return None


def git_root(start: Path) -> Path | None:
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if project_dir:
        return Path(project_dir)

    cwd = start if start.is_dir() else start.parent
    result = run(["git", "rev-parse", "--show-toplevel"], cwd)
    if result is None or result.returncode != 0:
        return None
    return Path(result.stdout.strip())


def deny(reason: str) -> None:
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
    _emit(
        {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": context,
            },
        },
    )


def context(hook_event_name: str, text: str, *, once_per_chain: bool = True) -> None:
    if (
        once_per_chain
        and hook_event_name in ("Stop", "SubagentStop")
        and read_event().get("stop_hook_active") is True
    ):
        return
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
