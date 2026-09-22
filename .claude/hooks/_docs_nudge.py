from __future__ import annotations

_EXCLUDED_PREFIXES = (
    "docs/",
    "src/osint_engine/infrastructure/persistence/pg/generated/",
)
_EXCLUDED_FILES = frozenset({"README.md", "TO-DO.md", "CLAUDE.md", "CONTEXT.md"})

SIBLING_REPO_NAME = "osint-studio"

_DOCS_NUDGE = (
    "Files changed this turn. Judge, don't act reflexively: was the change "
    "semantic (business/flow logic, a new library, a new tool/pattern, a "
    "trade-off worth remembering) or purely mechanical (rename, typing, "
    "refactor)? If semantic, the whole docs surface of this repo applies, "
    "not just one matching file — every docs/architecture/*.md, plus "
    "README.md, CONTEXT.md, and TO-DO.md.{sibling_clause} Update whichever "
    "no longer tells the truth, in natural language — never cite a "
    "function, class, or type name. If mechanical, skip."
)


def is_relevant_change(rel: str) -> bool:
    if rel in _EXCLUDED_FILES:
        return False
    return not any(rel.startswith(prefix) for prefix in _EXCLUDED_PREFIXES)


def docs_nudge_text(sibling_path: str | None = None) -> str:
    sibling_clause = (
        f" {SIBLING_REPO_NAME} at {sibling_path} shares this system's "
        "contract — check its docs/architecture/, README.md, CONTEXT.md, "
        "and TO-DO.md too if this change could affect it."
        if sibling_path
        else ""
    )
    return _DOCS_NUDGE.format(sibling_clause=sibling_clause)
