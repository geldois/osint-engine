from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

from scripts._report import GateOutcome, write_report

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def _read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_write_report_maps_each_status(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    outcomes = [
        GateOutcome("a", passed=True, duration_s=0.1, output="ok"),
        GateOutcome("b", passed=False, duration_s=0.2, output="boom"),
    ]

    report = _read(write_report(outcomes, mode="fast"))

    gates = cast("list[dict[str, object]]", report["gates"])
    assert [g["status"] for g in gates] == ["pass", "fail"]
    assert report["mode"] == "fast"


def test_write_report_passed_is_false_when_any_gate_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    outcomes = [
        GateOutcome("a", passed=True, duration_s=0.1, output=""),
        GateOutcome("b", passed=False, duration_s=0.2, output=""),
    ]

    assert _read(write_report(outcomes, mode="fast"))["passed"] is False


def test_write_report_is_always_written_even_on_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    path = write_report(
        [GateOutcome("a", passed=False, duration_s=0.1, output="")],
        mode="full",
    )

    assert path.exists()
