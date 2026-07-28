from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends

from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.presenters.graph_presenter import graph_to_schema
from osint_engine.interface.http.schemas.graph_schema import GraphSchema  # noqa: TC001
from osint_engine.interface.sanitizers import sanitize_cpf

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container


def build_get_cpf_handler(
    *, container: Container
) -> Callable[[str, dict[str, object]], Awaitable[GraphSchema]]:
    jwt_guard = build_jwt_guard(container=container)

    async def get_cpf(
        cpf: str,
        payload: dict[str, object] = Depends(jwt_guard),  # noqa: B008
    ) -> GraphSchema:
        cpf = sanitize_cpf(cpf)
        username = str(payload["sub"])

        use_case = container.use_cases.expand_by_cpf(cpf=cpf, username=username)

        graph = await use_case.execute()

        return graph_to_schema(graph)

    return get_cpf
