from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from scripts._report import Gate
from scripts.check import _run_gate  # pyright: ignore[reportPrivateUsage]

if TYPE_CHECKING:
    import pytest


def _python_gate(*, name: str, source: str) -> Gate:
    return Gate(name, (sys.executable, "-c", source))


def test_missing_tool_is_a_failure_not_a_skip(
    capsys: pytest.CaptureFixture[str],
) -> None:
    gate = Gate("ghost", ("osint-engine-nonexistent-binary",))

    outcome = _run_gate(gate, Path.cwd(), dict(os.environ))

    assert outcome.passed is False
    assert "not found" in capsys.readouterr().err


def test_a_tool_error_output_reaches_the_terminal_right_under_its_header(
    capfd: pytest.CaptureFixture[str],
) -> None:
    gate = _python_gate(
        name="noisy",
        source="import sys; print('line one', file=sys.stderr); "
        "print('line two', file=sys.stderr)",
    )

    outcome = _run_gate(gate, Path.cwd(), dict(os.environ))

    assert outcome.passed is True
    assert capfd.readouterr().err == "\n── noisy ──\nline one\nline two\n"


def test_a_tool_standard_output_reaches_the_terminal_untouched(
    capfd: pytest.CaptureFixture[str],
) -> None:
    gate = _python_gate(name="chatty", source="print('  indented  output  ')")

    _run_gate(gate, Path.cwd(), dict(os.environ))

    assert capfd.readouterr().out == "  indented  output  \n"


def test_a_nonzero_exit_is_a_failure_and_its_output_is_still_shown(
    capfd: pytest.CaptureFixture[str],
) -> None:
    gate = _python_gate(
        name="broken",
        source="import sys; print('why it failed', file=sys.stderr); sys.exit(3)",
    )

    outcome = _run_gate(gate, Path.cwd(), dict(os.environ))

    assert outcome.passed is False
    assert "why it failed" in capfd.readouterr().err


def test_the_outcome_names_the_gate_and_measures_its_duration() -> None:
    gate = _python_gate(name="timed", source="pass")

    outcome = _run_gate(gate, Path.cwd(), dict(os.environ))

    assert outcome.name == "timed"
    assert outcome.duration_s >= 0
