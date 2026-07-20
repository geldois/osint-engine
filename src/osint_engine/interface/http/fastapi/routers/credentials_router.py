from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, status

from osint_engine.interface.http.fastapi.routers.handlers.post.post_credential import (
    build_post_credential_handler,
)

if TYPE_CHECKING:
    from osint_engine.config.container import Container


def build_credentials_router(*, container: Container) -> APIRouter:
    router = APIRouter(prefix="/credentials")

    router.post(path="", status_code=status.HTTP_204_NO_CONTENT)(
        build_post_credential_handler(container=container)
    )

    return router
