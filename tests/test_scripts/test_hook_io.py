from __future__ import annotations

import importlib.util
import os
import re
import time
import uuid
from pathlib import Path

import pytest

_MODULE_PATH = Path(__file__).parents[2] / ".claude" / "hooks" / "_hook_io.py"
_spec = importlib.util.spec_from_file_location("_hook_io", _MODULE_PATH)
assert _spec is not None
assert _spec.loader is not None
_hook_io = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_hook_io)

session_id = _hook_io.session_id
set_marker = _hook_io.set_marker
take_marker = _hook_io.take_marker
marker_value = _hook_io.marker_value
take_marker_value = _hook_io.take_marker_value
git_root = _hook_io.git_root
command_target_dir = _hook_io.command_target_dir
strip_heredocs = _hook_io.strip_heredocs
stop_reinvoked = _hook_io.stop_reinvoked


@pytest.fixture(autouse=True)
def _isolated_marker_dir(  # pyright: ignore[reportUnusedFunction]
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(_hook_io, "_marker_dir", lambda: tmp_path)


def _unique() -> str:
    return uuid.uuid4().hex


def test_set_then_take_marker_round_trips() -> None:
    session = _unique()
    set_marker("test-prefix", session)
    assert take_marker("test-prefix", session) is True


def test_take_marker_is_single_use() -> None:
    session = _unique()
    set_marker("test-prefix", session)
    assert take_marker("test-prefix", session) is True
    assert take_marker("test-prefix", session) is False


def test_take_marker_never_set_is_false() -> None:
    assert take_marker("test-prefix", _unique()) is False


def test_set_marker_with_no_session_is_noop() -> None:
    set_marker("test-prefix", "")
    assert take_marker("test-prefix", "") is False


def test_take_marker_with_no_session_is_false() -> None:
    assert take_marker("test-prefix", "") is False


def test_markers_are_session_scoped() -> None:
    a, b = _unique(), _unique()
    set_marker("test-prefix", a)
    assert take_marker("test-prefix", b) is False
    assert take_marker("test-prefix", a) is True


def test_session_id_reads_string_field() -> None:
    assert session_id({"session_id": "abc123"}) == "abc123"


def test_session_id_missing_or_wrong_type_is_empty() -> None:
    assert session_id({}) == ""
    assert session_id({"session_id": 42}) == ""


def test_set_marker_sweeps_a_stale_marker_of_the_same_prefix() -> None:
    prefix = f"sweep-{_unique()}"
    stale_session = _unique()
    fresh_session = _unique()

    set_marker(prefix, stale_session)
    stale_path = _hook_io._marker_dir() / f"{prefix}-{stale_session}"
    old = time.time() - 13 * 60 * 60
    os.utime(stale_path, (old, old))

    set_marker(prefix, fresh_session)

    assert not stale_path.exists()
    assert take_marker(prefix, fresh_session) is True


def test_set_marker_leaves_a_fresh_marker_of_the_same_prefix_alone() -> None:
    prefix = f"sweep-{_unique()}"
    session_a = _unique()
    session_b = _unique()

    set_marker(prefix, session_a)
    set_marker(prefix, session_b)

    assert take_marker(prefix, session_a) is True
    assert take_marker(prefix, session_b) is True


def test_costs_exactly_one_nudge_no_matter_how_many_times_set_in_one_turn() -> None:
    session = _unique()
    set_marker("test-prefix", session)
    set_marker("test-prefix", session)
    set_marker("test-prefix", session)
    assert take_marker("test-prefix", session) is True
    assert take_marker("test-prefix", session) is False


def test_sanitizes_a_dangerous_session_value_used_as_a_marker_key() -> None:
    dangerous = "../../etc/passwd"
    set_marker("test-prefix", dangerous)
    prefix = "test-prefix-"
    entries = [
        p.name for p in _hook_io._marker_dir().iterdir() if p.name.startswith(prefix)
    ]
    assert entries == ["test-prefix-" + re.sub(r"[^A-Za-z0-9_-]", "_", dangerous)]
    assert take_marker("test-prefix", dangerous) is True


def test_marker_value_returns_the_stored_value_without_consuming_it() -> None:
    session = _unique()
    set_marker("test-prefix", session, "hello")
    assert marker_value("test-prefix", session) == "hello"
    assert take_marker("test-prefix", session) is True


def test_marker_value_returns_none_when_unset() -> None:
    assert marker_value("test-prefix", _unique()) is None


def test_marker_value_returns_none_when_session_is_empty() -> None:
    assert marker_value("test-prefix", "") is None


def test_marker_value_refreshes_mtime_so_a_read_marker_is_not_swept() -> None:
    prefix = f"sweep-{_unique()}"
    read_session = _unique()
    other_session = _unique()

    set_marker(prefix, read_session, "hello")
    old = time.time() - 13 * 60 * 60
    path = _hook_io._marker_dir() / f"{prefix}-{read_session}"
    os.utime(path, (old, old))

    assert marker_value(prefix, read_session) == "hello"
    set_marker(prefix, other_session)

    assert path.exists()
    assert take_marker(prefix, read_session) is True


def test_take_marker_value_returns_and_deletes() -> None:
    session = _unique()
    set_marker("test-prefix", session, "hello")
    assert take_marker_value("test-prefix", session) == "hello"
    assert take_marker_value("test-prefix", session) is None


def test_take_marker_value_returns_none_when_unset() -> None:
    assert take_marker_value("test-prefix", _unique()) is None


def test_take_marker_value_returns_none_when_session_is_empty() -> None:
    assert take_marker_value("test-prefix", "") is None


def test_stop_reinvoked_true_only_for_stop_with_flag() -> None:
    assert stop_reinvoked({"hook_event_name": "Stop", "stop_hook_active": True}) is True
    assert (
        stop_reinvoked({"hook_event_name": "Stop", "stop_hook_active": False}) is False
    )
    assert (
        stop_reinvoked({"hook_event_name": "PreToolUse", "stop_hook_active": True})
        is False
    )
    assert stop_reinvoked({}) is False


def test_strip_heredocs_collapses_a_heredoc_body() -> None:
    command = "cat <<EOF\nsome; body && stuff\nEOF\n"
    assert strip_heredocs(command) == "cat <<EOF\n"


def test_command_target_dir_follows_a_leading_cd(tmp_path: Path) -> None:
    target = tmp_path / "other-repo"
    target.mkdir()
    assert command_target_dir(f"cd {target} && git commit -m x", tmp_path) == target


def test_command_target_dir_resolves_a_relative_cd(tmp_path: Path) -> None:
    (tmp_path / "sub").mkdir()
    assert command_target_dir("cd sub; git status", tmp_path) == tmp_path / "sub"


def test_command_target_dir_defaults_to_base_with_no_leading_cd(tmp_path: Path) -> None:
    assert command_target_dir("git commit -m x", tmp_path) == tmp_path


def test_git_root_resolves_from_start_over_a_stale_env_var(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", "/nonexistent-root-marker")
    assert git_root(git_repo) == git_repo.resolve()


def test_git_root_falls_back_to_project_dir_outside_any_repo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    outside = tmp_path.parent
    assert git_root(outside / "does-not-exist.py") == tmp_path


def test_git_root_returns_none_with_no_repo_and_no_project_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    assert git_root(tmp_path / "does-not-exist.py") is None
