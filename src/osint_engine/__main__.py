from __future__ import annotations

import asyncio

from httpx2 import AsyncClient, Timeout

from osint_engine.config.croot import build_container
from osint_engine.config.settings import Settings
from osint_engine.interface.http.app import create_app, serve
from osint_engine.observability.logging import configure_logging


def _build_http_client(*, settings: Settings) -> AsyncClient:
    timeout = Timeout(
        timeout=None,
        connect=settings.fetcher_connect_timeout,
        read=settings.fetcher_read_timeout,
    )

    return AsyncClient(timeout=timeout)


async def main() -> None:
    settings = Settings.from_env()

    configure_logging(debug=settings.debug)

    async with _build_http_client(settings=settings) as http_client:
        container = build_container(settings=settings, http_client=http_client)

        app = create_app(container=container)

        await serve(app=app, settings=settings)


if __name__ == "__main__":
    asyncio.run(main=main())
