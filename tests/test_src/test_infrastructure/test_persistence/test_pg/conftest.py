from __future__ import annotations

from os import environ
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, cast

import asyncpg
import pytest
import pytest_asyncio
from docker import from_env
from testcontainers.postgres import PostgresContainer

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator


class _DockerClient(Protocol):
    def ping(self) -> bool: ...

    def close(self) -> None: ...


def _ensure_docker_host() -> None:
    """Point the Docker API client at a running Podman socket when there is no Docker.

    testcontainers talks to the Docker API socket, never the CLI, so a Podman
    install exposed only through a `docker` shim reads as "Docker is
    unavailable" and silently skips every integration test. Real Docker and an
    explicit DOCKER_HOST are both left untouched.
    """
    if environ.get("DOCKER_HOST") or Path("/var/run/docker.sock").exists():
        return

    runtime = environ.get("XDG_RUNTIME_DIR")
    if not runtime:
        return

    socket = Path(runtime) / "podman" / "podman.sock"
    if socket.exists():
        environ["DOCKER_HOST"] = f"unix://{socket}"


def _project_root() -> Path:
    for candidate in Path(__file__).parents:
        if (candidate / "pyproject.toml").is_file():
            return candidate
    message = "no pyproject.toml above this test file"
    raise RuntimeError(message)


@pytest.fixture(scope="session")
def postgres_url() -> Iterator[str]:
    _ensure_docker_host()
    # A container runtime is a documented setup requirement, so its absence is
    # a broken environment, not an optional test. from_env() raising here is
    # the report — louder and more diagnostic than a skip.
    docker_client = cast("_DockerClient", from_env())
    docker_client.ping()
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
            _project_root() / "migrations" / "000001_create_external_credentials.up.sql"
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
