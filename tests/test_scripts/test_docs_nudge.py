from __future__ import annotations

import importlib.util
from pathlib import Path

_MODULE_PATH = Path(__file__).parents[2] / ".claude" / "hooks" / "_docs_nudge.py"
_spec = importlib.util.spec_from_file_location("_docs_nudge", _MODULE_PATH)
assert _spec is not None
assert _spec.loader is not None
_docs_nudge = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_docs_nudge)

is_relevant_change = _docs_nudge.is_relevant_change
docs_nudge_text = _docs_nudge.docs_nudge_text
porcelain_paths = _docs_nudge.porcelain_paths
mtime_of = _docs_nudge.mtime_of
path_mtimes = _docs_nudge.path_mtimes
serialize_mtimes = _docs_nudge.serialize_mtimes
parse_mtimes = _docs_nudge.parse_mtimes
changed_paths = _docs_nudge.changed_paths


def test_excludes_docs_dir() -> None:
    assert is_relevant_change("docs/architecture/tooling.md") is False


def test_excludes_named_root_docs_and_lockfile() -> None:
    for rel in (
        "README.md",
        "TO-DO.md",
        "CLAUDE.md",
        "CONTEXT.md",
        "CHANGELOG.md",
        "uv.lock",
    ):
        assert is_relevant_change(rel) is False


def test_excludes_generated_and_vendor_prefixes() -> None:
    generated = "src/osint_engine/infrastructure/persistence/pg/generated/models.py"
    assert is_relevant_change(generated) is False
    assert is_relevant_change(".venv/lib/foo.py") is False
    assert is_relevant_change("__pycache__/foo.pyc") is False
    assert is_relevant_change(".cache/eslint/foo") is False
    assert is_relevant_change("build/out.py") is False


def test_includes_root_config_file() -> None:
    assert is_relevant_change("pyproject.toml") is True
    assert is_relevant_change("dprint.json") is True
    assert is_relevant_change(".mise.toml") is True


def test_includes_application_source() -> None:
    assert is_relevant_change("src/osint_engine/domain/foo.py") is True


def test_docs_nudge_text_lists_areas() -> None:
    text = docs_nudge_text(["config", "harness", "tests"])
    assert "(existing: config, harness, tests)" in text


def test_docs_nudge_text_omits_parenthetical_when_empty() -> None:
    text = docs_nudge_text([])
    assert "(existing:" not in text


def test_porcelain_paths_extracts_a_modified_path() -> None:
    assert porcelain_paths(" M pyproject.toml\0") == ["pyproject.toml"]


def test_porcelain_paths_extracts_an_untracked_path() -> None:
    assert porcelain_paths("?? new_file.py\0") == ["new_file.py"]


def test_porcelain_paths_extracts_only_the_destination_of_a_rename() -> None:
    assert porcelain_paths("R  new_name.py\0old_name.py\0") == ["new_name.py"]


def test_porcelain_paths_includes_a_deleted_path() -> None:
    assert porcelain_paths(" D removed.py\0") == ["removed.py"]


def test_porcelain_paths_returns_nothing_for_a_clean_tree() -> None:
    assert porcelain_paths("") == []


def test_porcelain_paths_passes_an_unusual_filename_through_verbatim() -> None:
    assert porcelain_paths(" M src/atualização.py\0") == ["src/atualização.py"]


def test_porcelain_paths_extracts_multiple_entries() -> None:
    assert porcelain_paths(" M a.py\0?? b.py\0") == ["a.py", "b.py"]


def test_serialize_then_parse_mtimes_round_trips() -> None:
    mtimes = {"a.py": 111.0, "b.py": 222.0}
    assert parse_mtimes(serialize_mtimes(mtimes)) == mtimes


def test_parse_mtimes_empty_string_is_empty_dict() -> None:
    assert parse_mtimes("") == {}


def test_serialize_then_parse_mtimes_round_trips_a_newline_in_a_path() -> None:
    mtimes = {"weird\nname.py": 111.0}
    assert parse_mtimes(serialize_mtimes(mtimes)) == mtimes


def test_changed_paths_does_not_report_an_unchanged_mtime() -> None:
    current = {"src/foo.py": 100.0}
    previous = {"src/foo.py": 100.0}
    assert changed_paths(current, previous) == []


def test_changed_paths_reports_a_different_mtime_even_if_already_dirty() -> None:
    current = {"src/foo.py": 200.0}
    previous = {"src/foo.py": 100.0}
    assert changed_paths(current, previous) == ["src/foo.py"]


def test_changed_paths_reports_a_path_absent_from_previous() -> None:
    current = {"src/foo.py": 100.0}
    previous: dict[str, float] = {}
    assert changed_paths(current, previous) == ["src/foo.py"]


def test_changed_paths_does_not_resurrect_an_unrelated_dirty_path() -> None:
    current = {"src/foo.py": 100.0, "README.md": 200.0}
    previous = {"src/foo.py": 100.0, "README.md": 100.0}
    assert changed_paths(current, previous) == ["README.md"]


def test_changed_paths_reports_a_path_gone_from_current_entirely() -> None:
    current: dict[str, float] = {}
    previous = {"src/foo.py": 100.0}
    assert changed_paths(current, previous) == ["src/foo.py"]


def test_mtime_of_returns_a_real_files_mtime(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("content")
    assert mtime_of(tmp_path, "a.py") > 0


def test_mtime_of_returns_minus_one_for_a_missing_path(tmp_path: Path) -> None:
    assert mtime_of(tmp_path, "missing.py") == -1.0


def test_path_mtimes_maps_every_given_path(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("content")
    mtimes = path_mtimes(tmp_path, ["a.py", "missing.py"])
    assert mtimes["a.py"] > 0
    assert mtimes["missing.py"] == -1.0
