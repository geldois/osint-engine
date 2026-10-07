from __future__ import annotations

from typing import TYPE_CHECKING

from scripts._report import GateOutcome, print_verdict

if TYPE_CHECKING:
    import pytest


def test_passing_run_prints_one_line(capsys: pytest.CaptureFixture[str]) -> None:
    outcomes = [
        GateOutcome("a", passed=True, duration_s=0.1, output="noise"),
        GateOutcome("b", passed=True, duration_s=0.2, output="noise"),
    ]

    print_verdict(outcomes)

    err = capsys.readouterr().err
    assert err.count("\n") == 1
    assert "passed · 2 gates" in err
    assert "noise" not in err


def test_failing_run_names_failed_gates_and_prints_only_their_output(
    capsys: pytest.CaptureFixture[str],
) -> None:
    outcomes = [
        GateOutcome("good", passed=True, duration_s=0.1, output="fine"),
        GateOutcome("bad", passed=False, duration_s=0.2, output="boom"),
    ]

    print_verdict(outcomes)

    err = capsys.readouterr().err
    assert "FAILED — bad" in err
    assert "── bad ──\nboom" in err
    assert "fine" not in err


def test_long_failure_output_keeps_only_the_tail(
    capsys: pytest.CaptureFixture[str],
) -> None:
    output = "\n".join(f"line {n}" for n in range(200))

    print_verdict([GateOutcome("bad", passed=False, duration_s=0.1, output=output)])

    err = capsys.readouterr().err
    assert "line 199" in err
    assert "line 0\n" not in err
    assert "earlier lines omitted" in err
