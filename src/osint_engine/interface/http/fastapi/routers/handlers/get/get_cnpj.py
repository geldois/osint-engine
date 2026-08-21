from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from osint_engine.domain.services.sanitization import sanitize_cnpj
from osint_engine.interface.http.presenters.graph_presenter import graph_to_schema
from osint_engine.interface.http.schemas.graph_schema import GraphSchema  # noqa: TC001

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container


def build_get_cnpj_handler(
    *, container: Container
) -> Callable[[str], Awaitable[GraphSchema]]:
    async def get_cnpj(cnpj: str) -> GraphSchema:
        cnpj = sanitize_cnpj(cnpj)
        use_case = container.use_cases.expand_by_cnpj(cnpj=cnpj)

        revision = await use_case.execute()
        graph = revision.entity
        matches_graph = await container.use_cases.find_possibly_matches(
            graph=graph
        ).execute()

        if matches_graph is not None:
            revision = replace(revision, entity=graph.merge(other=matches_graph))

        return graph_to_schema(revision)

    return get_cnpj
