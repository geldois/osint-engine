from __future__ import annotations

from typing import TYPE_CHECKING, override
from uuid import UUID

from structlog.stdlib import get_logger

from osint_engine.application.contracts.use_case import Query
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.domain.entities.bases.edge import Edge

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.application.contracts.uow import UoW

_logger = get_logger()


class ListEdgeHistory(Query[tuple[EntityRevision[Edge[UUID, UUID, UUID]], ...]]):
    uow_factory: Callable[[], UoW]
    edge_id: UUID

    @override
    def __init__(self, *, uow_factory: Callable[[], UoW], edge_id: UUID) -> None:
        super().__init__(uow_factory=uow_factory, edge_id=edge_id)

    @override
    async def execute(self) -> tuple[EntityRevision[Edge[UUID, UUID, UUID]], ...]:
        _logger.info("edge_history.list.start", edge_id=str(self.edge_id))

        async with self.uow_factory() as uow:
            revisions = await uow.edges.list_revisions(id_=self.edge_id)

        ordered = tuple(sorted(revisions, key=lambda revision: revision.fetched_at))

        _logger.info(
            "edge_history.list.success",
            edge_id=str(self.edge_id),
            revision_count=len(ordered),
        )

        return ordered
