from __future__ import annotations

import json
import re
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
_MAX_INLINE_LINES = 60
_PYTEST_PROGRESS = re.compile(r"\[\s*\d+%\]\s*$|^\s*[.sFExXpP]+\s*$")


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


@contextmanager
def running_ticker() -> Generator[None]:
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
        for outcome in failed:
            body = _actionable(outcome.output)
            if body:
                sys.stderr.write(f"\n── {outcome.name} ──\n{body}\n")
    else:
        sys.stderr.write(
            f"quality gates passed · {len(outcomes)} gates · {total_s:.1f}s\n",
        )


def _is_noise(line: str) -> bool:
    return line.lstrip().startswith("warning: `VIRTUAL_ENV") or bool(
        _PYTEST_PROGRESS.search(line)
    )


def _actionable(output: str) -> str:
    lines = [line for line in output.splitlines() if not _is_noise(line)]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if len(lines) > _MAX_INLINE_LINES:
        lines = ["…(trimmed; full output in the report)", *lines[-_MAX_INLINE_LINES:]]
    return "\n".join(lines)


def write_report(outcomes: Sequence[GateOutcome], *, mode: str) -> Path:
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
