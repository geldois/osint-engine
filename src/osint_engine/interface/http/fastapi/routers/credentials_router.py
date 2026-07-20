from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, status

from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.fastapi.routers.handlers.post.post_credential import (
    build_post_credential_handler,
)

if TYPE_CHECKING:
    from osint_engine.config.container import Container


def build_credentials_router(*, container: Container) -> APIRouter:
    jwt_guard = build_jwt_guard(container=container)

    router = APIRouter(prefix="/credentials", dependencies=[Depends(jwt_guard)])

    router.post(path="", status_code=status.HTTP_204_NO_CONTENT)(
        build_post_credential_handler(container=container)
    )

    return router
