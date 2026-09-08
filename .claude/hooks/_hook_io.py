from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import time
from contextlib import suppress
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


def project_root() -> Path | None:
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    return Path(project_dir) if project_dir else None


def git_root(start: Path) -> Path | None:
    cwd = start if start.is_dir() else start.parent
    result = run(["git", "rev-parse", "--show-toplevel"], cwd)
    if result is not None and result.returncode == 0:
        return Path(result.stdout.strip())

    return project_root()


def contained_rel(path: Path, root: Path) -> str | None:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return None


_LEADING_CD = re.compile(r"^\s*cd\s+(\S+)\s*(?:&&|;)\s*")


def command_target_dir(command: str, base: Path) -> Path:
    match = _LEADING_CD.match(command)
    if not match:
        return base
    target = Path(match.group(1).strip("'\""))
    return target if target.is_absolute() else base / target


_HEREDOC = re.compile(r"<<-?(['\"]?)(\w+)\1\n.*?\n\s*\2(?=\s|$)", re.DOTALL)


def strip_heredocs(command: str) -> str:
    return _HEREDOC.sub(lambda m: f"<<{m.group(2)}", command)


def session_id(event: dict[str, object]) -> str:
    value = event.get("session_id")
    return value if isinstance(value, str) else ""


_MARKER_STALE_SECONDS = 12 * 60 * 60


def set_marker(prefix: str, session: str, value: str = "") -> None:
    if not session:
        return
    try:
        directory = _marker_dir()
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        safe_prefix = _safe_marker(prefix)
        _sweep_stale_markers(directory, safe_prefix)
        (directory / f"{safe_prefix}-{_safe_marker(session)}").write_text(value)
    except OSError:
        return


def take_marker(prefix: str, session: str) -> bool:
    if not session:
        return False
    try:
        (_marker_dir() / f"{_safe_marker(prefix)}-{_safe_marker(session)}").unlink()
    except OSError:
        return False
    return True


def marker_value(prefix: str, session: str) -> str | None:
    if not session:
        return None
    path = _marker_dir() / f"{_safe_marker(prefix)}-{_safe_marker(session)}"
    try:
        value = path.read_text()
    except OSError:
        return None
    with suppress(OSError):
        os.utime(path)
    return value


def take_marker_value(prefix: str, session: str) -> str | None:
    if not session:
        return None
    path = _marker_dir() / f"{_safe_marker(prefix)}-{_safe_marker(session)}"
    try:
        value = path.read_text()
    except OSError:
        return None
    path.unlink(missing_ok=True)
    return value


def _marker_dir() -> Path:
    return Path(tempfile.gettempdir()) / "osint-engine-claude-hooks"


def _safe_marker(prefix: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "_", prefix)


def _sweep_stale_markers(directory: Path, prefix: str) -> None:
    cutoff = time.time() - _MARKER_STALE_SECONDS
    for marker in directory.glob(f"{prefix}-*"):
        try:
            if marker.stat().st_mtime < cutoff:
                marker.unlink(missing_ok=True)
        except OSError:
            continue


def stop_reinvoked(event: dict[str, object]) -> bool:
    return (
        event.get("hook_event_name") == "Stop" and event.get("stop_hook_active") is True
    )


def context(hook_event_name: str, text: str) -> None:
    if stop_reinvoked(read_event()):
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
