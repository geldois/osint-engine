from __future__ import annotations

import os
from pathlib import Path

from scripts._report import Gate
from scripts.gates import _run_gate  # pyright: ignore[reportPrivateUsage]


def test_missing_tool_is_a_failure_not_a_skip() -> None:
    gate = Gate("ghost", ("osint-engine-nonexistent-binary",))

    outcome = _run_gate(gate, Path.cwd(), dict(os.environ))

    assert outcome.passed is False
    assert "not found" in outcome.output
