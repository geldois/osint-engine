from __future__ import annotations

import subprocess
import tomllib
from contextlib import contextmanager
from typing import TYPE_CHECKING, cast

import pytest
from test_scripts.tools import ROOT

from scripts import mutation

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

_MUTATED_LAYERS = {"application", "domain"}


def _toml(name: str) -> dict[str, object]:
    return tomllib.loads((ROOT / name).read_text(encoding="utf-8"))


@pytest.fixture
def commands(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, ...]]:
    seen: list[tuple[str, ...]] = []

    def fake_run(
        _worktree: Path, *command: str, capture: bool = False
    ) -> subprocess.CompletedProcess[str]:
        seen.append(command)
        stdout = "survivor diff" if capture else ""

        return subprocess.CompletedProcess(command, 0, stdout=stdout)

    def fake_sync(_worktree: Path) -> None:
        return None

    @contextmanager
    def fake_worktree(_commit: str) -> Generator[Path]:
        yield tmp_path

    monkeypatch.setattr(mutation, "_run", fake_run)
    monkeypatch.setattr(mutation, "REPORTS", tmp_path / "reports")
    monkeypatch.setattr(mutation, "sync", fake_sync)
    monkeypatch.setattr(mutation, "detached_worktree", fake_worktree)

    return seen


def test_the_mutated_layers_are_exactly_domain_and_application() -> None:
    assert set(mutation.layers()) == _MUTATED_LAYERS


def test_each_layer_config_mutates_its_own_layer() -> None:
    for layer in mutation.layers():
        config = cast("dict[str, dict[str, str]]", _toml(f"cosmic-ray.{layer}.toml"))

        assert config["cosmic-ray"]["module-path"] == f"src/osint_engine/{layer}"
        assert f"tests/test_src/test_{layer}" in config["cosmic-ray"]["test-command"]


def test_every_layer_has_a_ceiling_between_zero_and_one_hundred() -> None:
    for layer in mutation.layers():
        assert 0 <= mutation.ceiling(layer) <= 100


def test_a_layer_without_a_ceiling_fails_loudly() -> None:
    with pytest.raises(KeyError):
        mutation.ceiling("no-such-layer")


def test_an_unknown_layer_is_refused(
    commands: list[tuple[str, ...]], capsys: pytest.CaptureFixture[str]
) -> None:
    assert mutation.run_mutation(layer="infrastructure") == 2
    assert "unknown layer" in capsys.readouterr().out
    assert commands == []


def test_one_layer_runs_the_session_in_order_and_gates_on_its_ceiling(
    commands: list[tuple[str, ...]],
) -> None:
    assert mutation.run_mutation(layer="domain") == 0

    steps = [command[:2] for command in commands]
    assert steps == [
        ("cosmic-ray", "init"),
        ("cosmic-ray", "baseline"),
        ("cosmic-ray", "exec"),
        ("cr-report", ".cache/mutation/domain.sqlite"),
        ("cr-rate", ".cache/mutation/domain.sqlite"),
    ]
    assert commands[-1][-2:] == ("--fail-over", str(mutation.ceiling("domain")))


@pytest.mark.usefixtures("commands")
def test_the_survivors_are_kept_after_the_worktree_is_gone(tmp_path: Path) -> None:
    mutation.run_mutation(layer="application")

    report = tmp_path / "reports" / "application-survivors.txt"
    assert report.read_text(encoding="utf-8") == "survivor diff"


def test_every_layer_runs_when_none_is_named(
    commands: list[tuple[str, ...]],
) -> None:
    mutation.run_mutation(layer=None)

    inited = {
        command[2] for command in commands if command[:2] == ("cosmic-ray", "init")
    }
    assert inited == {f"cosmic-ray.{layer}.toml" for layer in _MUTATED_LAYERS}
