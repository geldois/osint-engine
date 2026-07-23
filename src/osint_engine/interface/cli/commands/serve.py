from __future__ import annotations

import asyncio

import asyncpg
from httpx2 import AsyncClient, Timeout

from osint_engine.config.croot import build_container
from osint_engine.config.settings import Settings
from osint_engine.interface.http.fastapi.fastapi import build_fastapi_app
from osint_engine.interface.http.http_server import serve as serve_http
from osint_engine.observability.structlog.config import configure_logging


def _build_http_client(*, settings: Settings) -> AsyncClient:
    timeout = Timeout(
        timeout=None,
        connect=settings.fetcher_connect_timeout,
        read=settings.fetcher_read_timeout,
    )

    return AsyncClient(timeout=timeout)


async def _serve() -> None:
    settings = Settings.from_env()

    configure_logging(debug=settings.debug)

    async with (
        _build_http_client(settings=settings) as http_client,
        asyncpg.create_pool(  # pyright: ignore[reportUnknownMemberType]
            dsn=settings.database_url
        ) as pg_pool,
    ):
        container = build_container(
            settings=settings,
            http_client=http_client,
            pg_pool=pg_pool,
            external_credential_encryption_key=(
                settings.external_credential_encryption_key
            ),
        )
        fastapi_app = build_fastapi_app(container=container)

        await serve_http(app=fastapi_app, settings=settings)


def serve_command() -> None:
    asyncio.run(_serve())
