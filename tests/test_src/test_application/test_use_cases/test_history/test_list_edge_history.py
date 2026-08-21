from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import pytest

from osint_engine.application.use_cases.history.list_edge_history import (
    ListEdgeHistory,
)
from osint_engine.domain.entities.edges.possibly_matches import PossiblyMatches

if TYPE_CHECKING:
    from tests.conftest import (
        MakeEntityRevision,
        MakeFakeEdge,
        MakeMemStorage,
        MakeMemUoW,
    )
    from tests.test_src.test_application.conftest import MakeMemUoWFactory


_EARLY = datetime(2026, 1, 1, tzinfo=UTC)
_LATE = datetime(2026, 6, 1, tzinfo=UTC)


def _make_possibly_matches(*, confidence: Decimal) -> PossiblyMatches[UUID]:
    return PossiblyMatches(source_id=uuid4(), target_id=uuid4(), confidence=confidence)


class TestListEdgeHistoryOrchestration:
    @pytest.mark.asyncio
    async def test_returns_empty_tuple_for_an_unknown_edge_id(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        mem_uow = make_mem_uow(mem_storage=make_mem_storage())

        use_case = ListEdgeHistory(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow), edge_id=uuid4()
        )

        assert await use_case.execute() == ()

    @pytest.mark.asyncio
    async def test_orders_two_observations_by_fetched_at_and_each_carries_its_own_revision(  # noqa: E501
        self,
        make_entity_revision: MakeEntityRevision,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        edge = _make_possibly_matches(confidence=Decimal("0.5"))
        early = make_entity_revision(entity=edge, fetched_at=_EARLY)
        late = make_entity_revision(
            entity=PossiblyMatches(
                source_id=edge.source_id,
                target_id=edge.target_id,
                confidence=Decimal("0.9"),
            ),
            fetched_at=_LATE,
        )
        assert early.entity.id == late.entity.id
        assert early.entity.content_id != late.entity.content_id

        mem_storage = make_mem_storage(edges=[late, early])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = ListEdgeHistory(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow), edge_id=early.entity.id
        )

        history = await use_case.execute()

        assert history == (early, late)
        assert history[0].fetched_at != history[1].fetched_at

    @pytest.mark.asyncio
    async def test_excludes_observations_of_a_different_edge(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_edge: MakeFakeEdge,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        matching = make_entity_revision(entity=make_fake_edge())
        other = make_entity_revision(entity=make_fake_edge())
        mem_storage = make_mem_storage(edges=[matching, other])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = ListEdgeHistory(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            edge_id=matching.entity.id,
        )

        history = await use_case.execute()

        assert history == (matching,)
