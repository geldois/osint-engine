from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.interface.http.presenters.graph_presenter import graph_to_schema
from osint_engine.interface.http.schemas.graph_schema import GraphSchema  # noqa: TC001

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container


def build_get_cnpj_handler(
    *, container: Container
) -> Callable[[str], Awaitable[GraphSchema]]:
    async def get_cnpj(cnpj: str) -> GraphSchema:
        use_case = container.use_cases.expand_by_cnpj(cnpj=cnpj)

        graph = await use_case.execute()

        return graph_to_schema(graph)

    return get_cnpj
