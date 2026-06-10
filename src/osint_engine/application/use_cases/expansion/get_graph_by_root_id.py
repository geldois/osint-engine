from collections.abc import Callable
from typing import override
from uuid import UUID

from osint_engine.application.contracts.uow import UoW
from osint_engine.application.contracts.use_case import Query
from osint_engine.domain.value_objects.graph import Graph


class GetGraphByRootID(Query[Graph]):
    @override
    def __init__(self, *, uow_factory: Callable[[], UoW], root_id: UUID) -> None:
        self.uow_factory = uow_factory
        self.root_id = root_id

    @override
    async def execute(self) -> Graph:
        async with self.uow_factory() as uow:
            return await uow.graph_repo.get(root_id=self.root_id)
