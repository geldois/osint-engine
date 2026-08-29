from __future__ import annotations

import re
import sys
from pathlib import Path

from _hook_io import add_context, git_root, read_event, run, tool_input, tool_response

_HEREDOC = re.compile(r"<<-?(['\"]?)(\w+)\1\n.*?\n\s*\2(?=\s|$)", re.DOTALL)
_GIT_COMMIT_OR_MERGE = re.compile(r"\bgit\s+(?:commit|merge)\b")
_GATE_FAILED = "quality gates FAILED"


def _strip_heredocs(command: str) -> str:
    return _HEREDOC.sub(lambda m: f"<<{m.group(2)}", command)


def main() -> int:
    event = read_event()
    command = tool_input(event, "command")
    if not _GIT_COMMIT_OR_MERGE.search(_strip_heredocs(command)):
        return 0

    response = tool_response(event)
    stdout = response.get("stdout")
    stderr = response.get("stderr")
    combined = (stdout if isinstance(stdout, str) else "") + (
        stderr if isinstance(stderr, str) else ""
    )
    if _GATE_FAILED in combined:
        return 0

    root = git_root(Path.cwd())
    if root is None:
        return 0

    status = run(["git", "status", "--porcelain"], root)
    if status is None or not status.stdout.strip():
        return 0

    add_context(
        "Working tree isn't clean after that commit or merge — judge whether "
        "this is leftover fix output that needs its own commit(s) now, or a "
        "deliberate, unrelated work-in-progress you'll commit later.",
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
