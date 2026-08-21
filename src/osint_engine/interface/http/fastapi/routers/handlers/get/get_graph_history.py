from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from fastapi import Depends

from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.presenters.graph_presenter import graph_to_schema
from osint_engine.interface.http.schemas.graph_schema import GraphSchema  # noqa: TC001

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container


def build_get_graph_history_handler(
    *, container: Container
) -> Callable[[UUID, dict[str, object]], Awaitable[list[GraphSchema]]]:
    jwt_guard = build_jwt_guard(container=container)

    async def get_graph_history(
        root_id: UUID,
        payload: dict[str, object] = Depends(jwt_guard),  # noqa: B008
    ) -> list[GraphSchema]:
        del payload

        use_case = container.use_cases.list_graph_history(root_id=root_id)

        revisions = await use_case.execute()

        return [graph_to_schema(revision) for revision in revisions]

    return get_graph_history
