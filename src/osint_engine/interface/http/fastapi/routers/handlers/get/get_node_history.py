from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from fastapi import Depends

from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.presenters.node_presenter import (
    node_history_to_schema,
)
from osint_engine.interface.http.schemas.node_schema import NodeUnion  # noqa: TC001

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container


def build_get_node_history_handler(
    *, container: Container
) -> Callable[[UUID, dict[str, object]], Awaitable[list[NodeUnion]]]:
    jwt_guard = build_jwt_guard(container=container)

    async def get_node_history(
        node_id: UUID,
        payload: dict[str, object] = Depends(jwt_guard),  # noqa: B008
    ) -> list[NodeUnion]:
        del payload

        use_case = container.use_cases.list_node_history(node_id=node_id)

        revisions = await use_case.execute()

        return node_history_to_schema(revisions)

    return get_node_history
