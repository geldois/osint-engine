from __future__ import annotations

import importlib.util
import os
import re
import time
import uuid
from pathlib import Path

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
_marker_dir = _hook_io._marker_dir


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
    stale_path = _marker_dir() / f"{prefix}-{stale_session}"
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
    entries = [p.name for p in _marker_dir().iterdir() if p.name.startswith(prefix)]
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
