from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.fastapi.rate_limit import build_expansion_rate_limit
from osint_engine.interface.http.fastapi.routers.handlers.get.get_text_patterns import (
    build_get_text_patterns_handler,
)
from osint_engine.interface.http.fastapi.routers.handlers.post.post_text_ingestion import (  # noqa: E501
    build_post_text_ingestion_handler,
)

if TYPE_CHECKING:
    from osint_engine.config.container import Container


def build_text_ingestion_router(*, container: Container) -> APIRouter:
    jwt_guard = build_jwt_guard(container=container)
    rate_limit = build_expansion_rate_limit(scope="text_ingestion")

    router = APIRouter(
        prefix="/text-ingestion", dependencies=[Depends(jwt_guard), Depends(rate_limit)]
    )

    router.get(path="/patterns")(build_get_text_patterns_handler(container=container))
    router.post(path="")(build_post_text_ingestion_handler(container=container))

    return router
