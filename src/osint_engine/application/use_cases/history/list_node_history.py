from __future__ import annotations

from typing import TYPE_CHECKING, override
from uuid import UUID

from structlog.stdlib import get_logger

from osint_engine.application.contracts.use_case import Query
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.domain.entities.bases.node import Node

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.application.contracts.uow import UoW

_logger = get_logger()


class ListNodeHistory(Query[tuple[EntityRevision[Node[UUID]], ...]]):
    uow_factory: Callable[[], UoW]
    node_id: UUID

    @override
    def __init__(self, *, uow_factory: Callable[[], UoW], node_id: UUID) -> None:
        super().__init__(uow_factory=uow_factory, node_id=node_id)

    @override
    async def execute(self) -> tuple[EntityRevision[Node[UUID]], ...]:
        _logger.info("node_history.list.start", node_id=str(self.node_id))

        async with self.uow_factory() as uow:
            revisions = await uow.nodes.list_revisions(id_=self.node_id)

        ordered = tuple(sorted(revisions, key=lambda revision: revision.fetched_at))

        _logger.info(
            "node_history.list.success",
            node_id=str(self.node_id),
            revision_count=len(ordered),
        )

        return ordered
