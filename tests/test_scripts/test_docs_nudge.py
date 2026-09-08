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


def test_excludes_generated_persistence_prefix() -> None:
    generated = "src/osint_engine/infrastructure/persistence/pg/generated/models.py"
    assert is_relevant_change(generated) is False


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
