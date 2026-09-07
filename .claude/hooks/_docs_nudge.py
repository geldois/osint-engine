from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

_STATUS_PREFIX_LENGTH = 3

_EXCLUDED_PREFIXES = (
    "docs/",
    "src/osint_engine/infrastructure/persistence/pg/generated/",
    ".venv/",
    "__pycache__/",
    ".cache/",
    "build/",
)
_EXCLUDED_FILES = frozenset(
    {"README.md", "TO-DO.md", "CLAUDE.md", "CONTEXT.md", "CHANGELOG.md", "uv.lock"},
)

_DOCS_NUDGE = (
    "Files changed this turn. Judge, don't act reflexively: was the change "
    "semantic (business/flow logic, a new library, a new tool, a trade-off "
    "worth remembering) or purely mechanical (rename, typing, refactor)? If "
    "semantic, update the matching docs/architecture/<area>.md{areas_list} in "
    "natural language — never cite a function, class, or type name — and check "
    "whether the Mermaid architecture diagram in README.md still represents the "
    "truth. If mechanical, skip."
)


def is_relevant_change(rel: str) -> bool:
    if rel in _EXCLUDED_FILES:
        return False
    return not any(rel.startswith(prefix) for prefix in _EXCLUDED_PREFIXES)


def porcelain_paths(stdout: str) -> list[str]:
    fields = [field for field in stdout.split("\0") if field]
    paths: list[str] = []
    i = 0
    while i < len(fields):
        entry = fields[i]
        if len(entry) > _STATUS_PREFIX_LENGTH:
            status = entry[:2]
            paths.append(entry[_STATUS_PREFIX_LENGTH:])
            if status[0] in ("R", "C"):
                i += 1
        i += 1
    return paths


def mtime_of(root: Path, rel: str) -> float:
    try:
        return (root / rel).stat().st_mtime
    except OSError:
        return -1.0


def path_mtimes(root: Path, paths: list[str]) -> dict[str, float]:
    return {path: mtime_of(root, path) for path in paths}


def serialize_mtimes(mtimes: dict[str, float]) -> str:
    return "\0".join(f"{mtime}\t{path}" for path, mtime in mtimes.items())


def parse_mtimes(raw: str) -> dict[str, float]:
    mtimes: dict[str, float] = {}
    for record in raw.split("\0"):
        mtime_str, sep, path = record.partition("\t")
        if not sep or not path:
            continue
        mtimes[path] = float(mtime_str)
    return mtimes


def changed_paths(current: dict[str, float], previous: dict[str, float]) -> list[str]:
    return [
        path
        for path in current.keys() | previous.keys()
        if current.get(path) != previous.get(path)
    ]


def docs_nudge_text(areas: list[str]) -> str:
    areas_list = f" (existing: {', '.join(areas)})" if areas else ""
    return _DOCS_NUDGE.format(areas_list=areas_list)
