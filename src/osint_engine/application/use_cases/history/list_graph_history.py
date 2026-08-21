from __future__ import annotations

from typing import TYPE_CHECKING, override

from structlog.stdlib import get_logger

from osint_engine.application.contracts.use_case import Query
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.domain.entities.bases.graph import Graph

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from osint_engine.application.contracts.uow import UoW

_logger = get_logger()


class ListGraphHistory(Query[tuple[EntityRevision[Graph], ...]]):
    uow_factory: Callable[[], UoW]
    root_id: UUID

    @override
    def __init__(self, *, uow_factory: Callable[[], UoW], root_id: UUID) -> None:
        super().__init__(uow_factory=uow_factory, root_id=root_id)

    @override
    async def execute(self) -> tuple[EntityRevision[Graph], ...]:
        _logger.info("graph_history.list.start", root_id=str(self.root_id))

        async with self.uow_factory() as uow:
            revisions = await uow.graphs.list_revisions_by_root(root_id=self.root_id)

        ordered = tuple(sorted(revisions, key=lambda revision: revision.fetched_at))

        _logger.info(
            "graph_history.list.success",
            root_id=str(self.root_id),
            revision_count=len(ordered),
        )

        return ordered
