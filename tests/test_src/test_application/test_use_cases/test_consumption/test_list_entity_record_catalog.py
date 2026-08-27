from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

from osint_engine.application.use_cases.consumption.list_entity_record_catalog import (
    ListEntityRecordCatalog,
)

if TYPE_CHECKING:
    from tests.conftest import MakeEntityRecord, MakeMemStorage, MakeMemUoW
    from tests.test_src.test_application.conftest import MakeMemUoWFactory

_EARLY = datetime(2026, 1, 1, tzinfo=UTC)
_LATE = datetime(2026, 6, 1, tzinfo=UTC)


class TestListEntityRecordCatalogOrchestration:
    @pytest.mark.asyncio
    async def test_returns_empty_tuple_when_nothing_was_ever_recorded(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        mem_uow = make_mem_uow(mem_storage=make_mem_storage())

        use_case = ListEntityRecordCatalog(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow)
        )

        assert await use_case.execute() == ()

    @pytest.mark.asyncio
    async def test_returns_records_across_every_entity(
        self,
        make_entity_record: MakeEntityRecord,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        first = make_entity_record(entity_id=uuid4())
        second = make_entity_record(entity_id=uuid4())
        mem_storage = make_mem_storage(entity_records=[first, second])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = ListEntityRecordCatalog(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow)
        )

        found = await use_case.execute()

        assert set(found) == {first, second}

    @pytest.mark.asyncio
    async def test_orders_newest_requested_first(
        self,
        make_entity_record: MakeEntityRecord,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        early = make_entity_record(requested_at=_EARLY)
        late = make_entity_record(requested_at=_LATE)
        mem_storage = make_mem_storage(entity_records=[early, late])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = ListEntityRecordCatalog(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow)
        )

        found = await use_case.execute()

        assert found == (late, early)
