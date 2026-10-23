from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
from test_scripts.tools import BIN, ROOT, run, write

from scripts.check import SHELL_FILES

if TYPE_CHECKING:
    import subprocess
    from pathlib import Path

_ZIZMOR_CONFIG = ROOT / ".github" / "zizmor.yml"
_CLEAN = (
    'name: Probe\n"on": push\npermissions: {}\n'
    "concurrency:\n  group: probe\n  cancel-in-progress: true\n"
    "jobs:\n  probe:\n    name: Probe\n    runs-on: ubuntu-24.04\n"
    "    permissions:\n      contents: read\n    steps:\n"
    "      - name: Checkout\n"
    "        uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0"
    " # v7.0.0\n"
    "        with:\n          persist-credentials: false\n"
)
_CALLEE = (
    'name: Callee\n"on":\n  workflow_call:\n    secrets:\n      TOKEN:\n'
    "        required: false\npermissions: {}\n"
    "jobs:\n  work:\n    name: Work\n    runs-on: ubuntu-24.04\n"
    "    steps:\n      - name: Say\n        run: echo ok\n"
)
_CALLER = (
    'name: Caller\n"on": push\npermissions: {}\n'
    "concurrency:\n  group: caller\n  cancel-in-progress: true\n"
    "jobs:\n  call:\n    name: Call\n    uses: ./.github/workflows/callee.yml\n"
)
_INHERIT = "    secrets: inherit\n"


def _passing(secret: str) -> str:
    return f"    secrets:\n      {secret}: " + "${{ secrets.TOKEN }}\n"


def _repository(tmp_path: Path, **workflows: str) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    run(["git", "init", "--quiet"], cwd=tmp_path)
    directory = tmp_path / ".github" / "workflows"
    directory.mkdir(parents=True)
    for name, text in workflows.items():
        write(directory, f"{name}.yml", text)

    return tmp_path


def _actionlint(repository: Path) -> subprocess.CompletedProcess[str]:
    environment = {**os.environ, "PATH": f"{BIN}{os.pathsep}{os.environ['PATH']}"}

    return run([str(BIN / "actionlint")], cwd=repository, env=environment)


def _zizmor(repository: Path) -> subprocess.CompletedProcess[str]:
    return run(
        [
            str(BIN / "zizmor"),
            "--persona",
            "pedantic",
            "--offline",
            "--no-progress",
            "--config",
            str(_ZIZMOR_CONFIG),
            str(repository / ".github"),
        ],
        cwd=repository,
    )


def _findings(result: subprocess.CompletedProcess[str]) -> str:
    return result.stdout + result.stderr


def test_every_deploy_script_is_a_gated_shell_file() -> None:
    found = sorted(
        path.relative_to(ROOT).as_posix() for path in ROOT.glob("deploy/*.sh")
    )

    assert set(found) <= set(SHELL_FILES)
    assert found


def test_actionlint_accepts_a_workflow_that_calls_another_with_a_declared_secret(
    tmp_path: Path,
) -> None:
    repository = _repository(
        tmp_path,
        callee=_CALLEE,
        caller=_CALLER + _passing("TOKEN"),
    )

    result = _actionlint(repository)

    assert result.returncode == 0, _findings(result)


def test_actionlint_rejects_a_secret_the_called_workflow_does_not_declare(
    tmp_path: Path,
) -> None:
    repository = _repository(
        tmp_path,
        callee=_CALLEE,
        caller=_CALLER + _passing("OTHER"),
    )

    result = _actionlint(repository)

    assert result.returncode == 1
    assert "OTHER" in _findings(result)


def test_actionlint_checks_run_scripts_with_the_pinned_shellcheck(
    tmp_path: Path,
) -> None:
    broken = _CLEAN + "      - name: Echo\n        run: echo $UNQUOTED\n"
    repository = _repository(tmp_path, probe=broken)

    result = _actionlint(repository)

    assert result.returncode == 1
    assert "SC2086" in _findings(result)


@pytest.mark.parametrize(
    ("audit", "mutation"),
    [
        (
            "artipacked",
            ("        with:\n          persist-credentials: false\n", ""),
        ),
        (
            "excessive-permissions",
            ("permissions: {}\n", "permissions: write-all\n"),
        ),
        (
            "template-injection",
            (
                "    steps:\n",
                "    steps:\n      - name: Echo\n"
                "        run: echo ${{ github.ref_name }}\n",
            ),
        ),
    ],
)
def test_zizmor_rejects_each_hardened_workflow_when_it_is_weakened(
    tmp_path: Path, audit: str, mutation: tuple[str, str]
) -> None:
    clean = _repository(tmp_path / "clean", probe=_CLEAN)
    weakened = _repository(
        tmp_path / "weakened", probe=_CLEAN.replace(mutation[0], mutation[1])
    )

    assert _zizmor(clean).returncode == 0
    result = _zizmor(weakened)
    assert result.returncode != 0
    assert audit in _findings(result)


def test_zizmor_rejects_secrets_inherit(tmp_path: Path) -> None:
    repository = _repository(tmp_path, callee=_CALLEE, caller=_CALLER + _INHERIT)

    result = _zizmor(repository)

    assert result.returncode != 0
    assert "secrets-inherit" in _findings(result)
