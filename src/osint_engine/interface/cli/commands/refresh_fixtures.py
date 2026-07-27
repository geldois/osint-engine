from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def refresh_fixtures_command() -> None:
    script = Path("scripts/refresh_test_source_responses.py")

    subprocess.run([sys.executable, str(script)], check=True) # noqa: S603
