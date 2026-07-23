from __future__ import annotations

import subprocess
from typing import Literal

from osint_engine.config.settings import Settings


def _migrate(*, direction: Literal["up", "down"]) -> None:
    settings = Settings.from_env()

    subprocess.run(  # noqa: S603
        [  # noqa: S607
            "migrate",
            "-path",
            "migrations",
            "-database",
            settings.database_url,
            direction,
        ],
        check=True,
    )


def migrate_up() -> None:
    _migrate(direction="up")


def migrate_down() -> None:
    _migrate(direction="down")
