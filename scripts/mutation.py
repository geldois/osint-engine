from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path
from typing import cast

from scripts._discovery import ROOT, tracked
from scripts._isolation import detached_worktree, sync

REPORTS = ROOT / ".cache" / "mutation"

_CONFIG_PREFIX = "cosmic-ray."
_CONFIG_SUFFIX = ".toml"
_SESSIONS = Path(".cache") / "mutation"


def layers() -> tuple[str, ...]:
    return tuple(
        name.removeprefix(_CONFIG_PREFIX).removesuffix(_CONFIG_SUFFIX)
        for name in tracked(":(glob)cosmic-ray.*.toml")
    )


def ceiling(layer: str) -> float:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    tool = cast("dict[str, dict[str, dict[str, float]]]", project["tool"])

    return tool["scripts"]["mutation-ceiling"][layer]


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
    session = str(_SESSIONS / f"{layer}.sqlite")
    (worktree / _SESSIONS).mkdir(parents=True, exist_ok=True)

    for step in (
        ("cosmic-ray", "init", config, session),
        ("cosmic-ray", "baseline", config),
        ("cosmic-ray", "exec", config, session),
    ):
        code = _run(worktree, *step).returncode
        if code != 0:
            return code

    survivors = _run(
        worktree,
        "cr-report",
        session,
        "--show-diff",
        "--surviving-only",
        capture=True,
    )
    REPORTS.mkdir(parents=True, exist_ok=True)
    destination = REPORTS / f"{layer}-survivors.txt"
    destination.write_text(survivors.stdout, encoding="utf-8")
    print(f"survivors of {layer}: {destination}")

    return _run(
        worktree, "cr-rate", session, "--fail-over", str(ceiling(layer))
    ).returncode


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
