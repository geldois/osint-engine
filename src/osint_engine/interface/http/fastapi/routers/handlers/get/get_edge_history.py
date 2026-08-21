from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from fastapi import Depends

from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.presenters.edge_presenter import (
    edge_history_to_schema,
)
from osint_engine.interface.http.schemas.edge_schema import EdgeUnion  # noqa: TC001

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container


def build_get_edge_history_handler(
    *, container: Container
) -> Callable[[UUID, dict[str, object]], Awaitable[list[EdgeUnion]]]:
    jwt_guard = build_jwt_guard(container=container)

    async def get_edge_history(
        edge_id: UUID,
        payload: dict[str, object] = Depends(jwt_guard),  # noqa: B008
    ) -> list[EdgeUnion]:
        del payload

        use_case = container.use_cases.list_edge_history(edge_id=edge_id)

        revisions = await use_case.execute()

        return edge_history_to_schema(revisions)

    return get_edge_history
