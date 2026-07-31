"""Gate model, the JSON report, and minimal terminal output (ADR 0025).

Terminal: a single ``running quality gates… Ns`` ticker while gates run, then a
one-line verdict — on failure it names the failing gate(s) and points at the
report, never the raw tool output. ``build/reports/gates.json`` (always written)
carries the complete structured per-gate record read by tooling.
"""

from __future__ import annotations

import json
import sys
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence

REPORT_PATH = Path("build/reports/gates.json")

_TICK_S = 0.5


@dataclass(frozen=True)
class Gate:
    """A single deterministic pass/fail check invoked as a subprocess."""

    name: str
    command: tuple[str, ...]


@dataclass(frozen=True)
class GateOutcome:
    """The result of running one :class:`Gate`."""

    name: str
    passed: bool
    duration_s: float
    output: str


@contextmanager
def running_ticker() -> Generator[None]:
    """Show liveness while gates run: a live seconds counter on a TTY, one line off."""
    start = time.monotonic()

    if not sys.stderr.isatty():
        sys.stderr.write("running quality gates…\n")
        sys.stderr.flush()
        yield
        return

    stop = threading.Event()

    def tick() -> None:
        while not stop.wait(_TICK_S):
            sys.stderr.write(
                f"\rrunning quality gates… {time.monotonic() - start:.0f}s"
            )
            sys.stderr.flush()

    thread = threading.Thread(target=tick, daemon=True)
    thread.start()
    try:
        yield
    finally:
        stop.set()
        thread.join()
        sys.stderr.write("\r\033[K")
        sys.stderr.flush()


def print_verdict(outcomes: Sequence[GateOutcome], report_path: Path) -> None:
    failed = [o for o in outcomes if not o.passed]
    total_s = sum(o.duration_s for o in outcomes)

    if failed:
        names = ", ".join(o.name for o in failed)
        sys.stderr.write(
            f"quality gates FAILED — {names} · {total_s:.1f}s · see {report_path}\n",
        )
        # Two-channel, adapted for humans: a real TTY (a dev running the gate by
        # hand) gets the failing gate's own output inline, so no one has to open
        # the JSON to see what broke. A pipe (CI, a subagent, captured logs) still
        # gets just the one-line verdict above — the machine reads the report.
        if sys.stderr.isatty():
            for outcome in failed:
                body = outcome.output.strip()
                if body:
                    sys.stderr.write(f"\n── {outcome.name} ──\n{body}\n")
    else:
        sys.stderr.write(
            f"quality gates passed · {len(outcomes)} gates · {total_s:.1f}s\n",
        )


def write_report(outcomes: Sequence[GateOutcome], *, mode: str) -> Path:
    """Write the complete structured record, always, regardless of result."""
    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": mode,
        "passed": all(o.passed for o in outcomes),
        "gates": [
            {
                "name": o.name,
                "status": "pass" if o.passed else "fail",
                "duration_s": round(o.duration_s, 3),
                "output": o.output,
            }
            for o in outcomes
        ],
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    return REPORT_PATH
