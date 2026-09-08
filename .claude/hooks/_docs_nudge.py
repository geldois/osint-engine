from __future__ import annotations

_EXCLUDED_PREFIXES = (
    "docs/",
    "src/osint_engine/infrastructure/persistence/pg/generated/",
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


def docs_nudge_text(areas: list[str]) -> str:
    areas_list = f" (existing: {', '.join(areas)})" if areas else ""
    return _DOCS_NUDGE.format(areas_list=areas_list)
