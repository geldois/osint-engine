from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.fastapi.rate_limit import build_expansion_rate_limit
from osint_engine.interface.http.fastapi.routers.handlers.get.get_graph_catalog import (
    build_get_graph_catalog_handler,
)
from osint_engine.interface.http.fastapi.routers.handlers.get.get_graph_history import (
    build_get_graph_history_handler,
)

if TYPE_CHECKING:
    from osint_engine.config.container import Container


def build_graph_router(*, container: Container) -> APIRouter:
    jwt_guard = build_jwt_guard(container=container)
    rate_limit = build_expansion_rate_limit(scope="graph_catalog")

    router = APIRouter(
        prefix="/graphs", dependencies=[Depends(jwt_guard), Depends(rate_limit)]
    )

    router.get(path="")(build_get_graph_catalog_handler(container=container))

    router.get(path="/{root_id}/history")(
        build_get_graph_history_handler(container=container)
    )

    return router
