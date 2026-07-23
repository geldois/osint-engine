from __future__ import annotations

import asyncio
from time import monotonic

import asyncpg

from osint_engine.config.settings import Settings

_TIMEOUT_SECONDS = 30.0
_POLL_INTERVAL_SECONDS = 0.5


async def _wait_db() -> None:
    settings = Settings.from_env()
    deadline = monotonic() + _TIMEOUT_SECONDS

    while True:
        try:
            connection = await asyncpg.connect(  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
                dsn=settings.database_url
            )
        except (OSError, asyncpg.PostgresError) as error:
            if monotonic() >= deadline:
                message = (
                    f"Postgres did not become reachable within "
                    f"{_TIMEOUT_SECONDS}s at {settings.database_url!r}"
                )

                raise TimeoutError(message) from error

            await asyncio.sleep(_POLL_INTERVAL_SECONDS)
        else:
            await connection.close()  # pyright: ignore[reportUnknownMemberType]

            return


def wait_db_command() -> None:
    asyncio.run(_wait_db())
