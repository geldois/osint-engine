from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter

from osint_engine.interface.http.routers.handlers.post.post_token import (
    build_post_token_handler,
)

if TYPE_CHECKING:
    from osint_engine.config.container import Container


def build_auth_router(*, container: Container) -> APIRouter:
    router = APIRouter(prefix="/auth")

    router.post(path="/token")(build_post_token_handler(container=container))

    return router
