from __future__ import annotations

from typing import TYPE_CHECKING

from scripts._report import GateOutcome, print_header, print_verdict

if TYPE_CHECKING:
    import pytest


def test_header_is_one_line_naming_the_gate(
    capsys: pytest.CaptureFixture[str],
) -> None:
    print_header("ruff-check")

    assert capsys.readouterr().err == "\n── ruff-check ──\n"


def test_passing_run_ends_with_the_passed_verdict(
    capsys: pytest.CaptureFixture[str],
) -> None:
    outcomes = [
        GateOutcome("a", passed=True, duration_s=0.1),
        GateOutcome("b", passed=True, duration_s=0.2),
    ]

    print_verdict(outcomes)

    err = capsys.readouterr().err
    assert err.splitlines()[-1].startswith("quality gates passed · 2 gates")


def test_failing_run_ends_with_the_failed_gates_named(
    capsys: pytest.CaptureFixture[str],
) -> None:
    outcomes = [
        GateOutcome("good", passed=True, duration_s=0.1),
        GateOutcome("bad", passed=False, duration_s=0.2),
    ]

    print_verdict(outcomes)

    err = capsys.readouterr().err
    assert err.splitlines()[-1].startswith("quality gates FAILED — bad")
    assert "good" not in err
