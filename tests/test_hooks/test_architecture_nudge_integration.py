from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from uuid import uuid4

_HOOKS_DIR = Path(__file__).resolve().parent.parent.parent / ".claude" / "hooks"
_MARK = _HOOKS_DIR / "mark_architecture_area_touched.py"
_NUDGE = _HOOKS_DIR / "nudge_architecture_docs.py"


def _run_mark(*, file_path: Path, session_id: str, cwd: Path) -> None:
    event = json.dumps(
        {"session_id": session_id, "tool_input": {"file_path": str(file_path)}}
    )
    subprocess.run(
        [sys.executable, str(_MARK)],
        input=event,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=True,
    )


def _run_nudge(*, session_id: str, cwd: Path) -> str:
    event = json.dumps({"session_id": session_id})
    result = subprocess.run(
        [sys.executable, str(_NUDGE)],
        input=event,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


def _cleanup_markers(session_id: str) -> None:
    directory = Path(tempfile.gettempdir()) / "claude-hooks"
    for marker in directory.glob(f"architecture-touched-{session_id}-*"):
        marker.unlink(missing_ok=True)


def test_single_area_touched_fires_one_nudge_naming_it(git_repo: Path) -> None:
    session_id = f"test-{uuid4()}"
    target = git_repo / "src" / "osint_engine" / "domain" / "thing.py"
    target.parent.mkdir(parents=True)
    target.write_text("x = 1\n", encoding="utf-8")

    try:
        _run_mark(file_path=target, session_id=session_id, cwd=git_repo)
        output = _run_nudge(session_id=session_id, cwd=git_repo)

        assert output.strip()
        payload = json.loads(output)
        message = payload["hookSpecificOutput"]["additionalContext"]
        assert "domain" in message
        assert payload["hookSpecificOutput"]["hookEventName"] == "Stop"
    finally:
        _cleanup_markers(session_id)


def test_multiple_areas_same_message_fire_a_single_nudge_naming_both(
    git_repo: Path,
) -> None:
    session_id = f"test-{uuid4()}"
    domain_file = git_repo / "src" / "osint_engine" / "domain" / "thing.py"
    domain_file.parent.mkdir(parents=True)
    domain_file.write_text("x = 1\n", encoding="utf-8")
    interface_file = git_repo / "src" / "osint_engine" / "interface" / "thing.py"
    interface_file.parent.mkdir(parents=True)
    interface_file.write_text("x = 1\n", encoding="utf-8")

    try:
        _run_mark(file_path=domain_file, session_id=session_id, cwd=git_repo)
        _run_mark(file_path=interface_file, session_id=session_id, cwd=git_repo)
        output = _run_nudge(session_id=session_id, cwd=git_repo)

        payload = json.loads(output)
        message = payload["hookSpecificOutput"]["additionalContext"]
        assert "domain" in message
        assert "interface" in message
        assert output.count('"hookEventName"') == 1
    finally:
        _cleanup_markers(session_id)


def test_second_nudge_without_new_edit_does_not_refire(git_repo: Path) -> None:
    session_id = f"test-{uuid4()}"
    target = git_repo / "scripts" / "thing.py"
    target.parent.mkdir(parents=True)
    target.write_text("x = 1\n", encoding="utf-8")

    try:
        _run_mark(file_path=target, session_id=session_id, cwd=git_repo)
        first = _run_nudge(session_id=session_id, cwd=git_repo)
        second = _run_nudge(session_id=session_id, cwd=git_repo)

        assert first.strip()
        assert second.strip() == ""
    finally:
        _cleanup_markers(session_id)


def test_file_outside_any_macro_area_marks_nothing(git_repo: Path) -> None:
    session_id = f"test-{uuid4()}"
    target = git_repo / "README.md"
    target.write_text("# hello\n", encoding="utf-8")

    try:
        _run_mark(file_path=target, session_id=session_id, cwd=git_repo)
        output = _run_nudge(session_id=session_id, cwd=git_repo)

        assert output.strip() == ""
    finally:
        _cleanup_markers(session_id)
