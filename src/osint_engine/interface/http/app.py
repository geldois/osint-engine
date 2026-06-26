from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import FastAPI
from uvicorn import Config, Server

from osint_engine.interface.http.errors.handlers.error_handler import (
    build_error_handler,
)
from osint_engine.interface.http.routers.cnpj_router import build_cnpj_router
from osint_engine.observability.middlewares.http_middleware import http_middleware

if TYPE_CHECKING:
    from osint_engine.config.container import Container
    from osint_engine.config.settings import Settings


def create_app(*, container: Container) -> FastAPI:
    app = FastAPI()

    app.middleware(middleware_type="http")(http_middleware)

    app.add_exception_handler(Exception, build_error_handler(container=container))

    cnpj_router = build_cnpj_router(container=container)

    app.include_router(router=cnpj_router)

    return app


async def serve(app: FastAPI, settings: Settings) -> None:
    config = Config(
        app=app, host=settings.host, port=settings.port, log_level=settings.log_level
    )
    server = Server(config=config)

    await server.serve()
