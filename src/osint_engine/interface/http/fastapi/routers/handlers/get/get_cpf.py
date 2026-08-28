from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from fastapi import Depends, Response

from osint_engine.domain.errors.sanitization_error import SanitizationError
from osint_engine.domain.services.sanitization import sanitize_cpf
from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.presenters.graph_presenter import graph_to_schema
from osint_engine.interface.http.schemas.graph_schema import GraphSchema  # noqa: TC001

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container


def build_get_cpf_handler(
    *, container: Container
) -> Callable[[str, dict[str, object], bool], Awaitable[GraphSchema | Response]]:
    jwt_guard = build_jwt_guard(container=container)

    async def get_cpf(
        cpf: str,
        payload: dict[str, object] = Depends(jwt_guard),  # noqa: B008
        force: bool = False,  # noqa: FBT001, FBT002
    ) -> GraphSchema | Response:
        username = str(payload["sub"])

        try:
            cpf = sanitize_cpf(cpf)
        except SanitizationError:
            await container.use_cases.record_invalid_attempt(
                provider="cpf", raw_input=cpf, username=username
            ).execute()
            raise

        use_case = container.use_cases.expand_by_cpf(
            cpf=cpf, force=force, username=username
        )

        revision = await use_case.execute()

        if revision is None:
            return Response(status_code=204)

        graph = revision.entity
        matches_graph = await container.use_cases.find_possibly_matches(
            graph=graph
        ).execute()

        if matches_graph is not None:
            revision = replace(revision, entity=graph.merge(other=matches_graph))

        return graph_to_schema(revision)

    return get_cpf
