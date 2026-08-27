from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest

from osint_engine.application.use_cases.consumption.list_entity_records_by_cpf import (
    ListEntityRecordsByCPF,
)
from osint_engine.domain.entities.nodes.person import Person

if TYPE_CHECKING:
    from uuid import UUID

    from tests.conftest import MakeEntityRecord, MakeMemStorage, MakeMemUoW
    from tests.test_src.test_application.conftest import MakeMemUoWFactory

_CPF = "10000000000"
_OTHER_CPF = "20000000000"
_EARLY = datetime(2026, 1, 1, tzinfo=UTC)
_LATE = datetime(2026, 6, 1, tzinfo=UTC)


def _stub_id(cpf: str = _CPF) -> UUID:
    return Person(
        age_range=None,
        birthdate=None,
        cpf=cpf,
        name=None,
        registration_date=None,
        registration_status=None,
    ).id


class TestListEntityRecordsByCPFOrchestration:
    @pytest.mark.asyncio
    async def test_returns_empty_tuple_for_a_cpf_never_recorded(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        mem_uow = make_mem_uow(mem_storage=make_mem_storage())

        use_case = ListEntityRecordsByCPF(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow), cpf=_CPF
        )

        assert await use_case.execute() == ()

    @pytest.mark.asyncio
    async def test_excludes_records_from_a_different_cpf(
        self,
        make_entity_record: MakeEntityRecord,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        matching = make_entity_record(entity_id=_stub_id(_CPF))
        other = make_entity_record(entity_id=_stub_id(_OTHER_CPF))
        mem_storage = make_mem_storage(entity_records=[matching, other])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = ListEntityRecordsByCPF(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow), cpf=_CPF
        )

        assert await use_case.execute() == (matching,)

    @pytest.mark.asyncio
    async def test_includes_blocked_attempts_alongside_expanded_ones(
        self,
        make_entity_record: MakeEntityRecord,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        entity_id = _stub_id()
        expanded = make_entity_record(
            entity_id=entity_id, outcome="expanded", entity_ref=None
        )
        blocked = make_entity_record(
            entity_id=entity_id, outcome="already_fetched", entity_ref=None
        )
        mem_storage = make_mem_storage(entity_records=[expanded, blocked])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = ListEntityRecordsByCPF(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow), cpf=_CPF
        )

        found = await use_case.execute()

        assert set(found) == {expanded, blocked}

    @pytest.mark.asyncio
    async def test_orders_by_requested_at_regardless_of_insertion_order(
        self,
        make_entity_record: MakeEntityRecord,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        entity_id = _stub_id()
        early = make_entity_record(entity_id=entity_id, requested_at=_EARLY)
        late = make_entity_record(entity_id=entity_id, requested_at=_LATE)
        mem_storage = make_mem_storage(entity_records=[late, early])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = ListEntityRecordsByCPF(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow), cpf=_CPF
        )

        found = await use_case.execute()

        assert found == (early, late)
