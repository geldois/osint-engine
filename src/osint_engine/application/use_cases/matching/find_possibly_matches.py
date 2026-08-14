from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, override

from structlog.stdlib import get_logger

from osint_engine.application.contracts.use_case import Query
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.edges.possibly_matches import PossiblyMatches
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.errors.document_error import InvalidMaskedDocumentError
from osint_engine.domain.services.masked_document_matching import (
    masked_document_overlap,
)
from osint_engine.domain.services.normalization import normalize_masked_document

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from osint_engine.application.contracts.uow import UoW
    from osint_engine.domain.entities.bases.node import Node

_logger = get_logger()

_PROVIDER = "masked_document_overlap"

_DOCUMENT_FIELDS: dict[type[Node[UUID]], str] = {
    Person: "cpf",
}


def _extract_document(*, node: Node[UUID]) -> str | None:
    field = _DOCUMENT_FIELDS.get(type(node))

    if field is None:
        return None

    value = getattr(node, field)

    if not value:
        return None

    try:
        return normalize_masked_document(value=str(value))
    except InvalidMaskedDocumentError:
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
                document = _extract_document(node=node)

                if document is None:
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

                    candidate_document = _extract_document(node=candidate)

                    if candidate_document is None:
                        continue

                    overlap = masked_document_overlap(
                        left=document, right=candidate_document
                    )

                    if overlap is None:
                        continue

                    matches.add(
                        PossiblyMatches(
                            source_id=node.id,
                            target_id=candidate.id,
                            confidence=Decimal(overlap) / Decimal(len(document)),
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
                        provider=_PROVIDER,
                    )
                    for match in matches
                )
            )

        _logger.info("possibly_matches.found", match_count=len(matches))

        anchor = min(matched_nodes, key=lambda node: node.id)

        return Graph(
            edges=frozenset(matches), nodes=frozenset(matched_nodes), root_id=anchor.id
        )
