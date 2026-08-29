from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from scripts._report import REPORT_PATH, GateOutcome, print_verdict
from scripts.gates import SHELL_FILES, run_check

if TYPE_CHECKING:
    from collections.abc import Callable

_UV_RUN = ("uv", "run", "--no-sync")
_DPRINT_EXTENSIONS = (".md", ".json", ".jsonc", ".toml", ".yaml", ".yml")
_FIX_EXTENSIONS = (".py", ".sql", *_DPRINT_EXTENSIONS)
_SQL_DIRS = ("migrations", "src")
_TREE_HASH_FILE = Path("build/.gate-tree-hash")
_FIXED_PATHS_FILE = Path("build/.gate-fixed-paths")


def run_fix(paths: tuple[str, ...] = ()) -> int:
    staged_before = [path for path in _staged_files() if Path(path).is_file()]
    blobs = _index_blobs()
    pre_hash = {path: _hash_object(path) for path in staged_before}

    if not paths:
        _ruff(["."])
        _dprint([])
        _sqruff(list(_SQL_DIRS))
        _shfmt(list(SHELL_FILES))
    else:
        _fix_group([p for p in paths if p.endswith(".py")], _ruff)
        _fix_group([p for p in paths if p.endswith(_DPRINT_EXTENSIONS)], _dprint)
        _fix_group([p for p in paths if p.endswith(".sql")], _sqruff)
        _fix_group([p for p in paths if p in SHELL_FILES or p.endswith(".sh")], _shfmt)

    if staged_before:
        subprocess.run(["git", "add", "--", *staged_before], check=True)
        rewritten = [
            path for path in staged_before if pre_hash.get(path) != _hash_object(path)
        ]
        if rewritten:
            _FIXED_PATHS_FILE.parent.mkdir(parents=True, exist_ok=True)
            _FIXED_PATHS_FILE.write_text(
                "".join(f"{path}\t{blobs.get(path, '')}\n" for path in rewritten),
                encoding="utf-8",
            )
    return 0


def _fix_group(targets: list[str], run: Callable[[list[str]], None]) -> None:
    if targets:
        run(targets)


def _ruff(targets: list[str]) -> None:
    subprocess.run([*_UV_RUN, "ruff", "check", "--fix", *targets], check=False)
    subprocess.run([*_UV_RUN, "ruff", "format", *targets], check=False)


def _dprint(targets: list[str]) -> None:
    subprocess.run(["mise", "exec", "--", "dprint", "fmt", *targets], check=False)


def _sqruff(targets: list[str]) -> None:
    subprocess.run(["mise", "exec", "--", "sqruff", "fix", *targets], check=False)


def _shfmt(targets: list[str]) -> None:
    subprocess.run(["mise", "exec", "--", "shfmt", "-w", *targets], check=False)


def run_precommit() -> int:
    staged_before = [path for path in _staged_files() if Path(path).is_file()]

    run_fix()

    tree_hash = _tree_hash()
    if tree_hash == _cached_tree_hash():
        status = _replay_cached_report()
        if status:
            _reset_index(staged_before)
        return status

    status = run_check(full=True)
    if status:
        _reset_index(staged_before)
    _TREE_HASH_FILE.parent.mkdir(parents=True, exist_ok=True)
    _TREE_HASH_FILE.write_text(tree_hash, encoding="utf-8")
    return status


def _reset_index(staged_before: list[str]) -> None:
    if staged_before:
        subprocess.run(["git", "reset", "-q", "--", *staged_before], check=True)


def _staged_files() -> list[str]:
    return _git_lines("diff", "--name-only", "--cached")


def _hash_object(path: str) -> str | None:
    result = subprocess.run(
        ["git", "hash-object", path], capture_output=True, text=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else None


_LS_SHA = 1
_LS_PATH = 3


def _index_blobs() -> dict[str, str]:
    result = subprocess.run(
        ["git", "ls-files", "-s"], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        return {}
    blobs: dict[str, str] = {}
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) > _LS_PATH:
            blobs[parts[_LS_PATH]] = parts[_LS_SHA]
    return blobs


def _tree_hash() -> str:
    digest = hashlib.sha256()
    for rel in _git_lines("ls-files"):
        digest.update(rel.encode())
        path = Path(rel)
        if path.is_file():
            digest.update(path.read_bytes())
    return digest.hexdigest()


def _cached_tree_hash() -> str | None:
    if not _TREE_HASH_FILE.is_file() or not REPORT_PATH.is_file():
        return None
    return _TREE_HASH_FILE.read_text(encoding="utf-8")


def _replay_cached_report() -> int:
    data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    outcomes = [
        GateOutcome(
            name=gate["name"],
            passed=gate["status"] == "pass",
            duration_s=gate["duration_s"],
            output=gate["output"],
        )
        for gate in data["gates"]
    ]
    print_verdict(outcomes, REPORT_PATH)
    return 0 if data["passed"] else 1


def _git_lines(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
    )

    return [line for line in result.stdout.splitlines() if line]
