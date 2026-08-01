from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, override

from rapidfuzz import fuzz
from structlog.stdlib import get_logger

from osint_engine.application.contracts.use_case import Query
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.edges.possibly_matches import PossiblyMatches
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.person import Person

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from osint_engine.application.contracts.uow import UoW
    from osint_engine.domain.entities.bases.node import Node

_logger = get_logger()

_SOURCE = "fuzzy_match"
_MIN_CONFIDENCE_SCORE = 92

_NAME_FIELDS: dict[type[Node[UUID]], tuple[str, ...]] = {
    Company: ("legal_name", "trade_name"),
    Person: ("name",),
}


def _extract_name(*, node: Node[UUID]) -> str | None:
    fields = _NAME_FIELDS.get(type(node))

    if fields is None:
        return None

    for field in fields:
        value = getattr(node, field)

        if value:
            return str(value).strip().upper()

    return None


class FindPossiblyMatches(Query[Graph | None]):
    uow_factory: Callable[[], UoW]
    graph: Graph

    @override
    def __init__(self, *, uow_factory: Callable[[], UoW], graph: Graph) -> None:
        super().__init__(uow_factory=uow_factory, graph=graph)

    @override
    async def execute(self) -> Graph | None:
        matches: set[PossiblyMatches[UUID]] = set()
        matched_nodes: set[Node[UUID]] = set()
        candidates_by_type: dict[
            type[Node[UUID]], tuple[EntityRevision[Node[UUID]], ...]
        ] = {}

        async with self.uow_factory() as uow:
            for node in self.graph.nodes:
                name = _extract_name(node=node)

                if name is None:
                    continue

                node_type = type(node)

                if node_type not in candidates_by_type:
                    candidates_by_type[node_type] = await uow.nodes.list_by_type(
                        node_type=node_type
                    )

                for candidate_revision in candidates_by_type[node_type]:
                    candidate = candidate_revision.entity

                    if candidate.id == node.id:
                        continue

                    candidate_name = _extract_name(node=candidate)

                    if candidate_name is None:
                        continue

                    score = round(fuzz.token_sort_ratio(name, candidate_name), 2)

                    if score < _MIN_CONFIDENCE_SCORE:
                        continue

                    matches.add(
                        PossiblyMatches(
                            source_id=node.id,
                            target_id=candidate.id,
                            confidence=Decimal(str(score)) / 100,
                        )
                    )
                    matched_nodes.add(node)
                    matched_nodes.add(candidate)

            if not matches:
                return None

            fetched_at = datetime.now(tz=UTC)

            await uow.edges.merge_many(
                revisions=frozenset(
                    EntityRevision(
                        entity=match,
                        fetched_at=fetched_at,
                        merged_at=None,
                        source=_SOURCE,
                    )
                    for match in matches
                )
            )

        _logger.info("possibly_matches.found", match_count=len(matches))

        anchor = next(iter(matched_nodes))

        return Graph(
            edges=frozenset(matches), nodes=frozenset(matched_nodes), root_id=anchor.id
        )
