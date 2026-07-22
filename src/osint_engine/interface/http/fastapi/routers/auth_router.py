from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from osint_engine.interface.http.fastapi.rate_limit import (
    build_auth_token_rate_limit,
    build_viewer_token_rate_limit,
)
from osint_engine.interface.http.fastapi.routers.handlers.post.post_token import (
    build_post_token_handler,
)
from osint_engine.interface.http.fastapi.routers.handlers.post.post_viewer_token import (  # noqa: E501
    build_post_viewer_token_handler,
)

if TYPE_CHECKING:
    from osint_engine.config.container import Container


def build_auth_router(*, container: Container) -> APIRouter:
    router = APIRouter(prefix="/auth")

    router.post(path="/token", dependencies=[Depends(build_auth_token_rate_limit())])(
        build_post_token_handler(container=container)
    )
    router.post(
        path="/viewer-token", dependencies=[Depends(build_viewer_token_rate_limit())]
    )(build_post_viewer_token_handler(container=container))

    return router
