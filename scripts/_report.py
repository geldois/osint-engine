from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

_MAX_FAILURE_LINES = 60


@dataclass(frozen=True)
class Gate:
    name: str
    command: tuple[str, ...]


@dataclass(frozen=True)
class GateOutcome:
    name: str
    passed: bool
    duration_s: float
    output: str


def print_verdict(outcomes: Sequence[GateOutcome]) -> None:
    failed = [o for o in outcomes if not o.passed]
    total_s = sum(o.duration_s for o in outcomes)

    if not failed:
        sys.stderr.write(
            f"quality gates passed · {len(outcomes)} gates · {total_s:.1f}s\n"
        )
        return

    names = ", ".join(o.name for o in failed)
    sys.stderr.write(f"quality gates FAILED — {names} · {total_s:.1f}s\n")
    for outcome in failed:
        sys.stderr.write(f"\n── {outcome.name} ──\n{_tail(outcome.output)}\n")


def _tail(output: str) -> str:
    lines = output.strip().splitlines()
    if len(lines) <= _MAX_FAILURE_LINES:
        return "\n".join(lines)
    omitted = len(lines) - _MAX_FAILURE_LINES
    return "\n".join(
        [f"…({omitted} earlier lines omitted)", *lines[-_MAX_FAILURE_LINES:]]
    )
