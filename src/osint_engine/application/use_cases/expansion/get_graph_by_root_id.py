from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.application.contracts.use_case import Query
from osint_engine.domain.entities.bases.graph import Graph

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from osint_engine.application.contracts.uow import UoW


class GetGraphByGraphID(Query[Graph]):
    @override
    def __init__(self, *, uow_factory: Callable[[], UoW], graph_id: UUID) -> None:
        self.uow_factory = uow_factory
        self.graph_id = graph_id

    @override
    async def execute(self) -> Graph: ...
