from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends

from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.presenters.graph_presenter import (
    graph_catalog_to_schema,
)
from osint_engine.interface.http.schemas.graph_catalog_schema import (  # noqa: TC001
    GraphCatalogSchema,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container


def build_get_graph_catalog_handler(
    *, container: Container
) -> Callable[[dict[str, object]], Awaitable[GraphCatalogSchema]]:
    jwt_guard = build_jwt_guard(container=container)

    async def get_graph_catalog(
        payload: dict[str, object] = Depends(jwt_guard),  # noqa: B008
    ) -> GraphCatalogSchema:
        del payload

        use_case = container.use_cases.list_graph_catalog()

        entries = await use_case.execute()

        return graph_catalog_to_schema(entries)

    return get_graph_catalog
