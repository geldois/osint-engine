from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass(frozen=True)
class Gate:
    name: str
    command: tuple[str, ...]


@dataclass(frozen=True)
class GateOutcome:
    name: str
    passed: bool
    duration_s: float


def print_header(name: str) -> None:
    sys.stderr.write(f"\n── {name} ──\n")
    sys.stderr.flush()


def print_verdict(outcomes: Sequence[GateOutcome]) -> None:
    failed = [o for o in outcomes if not o.passed]
    total_s = sum(o.duration_s for o in outcomes)

    if not failed:
        sys.stderr.write(
            f"\nquality gates passed · {len(outcomes)} gates · {total_s:.1f}s\n"
        )
        return

    names = ", ".join(o.name for o in failed)
    sys.stderr.write(f"\nquality gates FAILED — {names} · {total_s:.1f}s\n")
