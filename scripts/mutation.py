from __future__ import annotations

import sqlite3
import subprocess
import tomllib
from collections import Counter
from contextlib import closing
from dataclasses import dataclass
from decimal import ROUND_DOWN, Decimal
from pathlib import Path
from typing import cast

from scripts._discovery import ROOT, tracked
from scripts._isolation import detached_worktree, sync

REPORTS = ROOT / ".cache" / "mutation"

_CONFIG_PREFIX = "cosmic-ray."
_CONFIG_SUFFIX = ".toml"
_SESSIONS = Path(".cache") / "mutation"
_HUNDRED = Decimal(100)
_RATCHET_STEP = Decimal(1)
_NORMAL = "NORMAL"
_KILLED = "KILLED"
_SURVIVED = "SURVIVED"
_INCOMPETENT = "INCOMPETENT"


@dataclass(frozen=True)
class Score:
    planned: int
    killed: int
    survived: int
    incompetent: int
    errors: int

    @property
    def completed(self) -> int:
        return self.killed + self.survived + self.incompetent + self.errors

    @property
    def killed_percent(self) -> Decimal | None:
        scored = self.killed + self.survived
        if scored == 0:
            return None

        return Decimal(self.killed) * _HUNDRED / Decimal(scored)


def layers() -> tuple[str, ...]:
    return tuple(
        name.removeprefix(_CONFIG_PREFIX).removesuffix(_CONFIG_SUFFIX)
        for name in tracked(":(glob)cosmic-ray.*.toml")
    )


def floor_from(project: dict[str, object], layer: str) -> Decimal | None:
    tool = cast("dict[str, object]", project.get("tool", {}))
    scripts = cast("dict[str, object]", tool.get("scripts", {}))
    table = cast("dict[str, object]", scripts.get("mutation-floor", {}))
    if layer not in table:
        return None

    value = table[layer]
    if isinstance(value, bool) or not isinstance(value, int | float):
        message = f"mutation-floor of {layer!r} must be a number, got {value!r}"
        raise TypeError(message)

    floor = Decimal(str(value))
    if not Decimal(0) <= floor <= _HUNDRED:
        message = f"mutation-floor of {layer!r} must be within 0 and 100, got {floor}"
        raise ValueError(message)

    return floor


def floor(layer: str) -> Decimal | None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    return floor_from(cast("dict[str, object]", project), layer)


def score_from(planned: int, outcomes: Counter[tuple[str, str | None]]) -> Score:
    killed = outcomes[(_NORMAL, _KILLED)]
    survived = outcomes[(_NORMAL, _SURVIVED)]
    incompetent = outcomes[(_NORMAL, _INCOMPETENT)]
    errors = sum(outcomes.values()) - killed - survived - incompetent

    return Score(
        planned=planned,
        killed=killed,
        survived=survived,
        incompetent=incompetent,
        errors=errors,
    )


def read_score(session: Path) -> Score:
    with closing(sqlite3.connect(f"file:{session}?mode=ro", uri=True)) as database:
        planned = cast(
            "int", database.execute("select count(*) from work_items").fetchone()[0]
        )
        rows = cast(
            "list[tuple[str, str | None, int]]",
            database.execute(
                "select worker_outcome, test_outcome, count(*) "
                "from work_results group by 1, 2"
            ).fetchall(),
        )

    return score_from(
        planned, Counter({(worker, test): count for worker, test, count in rows})
    )


def _scored(score: Score) -> Decimal | str:
    if score.planned == 0 or score.completed != score.planned:
        return f"incomplete session: {score.completed} of {score.planned} mutants ran"
    if score.errors:
        return f"{score.errors} mutants could not be scored: worker errors"

    percent = score.killed_percent

    return "no mutant was scored" if percent is None else percent


def verdict(score: Score, layer_floor: Decimal | None) -> tuple[int, list[str]]:
    percent = _scored(score)
    if isinstance(percent, str):
        return 1, [percent]

    lines = [
        f"killed {percent:.2f}% ({score.killed} killed, {score.survived} survived, "
        f"{score.incompetent} incompetent)"
    ]
    if layer_floor is None:
        return 0, [*lines, "no floor set: measurement only, nothing gates"]
    if percent < layer_floor:
        return 1, [*lines, f"below the floor of {layer_floor}%"]
    if percent - layer_floor >= _RATCHET_STEP:
        raised = percent.quantize(Decimal("0.1"), rounding=ROUND_DOWN)
        return 0, [*lines, f"floor of {layer_floor}% held; raise it to {raised}%"]

    return 0, [*lines, f"floor of {layer_floor}% held"]


def _run(
    worktree: Path, *command: str, capture: bool = False
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["uv", "run", "--no-sync", *command],
        cwd=worktree,
        check=False,
        capture_output=capture,
        text=True,
    )


def _run_layer(layer: str, worktree: Path) -> int:
    config = f"cosmic-ray.{layer}.toml"
    session = _SESSIONS / f"{layer}.sqlite"
    (worktree / _SESSIONS).mkdir(parents=True, exist_ok=True)

    for step in (
        ("cosmic-ray", "init", config, str(session)),
        ("cosmic-ray", "baseline", config),
        ("cosmic-ray", "exec", config, str(session)),
    ):
        code = _run(worktree, *step).returncode
        if code != 0:
            return code

    survivors = _run(
        worktree,
        "cr-report",
        str(session),
        "--show-diff",
        "--surviving-only",
        capture=True,
    )
    code, lines = verdict(read_score(worktree / session), floor(layer))
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / f"{layer}-survivors.txt").write_text(survivors.stdout, encoding="utf-8")
    (REPORTS / f"{layer}-score.txt").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    for line in lines:
        print(f"{layer}: {line}")

    return code


def run_mutation(*, layer: str | None) -> int:
    known = layers()
    if layer is not None and layer not in known:
        print(f"unknown layer {layer!r}; known: {', '.join(known)}")
        return 2

    selected = known if layer is None else (layer,)
    worst = 0
    with detached_worktree("HEAD") as worktree:
        sync(worktree)
        for name in selected:
            worst = max(worst, _run_layer(name, worktree))

    return worst
