from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.fastapi.rate_limit import build_expansion_rate_limit
from osint_engine.interface.http.fastapi.routers.handlers.get.get_node_history import (
    build_get_node_history_handler,
)

if TYPE_CHECKING:
    from osint_engine.config.container import Container


def build_node_router(*, container: Container) -> APIRouter:
    jwt_guard = build_jwt_guard(container=container)
    rate_limit = build_expansion_rate_limit(scope="node_history")

    router = APIRouter(
        prefix="/nodes", dependencies=[Depends(jwt_guard), Depends(rate_limit)]
    )

    router.get(path="/{node_id}/history")(
        build_get_node_history_handler(container=container)
    )

    return router
