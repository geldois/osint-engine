from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends

from osint_engine.domain.value_objects.pattern_set_id import PatternSetID
from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.presenters.graph_presenter import graph_to_schema
from osint_engine.interface.http.schemas.graph_schema import GraphSchema  # noqa: TC001
from osint_engine.interface.http.schemas.text_ingestion_schema import (  # noqa: TC001
    IngestTextRequestSchema,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container


def build_post_text_ingestion_handler(
    *, container: Container
) -> Callable[[IngestTextRequestSchema, dict[str, object]], Awaitable[GraphSchema]]:
    jwt_guard = build_jwt_guard(container=container)

    async def post_text_ingestion(
        body: IngestTextRequestSchema,
        payload: dict[str, object] = Depends(jwt_guard),  # noqa: B008
    ) -> GraphSchema:
        del payload

        use_case = container.use_cases.ingest_text(
            pattern_set_id=PatternSetID(body.pattern_set_id), text=body.text
        )

        graph = await use_case.execute()
        matches_graph = await container.use_cases.find_possibly_matches(
            graph=graph
        ).execute()

        if matches_graph is not None:
            graph = graph.merge(other=matches_graph)

        return graph_to_schema(graph)

    return post_text_ingestion
