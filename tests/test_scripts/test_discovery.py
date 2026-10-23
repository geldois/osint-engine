from __future__ import annotations

from scripts._discovery import tracked


def test_a_tracked_file_is_found() -> None:
    assert tracked("pyproject.toml") == ("pyproject.toml",)


def test_a_path_that_matches_nothing_yields_nothing() -> None:
    assert tracked("no-such-file-anywhere.txt") == ()


def test_a_glob_pathspec_stays_at_its_own_depth() -> None:
    found = tracked(":(glob)*.toml")

    assert "pyproject.toml" in found
    assert all("/" not in path for path in found)


def test_the_result_is_sorted() -> None:
    found = tracked("*.py")

    assert list(found) == sorted(found)
