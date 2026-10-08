from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, status

from osint_engine.interface.http.fastapi.rate_limit import (
    build_auth_token_rate_limit,
    build_register_rate_limit,
)
from osint_engine.interface.http.fastapi.routers.handlers.post.post_register import (
    build_post_register_handler,
)
from osint_engine.interface.http.fastapi.routers.handlers.post.post_token import (
    build_post_token_handler,
)

if TYPE_CHECKING:
    from osint_engine.config.container import Container


def build_auth_router(*, container: Container) -> APIRouter:
    router = APIRouter(prefix="/auth")

    router.post(path="/token", dependencies=[Depends(build_auth_token_rate_limit())])(
        build_post_token_handler(container=container)
    )
    router.post(
        path="/register",
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(build_register_rate_limit())],
    )(build_post_register_handler(container=container))

    return router
