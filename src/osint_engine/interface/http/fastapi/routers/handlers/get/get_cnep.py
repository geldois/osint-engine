from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends

from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.presenters.graph_presenter import graph_to_schema
from osint_engine.interface.http.schemas.graph_schema import GraphSchema  # noqa: TC001
from osint_engine.interface.sanitizers import sanitize_cpf_or_cnpj

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container


def build_get_cnep_handler(
    *, container: Container
) -> Callable[[str, dict[str, object], int | None], Awaitable[GraphSchema]]:
    jwt_guard = build_jwt_guard(container=container)

    async def get_cnep(
        cpf_or_cnpj: str,
        payload: dict[str, object] = Depends(jwt_guard),  # noqa: B008
        cnep_id: int | None = None,
    ) -> GraphSchema:
        cpf_or_cnpj = sanitize_cpf_or_cnpj(cpf_or_cnpj)
        username = str(payload["sub"])

        use_case = container.use_cases.expand_by_cnep(
            cpf_or_cnpj=cpf_or_cnpj, cnep_id=cnep_id, username=username
        )

        graph = await use_case.execute()

        return graph_to_schema(graph)

    return get_cnep
