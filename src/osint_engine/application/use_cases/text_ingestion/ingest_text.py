from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, override

from structlog.stdlib import get_logger

from osint_engine.application.contracts.use_case import Query
from osint_engine.application.errors.text_ingestion_error import (
    NoPatternMatchedError,
    UnsupportedPatternNodeTypeError,
)
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.application.text_ingestion.extraction import extract_matches
from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.edges.address_mentioned_in_text import (
    AddressMentionedInText,
)
from osint_engine.domain.entities.edges.company_mentioned_in_text import (
    CompanyMentionedInText,
)
from osint_engine.domain.entities.edges.person_mentioned_in_text import (
    PersonMentionedInText,
)
from osint_engine.domain.entities.nodes.address import Address
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.entities.nodes.text_source import TextSource

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from osint_engine.application.contracts.repositories.pattern_set_repository import (
        PatternSetRepository,
    )
    from osint_engine.application.contracts.uow import UoW
    from osint_engine.application.text_ingestion.extraction import ExtractedMatch
    from osint_engine.domain.entities.bases.edge import Edge
    from osint_engine.domain.entities.bases.node import Node
    from osint_engine.domain.entities.nodes.text_source import TextSourceID
    from osint_engine.domain.value_objects.text_pattern import TextPatternName

_logger = get_logger()

_PROVIDER = "text_pattern"


def _build_person_stub(*, field_values: dict[str, str]) -> Person:
    return Person(
        age_range=None,
        birthdate=None,
        cpf=field_values["cpf"],
        name=None,
        registration_date=None,
        registration_status=None,
    )


def _build_company_stub(*, field_values: dict[str, str]) -> Company:
    return Company(
        activity_start_date=None,
        cnpj=field_values["cnpj"],
        is_headquarters=None,
        legal_name=None,
        legal_nature=None,
        registration_status=None,
        registration_status_date=None,
        registration_status_reason=None,
        share_capital=None,
        size_category=None,
        trade_name=None,
    )


def _build_address_stub(*, field_values: dict[str, str]) -> Address:
    return Address(
        cep=field_values["cep"],
        city=None,
        complement=None,
        neighborhood=None,
        number=field_values["number"],
        state=None,
        street=None,
    )


_STUB_BUILDERS: dict[type[Node[UUID]], Callable[..., Node[UUID]]] = {
    Address: _build_address_stub,
    Company: _build_company_stub,
    Person: _build_person_stub,
}


def _build_stub(
    *, node_type: type[Node[UUID]], field_values: dict[str, str]
) -> Node[UUID]:
    builder = _STUB_BUILDERS.get(node_type)

    if builder is None:
        raise UnsupportedPatternNodeTypeError(node_type=node_type)

    return builder(field_values=field_values)


_MENTION_EDGE_BUILDERS: dict[
    type[Node[UUID]], Callable[..., Edge[UUID, UUID, UUID]]
] = {
    Address: AddressMentionedInText,
    Company: CompanyMentionedInText,
    Person: PersonMentionedInText,
}


def _build_mention_edge(
    *,
    node: Node[UUID],
    text_source_id: TextSourceID,
    matched_field: str,
    pattern_name: TextPatternName,
) -> Edge[UUID, UUID, UUID]:
    builder = _MENTION_EDGE_BUILDERS.get(type(node))

    if builder is None:
        raise UnsupportedPatternNodeTypeError(node_type=type(node))

    return builder(
        source_id=node.id,
        target_id=text_source_id,
        matched_field=matched_field,
        pattern_name=pattern_name,
    )


async def _resolve_node(*, uow: UoW, match: ExtractedMatch) -> Node[UUID]:

    field_values = dict(match.field_values)
    stub = _build_stub(node_type=match.node_type, field_values=field_values)

    existing = await uow.nodes.find(id_=stub.id)

    return existing.entity if existing is not None else stub


class IngestText(Query[Graph]):
    uow_factory: Callable[[], UoW]
    pattern_set_repository: PatternSetRepository
    patterns: frozenset[str]
    text: str

    @override
    def __init__(
        self,
        *,
        uow_factory: Callable[[], UoW],
        pattern_set_repository: PatternSetRepository,
        patterns: frozenset[str],
        text: str,
    ) -> None:
        super().__init__(
            uow_factory=uow_factory,
            pattern_set_repository=pattern_set_repository,
            patterns=patterns,
            text=text,
        )

    @override
    async def execute(self) -> Graph:
        _logger.info("text_ingestion.start", patterns=self.patterns)

        pattern_names = await self.pattern_set_repository.resolve(names=self.patterns)
        matches = extract_matches(text=self.text, pattern_names=pattern_names)

        if not matches:
            raise NoPatternMatchedError(requested_patterns=self.patterns)

        fetched_at = datetime.now(tz=UTC)
        text_source = TextSource(text=self.text)

        nodes: set[Node[UUID]] = {text_source}
        edges: set[Edge[UUID, UUID, UUID]] = set()

        async with self.uow_factory() as uow:
            for match in matches:
                node = await _resolve_node(uow=uow, match=match)
                edge = _build_mention_edge(
                    node=node,
                    text_source_id=text_source.id,
                    matched_field=match.matched_field,
                    pattern_name=match.pattern_name,
                )

                nodes.add(node)
                edges.add(edge)

            graph = Graph(
                edges=frozenset(edges), nodes=frozenset(nodes), root_id=text_source.id
            )

            await uow.graphs.merge(
                revision=EntityRevision(
                    entity=graph,
                    fetched_at=fetched_at,
                    merged_at=None,
                    provider=_PROVIDER,
                )
            )

        _logger.info(
            "text_ingestion.success",
            patterns=self.patterns,
            match_count=len(matches),
        )

        return graph
