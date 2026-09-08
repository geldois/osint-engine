from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from structlog.stdlib import get_logger

from osint_engine.application.consumption.guard_reuse_lock import (
    ALREADY_FETCHED_OUTCOMES,
)
from osint_engine.application.contracts.use_case import Query

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from osint_engine.application.contracts.uow import UoW
    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.domain.entities.bases.graph import Graph

_logger = get_logger()


@dataclass(eq=True, frozen=True, kw_only=True)
class GraphCatalogEntry:
    fetched_routes: frozenset[str]
    revisions: tuple[EntityRevision[Graph], ...]


class ListGraphCatalog(Query[tuple[GraphCatalogEntry, ...]]):
    uow_factory: Callable[[], UoW]

    @override
    def __init__(self, *, uow_factory: Callable[[], UoW]) -> None:
        super().__init__(uow_factory=uow_factory)

    @override
    async def execute(self) -> tuple[GraphCatalogEntry, ...]:
        _logger.info("graph_catalog.list.start")

        entries: list[GraphCatalogEntry] = []

        async with self.uow_factory() as uow:
            revisions = await uow.graphs.list_all_revisions()

            by_root: dict[UUID, list[EntityRevision[Graph]]] = {}

            for revision in revisions:
                by_root.setdefault(revision.entity.root_id, []).append(revision)

            for root_id, group in by_root.items():
                entity_records = await uow.entity_records.list_by_entity_id(
                    entity_id=root_id
                )
                fetched_routes = frozenset(
                    record.provider
                    for record in entity_records
                    if record.outcome in ALREADY_FETCHED_OUTCOMES
                )
                sorted_group = tuple(
                    sorted(group, key=lambda revision: revision.fetched_at)
                )

                entries.append(
                    GraphCatalogEntry(
                        fetched_routes=fetched_routes, revisions=sorted_group
                    )
                )

        ordered = tuple(
            sorted(
                entries,
                key=lambda entry: entry.revisions[-1].fetched_at,
                reverse=True,
            )
        )

        _logger.info("graph_catalog.list.success", entry_count=len(ordered))

        return ordered
