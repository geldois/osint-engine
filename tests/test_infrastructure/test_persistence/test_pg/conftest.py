from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol, cast

import asyncpg
import pytest
import pytest_asyncio
from docker import from_env
from docker.errors import DockerException
from testcontainers.postgres import PostgresContainer

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator


class _DockerClient(Protocol):
    def ping(self) -> bool: ...

    def close(self) -> None: ...


@pytest.fixture(scope="session")
def postgres_url() -> Iterator[str]:
    try:
        docker_client = cast("_DockerClient", from_env())
        docker_client.ping()
    except DockerException as error:
        pytest.skip(f"Docker is unavailable: {error}")
    else:
        docker_client.close()

    with PostgresContainer("postgres:18") as postgres:
        connection_url = postgres.get_connection_url()

        yield connection_url.replace("postgresql+psycopg2://", "postgresql://", 1)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def postgres_pool(postgres_url: str) -> AsyncIterator[asyncpg.Pool]:
    async with asyncpg.create_pool(  # pyright: ignore[reportUnknownMemberType]
        dsn=postgres_url
    ) as pool:
        migration_path = (
            Path(__file__).parents[4]
            / "migrations"
            / "000001_create_external_credentials.up.sql"
        )

        await pool.execute(  # pyright: ignore[reportUnknownMemberType]
            migration_path.read_text(encoding="utf-8")
        )

        yield pool


@pytest_asyncio.fixture(autouse=True)
async def clean_external_credentials(
    postgres_pool: asyncpg.Pool,
) -> AsyncIterator[None]:
    await postgres_pool.execute(  # pyright: ignore[reportUnknownMemberType]
        "TRUNCATE TABLE external_credentials"
    )

    yield
