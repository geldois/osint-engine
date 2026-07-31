"""Shift-left autofix (ADR 0025) — ``PostToolUse(Edit|Write)``.

After each edit, first apply every SAFE autofix to the file in place
(formatting + mechanically-fixable lint), then inject ONLY the residual — what
no formatter can decide (type errors, un-reflowable lint) — back into the
model's context to fix by hand. Trivial hygiene never costs a token; only real
judgment is surfaced, per file, while writing. Silent on success. Heavy
whole-program gates stay at the commit gate.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from _hook_io import add_context, read_event, tool_input

_RUFF = ("uv", "run", "--no-sync", "ruff")
_BASEDPYRIGHT = ("uv", "run", "--no-sync", "basedpyright")
_DPRINT = ("mise", "exec", "--", "dprint", "fmt")

# The extensions dprint owns (json/toml/yaml/markdown) — reflowed in place, no
# residual. Python is handled by ruff + basedpyright below.
_DPRINT_EXTENSIONS = frozenset({".md", ".json", ".jsonc", ".toml", ".yaml", ".yml"})


def main() -> int:
    """Autofix the edited file in place; inject only the irreducible residual."""
    file = tool_input(event=read_event(), key="file_path")
    if not file:
        return 0

    path = Path(file)
    if not path.is_absolute():
        path = Path.cwd() / path
    # uv.lock is generated TOML; never reformat it (would break `uv lock --check`).
    if path.name == "uv.lock" or not path.is_file():
        return 0

    suffix = path.suffix
    if suffix != ".py" and suffix not in _DPRINT_EXTENSIONS:
        return 0

    root = _git_root(path.parent)
    if root is None:
        return 0

    sections: list[str] = []
    if suffix == ".py":
        _run([*_RUFF, "format", str(path)], root)
        _run([*_RUFF, "check", "--fix", str(path)], root)
        _collect(sections, "ruff", [*_RUFF, "check", str(path)], root)
        _collect(sections, "basedpyright", [*_BASEDPYRIGHT, str(path)], root)
    else:
        relative = path.relative_to(root)
        _collect(sections, "dprint", [*_DPRINT, str(relative)], root)

    if sections:
        add_context("\n\n".join(sections))

    return 0


def _git_root(start: Path) -> Path | None:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=start,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip())


def _run(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)


def _collect(sections: list[str], label: str, command: list[str], cwd: Path) -> None:
    result = subprocess.run(
        command, cwd=cwd, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        output = (result.stdout or "") + (result.stderr or "")
        sections.append(f"── {label} ──\n{output}")


if __name__ == "__main__":
    sys.exit(main())
