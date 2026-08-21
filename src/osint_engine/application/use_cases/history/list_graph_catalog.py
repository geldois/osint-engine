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

type GraphCatalogEntry = tuple[EntityRevision[Graph], ...]


class ListGraphCatalog(Query[tuple[GraphCatalogEntry, ...]]):
    uow_factory: Callable[[], UoW]

    @override
    def __init__(self, *, uow_factory: Callable[[], UoW]) -> None:
        super().__init__(uow_factory=uow_factory)

    @override
    async def execute(self) -> tuple[GraphCatalogEntry, ...]:
        _logger.info("graph_catalog.list.start")

        async with self.uow_factory() as uow:
            revisions = await uow.graphs.list_all_revisions()

        by_root: dict[UUID, list[EntityRevision[Graph]]] = {}

        for revision in revisions:
            by_root.setdefault(revision.entity.root_id, []).append(revision)

        entries = tuple(
            tuple(sorted(group, key=lambda revision: revision.fetched_at))
            for group in by_root.values()
        )

        ordered = tuple(
            sorted(entries, key=lambda entry: entry[-1].fetched_at, reverse=True)
        )

        _logger.info("graph_catalog.list.success", entry_count=len(ordered))

        return ordered
