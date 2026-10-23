from __future__ import annotations

from typing import TYPE_CHECKING

from test_scripts.tools import BIN, ROOT, run, write

from scripts.check import COMPOSE_FILES, WORKFLOW_FILES

if TYPE_CHECKING:
    from pathlib import Path

_VALID_COMPOSE = "services:\n  app:\n    image: example\n"
_VALID_WORKFLOW = (
    'name: Probe\n"on": push\njobs:\n  probe:\n    runs-on: ubuntu-24.04\n'
    "    steps:\n      - run: echo ok\n"
)


def _yamllint(target: Path) -> tuple[int, str]:
    result = run(
        [str(BIN / "yamllint"), "--strict", "-c", str(ROOT / ".yamllint"), str(target)],
        cwd=target.parent,
    )

    return result.returncode, result.stdout


def _schema(builtin: str, target: Path) -> tuple[int, str]:
    result = run(
        [str(BIN / "check-jsonschema"), "--builtin-schema", builtin, str(target)],
        cwd=target.parent,
    )

    return result.returncode, result.stdout + result.stderr


def test_the_compose_files_the_gate_checks_are_every_compose_file() -> None:
    found = sorted(
        path.name
        for pattern in ("compose*.y*ml", "docker-compose*.y*ml")
        for path in ROOT.glob(pattern)
    )

    assert sorted(COMPOSE_FILES) == found


def test_the_workflow_files_the_gate_checks_are_every_workflow() -> None:
    found = sorted(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / ".github" / "workflows").glob("*.y*ml")
    )

    assert sorted(WORKFLOW_FILES) == found


def test_a_duplicate_key_fails_the_yaml_linter(tmp_path: Path) -> None:
    code, output = _yamllint(write(tmp_path, "probe.yml", "a: 1\na: 2\n"))

    assert code == 1
    assert "key-duplicates" in output


def test_a_yaml_one_is_not_a_boolean_for_the_linter(tmp_path: Path) -> None:
    code, output = _yamllint(write(tmp_path, "probe.yml", "enabled: yes\n"))

    assert code != 0
    assert "truthy" in output


def test_layout_is_left_to_the_formatter(tmp_path: Path) -> None:
    messy = "a:   1  # note\nlong: " + "x" * 200 + "\nlist:\n- one\n-   two\n"

    code, output = _yamllint(write(tmp_path, "probe.yml", messy))

    assert code == 0, output


def test_a_compose_file_with_an_unknown_key_fails_the_schema(tmp_path: Path) -> None:
    target = write(tmp_path, "compose.yml", _VALID_COMPOSE + "servics: {}\n")

    code, _ = _schema("vendor.compose-spec", target)

    assert code == 1


def test_a_valid_compose_file_passes_the_schema(tmp_path: Path) -> None:
    code, output = _schema(
        "vendor.compose-spec", write(tmp_path, "compose.yml", _VALID_COMPOSE)
    )

    assert code == 0, output


def test_a_workflow_job_without_a_runner_fails_the_schema(tmp_path: Path) -> None:
    broken = _VALID_WORKFLOW.replace("    runs-on: ubuntu-24.04\n", "")

    code, _ = _schema("vendor.github-workflows", write(tmp_path, "w.yml", broken))

    assert code == 1


def test_a_valid_workflow_passes_the_schema(tmp_path: Path) -> None:
    code, output = _schema(
        "vendor.github-workflows", write(tmp_path, "w.yml", _VALID_WORKFLOW)
    )

    assert code == 0, output
