from __future__ import annotations

import subprocess
from pathlib import Path

_GENERATED_DIR = Path("src/osint_engine/infrastructure/persistence/pg/generated")
_KEEP = {"models.py", "__init__.py"}


def run_sqlc_generate() -> int:
    result = subprocess.run(["mise", "exec", "--", "sqlc", "generate"], check=False)
    if result.returncode != 0:
        return result.returncode

    for generated_file in _GENERATED_DIR.glob("*.py"):
        if generated_file.name not in _KEEP:
            generated_file.unlink()

    (_GENERATED_DIR / "__init__.py").touch()

    return 0
