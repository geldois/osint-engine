from __future__ import annotations

import re
import sys
from pathlib import Path

from _hook_io import contained_rel, context, project_root, read_event, tool_input

_FETCHER_PATH = re.compile(
    r"^src/osint_engine/infrastructure/providers/(?!kipflow/)[^/]+/.*_fetcher\.py$"
)
_URL_SUFFIX = re.compile(r'url_suffix="([^"]+)"')
_FIXTURES_SCRIPT = "scripts/fixtures.py"


def main() -> int:
    file = tool_input(read_event(), "file_path")
    if not file:
        return 0

    target = _resolve_fetcher(file)
    if target is None:
        return 0
    root, rel, source = target

    fixtures_path = root / _FIXTURES_SCRIPT
    fixtures_source = (
        fixtures_path.read_text(encoding="utf-8") if fixtures_path.is_file() else ""
    )

    found = _URL_SUFFIX.findall(source)
    missing = [suffix for suffix in found if f'"{suffix}"' not in fixtures_source]
    if missing:
        context(
            "PostToolUse",
            f"{rel} declares url_suffix {', '.join(missing)} with no matching "
            f"case in {_FIXTURES_SCRIPT} (CLAUDE.md). Add one, or confirm this "
            "endpoint is excluded on purpose (e.g. a paid provider).",
        )

    return 0


def _resolve_fetcher(file: str) -> tuple[Path, str, str] | None:
    root = project_root()
    if root is None:
        return None

    path = Path(file)
    if not path.is_absolute():
        path = root / path
    if not path.is_file():
        return None
    rel = contained_rel(path, root)
    if rel is None:
        return None
    if not _FETCHER_PATH.match(rel):
        return None

    return root, rel, path.read_text(encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
