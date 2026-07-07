"""
Runs all maintenance scripts.

Usage: uv run python scripts/
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    scripts_dir = Path(__file__).parent

    for script in sorted(scripts_dir.glob("*.py")):
        if script.name.startswith("_"):
            continue

        print(f"\n── {script.name} ──")

        subprocess.run([sys.executable, script], check=True)  # noqa: S603


if __name__ == "__main__":
    main()
