from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from osint_engine.interface.http.fastapi.error_handler import build_error_handler
from osint_engine.interface.http.fastapi.middlewares.logging_handler import (
    handle_logging,
)
from osint_engine.interface.http.fastapi.routers.auth_router import build_auth_router
from osint_engine.interface.http.fastapi.routers.cnpj_router import build_cnpj_router

if TYPE_CHECKING:
    from osint_engine.config.container import Container


def build_fastapi_app(*, container: Container) -> FastAPI:
    fastapi_app = FastAPI()

    fastapi_app.include_router(router=build_auth_router(container=container))
    fastapi_app.include_router(router=build_cnpj_router(container=container))

    fastapi_app.add_exception_handler(
        exc_class_or_status_code=Exception,
        handler=build_error_handler(container=container),
    )

    fastapi_app.middleware(middleware_type="http")(handle_logging)

    fastapi_app.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=container.settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return fastapi_app
