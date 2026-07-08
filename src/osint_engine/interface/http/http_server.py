from __future__ import annotations

from typing import TYPE_CHECKING

from uvicorn import Config, Server

if TYPE_CHECKING:
    from starlette.types import ASGIApp

    from osint_engine.config.settings import Settings


async def serve(app: ASGIApp, settings: Settings) -> None:
    config = Config(
        app=app, host=settings.host, port=settings.port, log_level=settings.log_level
    )
    server = Server(config=config)

    await server.serve()
