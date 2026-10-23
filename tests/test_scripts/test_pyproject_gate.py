from __future__ import annotations

from typing import TYPE_CHECKING

from test_scripts.tools import BIN, ROOT, run, write

if TYPE_CHECKING:
    import subprocess
    from pathlib import Path

_VALID = '[project]\nname = "probe"\nversion = "1"\n'


def _validate(tmp_path: Path, text: str) -> subprocess.CompletedProcess[str]:
    target = write(tmp_path, "pyproject.toml", text)

    return run([str(BIN / "validate-pyproject"), str(target)], cwd=tmp_path)


def test_the_project_manifest_is_valid() -> None:
    result = run(
        [str(BIN / "validate-pyproject"), str(ROOT / "pyproject.toml")], cwd=ROOT
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_a_minimal_manifest_is_valid(tmp_path: Path) -> None:
    result = _validate(tmp_path, _VALID)

    assert result.returncode == 0, result.stdout + result.stderr


def test_a_wrong_type_fails_the_manifest_check(tmp_path: Path) -> None:
    result = _validate(tmp_path, _VALID.replace('"probe"', "1"))

    assert result.returncode != 0


def test_an_unknown_trove_classifier_fails_the_manifest_check(tmp_path: Path) -> None:
    result = _validate(tmp_path, _VALID + 'classifiers = ["Not :: A :: Classifier"]\n')

    assert result.returncode != 0
