from __future__ import annotations

import sqlite3
import subprocess
import tomllib
from collections import Counter
from contextlib import closing, contextmanager
from decimal import Decimal
from typing import TYPE_CHECKING, cast

import pytest
from test_scripts.tools import ROOT

from scripts import mutation
from scripts.mutation import Score

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

_MUTATED_LAYERS = {"application", "domain"}
_KILLED = ("NORMAL", "KILLED")
_SURVIVED = ("NORMAL", "SURVIVED")
_INCOMPETENT = ("NORMAL", "INCOMPETENT")


def _toml(name: str) -> dict[str, object]:
    return tomllib.loads((ROOT / name).read_text(encoding="utf-8"))


def _score(
    *, killed: int = 0, survived: int = 0, incompetent: int = 0, errors: int = 0
) -> Score:
    return Score(
        planned=killed + survived + incompetent + errors,
        killed=killed,
        survived=survived,
        incompetent=incompetent,
        errors=errors,
    )


def _session(
    path: Path, *, planned: int, rows: Counter[tuple[str, str | None]]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as database:
        database.execute("create table work_items (job_id text)")
        database.execute(
            "create table work_results "
            "(job_id text, worker_outcome text, test_outcome text)"
        )
        database.executemany(
            "insert into work_items values (?)", [(str(n),) for n in range(planned)]
        )
        database.executemany(
            "insert into work_results values (?, ?, ?)",
            [
                (f"{worker}{test}{n}", worker, test)
                for (worker, test), count in rows.items()
                for n in range(count)
            ],
        )
        database.commit()


class _Run:
    def __init__(self, tmp_path: Path) -> None:
        self.tmp_path = tmp_path
        self.commands: list[tuple[str, ...]] = []
        self.rows: Counter[tuple[str, str | None]] = Counter({_KILLED: 4, _SURVIVED: 1})
        self.planned = 5

    def __call__(
        self, _worktree: Path, *command: str, capture: bool = False
    ) -> subprocess.CompletedProcess[str]:
        self.commands.append(command)
        if command[:2] == ("cosmic-ray", "exec"):
            _session(self.tmp_path / command[3], planned=self.planned, rows=self.rows)
        stdout = "survivor diff" if capture else ""

        return subprocess.CompletedProcess(command, 0, stdout=stdout)


@pytest.fixture
def run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> _Run:
    fake = _Run(tmp_path)

    def fake_sync(_worktree: Path) -> None:
        return None

    @contextmanager
    def fake_worktree(_commit: str) -> Generator[Path]:
        yield tmp_path

    monkeypatch.setattr(mutation, "_run", fake)
    monkeypatch.setattr(mutation, "REPORTS", tmp_path / "reports")
    monkeypatch.setattr(mutation, "sync", fake_sync)
    monkeypatch.setattr(mutation, "detached_worktree", fake_worktree)
    _set_floors(monkeypatch, {})

    return fake


def _set_floors(monkeypatch: pytest.MonkeyPatch, floors: dict[str, Decimal]) -> None:
    def fake_floor(layer: str) -> Decimal | None:
        return floors.get(layer)

    monkeypatch.setattr(mutation, "floor", fake_floor)


def test_the_mutated_layers_are_exactly_domain_and_application() -> None:
    assert set(mutation.layers()) == _MUTATED_LAYERS


def test_each_layer_config_mutates_its_own_layer() -> None:
    for layer in mutation.layers():
        config = cast("dict[str, dict[str, str]]", _toml(f"cosmic-ray.{layer}.toml"))

        assert config["cosmic-ray"]["module-path"] == f"src/osint_engine/{layer}"
        assert f"tests/test_src/test_{layer}" in config["cosmic-ray"]["test-command"]


def test_the_project_configuration_floors_only_name_mutated_layers() -> None:
    project = _toml("pyproject.toml")
    scripts = cast("dict[str, dict[str, object]]", project["tool"]).get("scripts", {})

    assert set(cast("dict[str, object]", scripts.get("mutation-floor", {}))) <= (
        _MUTATED_LAYERS
    )


@pytest.mark.parametrize(
    ("project", "expected"),
    [
        ({}, None),
        ({"tool": {"scripts": {}}}, None),
        ({"tool": {"scripts": {"mutation-floor": {"other": 90}}}}, None),
        ({"tool": {"scripts": {"mutation-floor": {"domain": 90}}}}, Decimal(90)),
        ({"tool": {"scripts": {"mutation-floor": {"domain": 91.9}}}}, Decimal("91.9")),
        ({"tool": {"scripts": {"mutation-floor": {"domain": 0}}}}, Decimal(0)),
        ({"tool": {"scripts": {"mutation-floor": {"domain": 100}}}}, Decimal(100)),
    ],
)
def test_a_floor_is_read_exactly_or_absent(
    project: dict[str, object], expected: Decimal | None
) -> None:
    assert mutation.floor_from(project, "domain") == expected


@pytest.mark.parametrize("value", ["90", True, None, [90]])
def test_a_floor_that_is_not_a_number_is_refused(value: object) -> None:
    project: dict[str, object] = {
        "tool": {"scripts": {"mutation-floor": {"domain": value}}}
    }

    with pytest.raises(TypeError):
        mutation.floor_from(project, "domain")


@pytest.mark.parametrize("value", [-0.1, 100.1, 101, -1])
def test_a_floor_outside_zero_to_one_hundred_is_refused(value: float) -> None:
    project: dict[str, object] = {
        "tool": {"scripts": {"mutation-floor": {"domain": value}}}
    }

    with pytest.raises(ValueError, match="within 0 and 100"):
        mutation.floor_from(project, "domain")


def test_incompetent_mutants_leave_the_denominator() -> None:
    score = mutation.score_from(6, Counter({_KILLED: 3, _SURVIVED: 1, _INCOMPETENT: 2}))

    assert score.killed_percent == Decimal(75)
    assert score.incompetent == 2


def test_every_worker_outcome_but_a_normal_one_is_an_error() -> None:
    score = mutation.score_from(
        4,
        Counter(
            {
                _KILLED: 1,
                ("EXCEPTION", None): 1,
                ("NO_TEST", None): 1,
                ("ABNORMAL", None): 1,
            }
        ),
    )

    assert score.errors == 3


def test_a_normal_worker_with_an_unknown_test_outcome_is_an_error() -> None:
    score = mutation.score_from(2, Counter({_KILLED: 1, ("NORMAL", "SURPRISE"): 1}))

    assert score.errors == 1


def test_a_floor_exactly_met_passes() -> None:
    code, lines = mutation.verdict(_score(killed=9, survived=1), Decimal(90))

    assert code == 0
    assert "held" in lines[-1]


def test_a_score_just_under_the_floor_fails() -> None:
    code, lines = mutation.verdict(_score(killed=899, survived=101), Decimal(90))

    assert code == 1
    assert "below the floor" in lines[-1]


def test_a_floor_of_one_hundred_fails_on_a_single_survivor() -> None:
    code, _ = mutation.verdict(_score(killed=999, survived=1), Decimal(100))

    assert code == 1


def test_a_floor_of_zero_never_fails_a_complete_session() -> None:
    code, _ = mutation.verdict(_score(survived=7), Decimal(0))

    assert code == 0


def test_a_score_a_full_point_over_the_floor_says_to_raise_it() -> None:
    code, lines = mutation.verdict(_score(killed=95, survived=5), Decimal(90))

    assert code == 0
    assert "raise it to 95.0%" in lines[-1]


def test_a_score_under_a_point_over_the_floor_asks_for_nothing() -> None:
    _, lines = mutation.verdict(_score(killed=905, survived=95), Decimal(90))

    assert "raise" not in lines[-1]


def test_without_a_floor_the_run_only_measures() -> None:
    code, lines = mutation.verdict(_score(killed=1, survived=9), None)

    assert code == 0
    assert "measurement only" in lines[-1]


def test_a_session_that_did_not_finish_never_passes() -> None:
    unfinished = Score(planned=10, killed=5, survived=0, incompetent=0, errors=0)

    code, lines = mutation.verdict(unfinished, None)

    assert code == 1
    assert "5 of 10" in lines[0]


def test_a_session_with_no_planned_mutant_never_passes() -> None:
    code, _ = mutation.verdict(Score(0, 0, 0, 0, 0), None)

    assert code == 1


def test_worker_errors_fail_even_with_a_perfect_score_on_the_rest() -> None:
    code, lines = mutation.verdict(_score(killed=9, errors=1), Decimal(0))

    assert code == 1
    assert "worker errors" in lines[0]


def test_a_session_where_nothing_was_scored_never_passes() -> None:
    code, lines = mutation.verdict(_score(incompetent=3), None)

    assert code == 1
    assert "no mutant was scored" in lines[0]


def test_a_session_file_is_read_back_into_its_score(tmp_path: Path) -> None:
    path = tmp_path / "session.sqlite"
    _session(path, planned=7, rows=Counter({_KILLED: 4, _SURVIVED: 2, _INCOMPETENT: 1}))

    assert mutation.read_score(path) == Score(
        planned=7, killed=4, survived=2, incompetent=1, errors=0
    )


def test_an_unknown_layer_is_refused(
    run: _Run, capsys: pytest.CaptureFixture[str]
) -> None:
    assert mutation.run_mutation(layer="infrastructure") == 2
    assert "unknown layer" in capsys.readouterr().out
    assert run.commands == []


def test_one_layer_runs_the_session_in_order(run: _Run) -> None:
    assert mutation.run_mutation(layer="domain") == 0

    assert [command[:2] for command in run.commands] == [
        ("cosmic-ray", "init"),
        ("cosmic-ray", "baseline"),
        ("cosmic-ray", "exec"),
        ("cr-report", ".cache/mutation/domain.sqlite"),
    ]


@pytest.mark.usefixtures("run")
def test_the_score_and_the_survivors_are_kept_after_the_worktree_is_gone(
    tmp_path: Path,
) -> None:
    mutation.run_mutation(layer="application")

    reports = tmp_path / "reports"
    assert (reports / "application-survivors.txt").read_text(encoding="utf-8") == (
        "survivor diff"
    )
    assert "killed 80.00%" in (reports / "application-score.txt").read_text(
        encoding="utf-8"
    )


@pytest.mark.usefixtures("run")
def test_a_floor_above_the_measured_score_fails_the_run(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_floors(monkeypatch, {"domain": Decimal(81)})

    assert mutation.run_mutation(layer="domain") == 1


def test_an_incomplete_session_fails_the_run(run: _Run) -> None:
    run.planned = 9

    assert mutation.run_mutation(layer="domain") == 1


def test_every_layer_runs_when_none_is_named(run: _Run) -> None:
    mutation.run_mutation(layer=None)

    inited = {
        command[2] for command in run.commands if command[:2] == ("cosmic-ray", "init")
    }
    assert inited == {f"cosmic-ray.{layer}.toml" for layer in _MUTATED_LAYERS}


@pytest.mark.usefixtures("run")
def test_a_failing_layer_does_not_hide_behind_a_passing_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_floors(monkeypatch, {"domain": Decimal(99), "application": Decimal(0)})

    assert mutation.run_mutation(layer=None) == 1
