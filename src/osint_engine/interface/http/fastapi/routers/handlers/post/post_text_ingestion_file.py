from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, File, Form, UploadFile

from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.presenters.graph_presenter import graph_to_schema
from osint_engine.interface.http.schemas.graph_schema import GraphSchema  # noqa: TC001

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container


def build_post_text_ingestion_file_handler(
    *, container: Container
) -> Callable[..., Awaitable[GraphSchema]]:
    jwt_guard = build_jwt_guard(container=container)

    async def post_text_ingestion_file(
        file: Annotated[UploadFile, File()],
        patterns: Annotated[list[str], Form()],
        payload: dict[str, object] = Depends(jwt_guard),  # noqa: B008
    ) -> GraphSchema:
        del payload

        content = await file.read(container.services.spreadsheet_max_file_bytes + 1)
        text = container.services.read_spreadsheet_text(
            content=content, filename=file.filename or ""
        )

        use_case = container.use_cases.ingest_text(
            patterns=frozenset(patterns), text=text
        )

        revision = await use_case.execute()
        graph = revision.entity
        matches_graph = await container.use_cases.find_possibly_matches(
            graph=graph
        ).execute()

        if matches_graph is not None:
            revision = replace(revision, entity=graph.merge(other=matches_graph))

        return graph_to_schema(revision)

    return post_text_ingestion_file
