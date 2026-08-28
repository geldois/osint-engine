from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from osint_engine.domain.errors.sanitization_error import SanitizationError
from osint_engine.domain.services.sanitization import sanitize_cnpj
from osint_engine.interface.http.presenters.graph_presenter import graph_to_schema
from osint_engine.interface.http.schemas.graph_schema import GraphSchema  # noqa: TC001

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container

_ANONYMOUS_USERNAME = "anonymous"


def build_get_cnpj_handler(
    *, container: Container
) -> Callable[[str], Awaitable[GraphSchema]]:
    async def get_cnpj(cnpj: str) -> GraphSchema:
        try:
            cnpj = sanitize_cnpj(cnpj)
        except SanitizationError:
            await container.use_cases.record_invalid_attempt(
                provider="brasilapi", raw_input=cnpj, username=_ANONYMOUS_USERNAME
            ).execute()
            raise

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
