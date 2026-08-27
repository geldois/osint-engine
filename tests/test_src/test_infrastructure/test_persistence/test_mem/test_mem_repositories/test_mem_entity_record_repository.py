from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

if TYPE_CHECKING:
    from tests.conftest import MakeEntityRecord, MakeMemStorage
    from tests.test_src.test_infrastructure.test_persistence.test_mem.test_mem_repositories.conftest import (  # noqa: E501
        MakeMemEntityRecordRepository,
    )


class TestMemEntityRecordRepositorySave:
    @pytest.mark.asyncio
    async def test_appends_to_the_backing_storage(
        self,
        make_entity_record: MakeEntityRecord,
        make_mem_storage: MakeMemStorage,
        make_mem_entity_record_repository: MakeMemEntityRecordRepository,
    ) -> None:
        mem_storage = make_mem_storage()
        repo = make_mem_entity_record_repository(mem_storage=mem_storage)
        record = make_entity_record()

        returned = await repo.save(record=record)

        assert returned is record
        assert mem_storage.entity_records == [record]

    @pytest.mark.asyncio
    async def test_never_overwrites_an_earlier_record_for_the_same_entity(
        self,
        make_entity_record: MakeEntityRecord,
        make_mem_storage: MakeMemStorage,
        make_mem_entity_record_repository: MakeMemEntityRecordRepository,
    ) -> None:
        entity_id = uuid4()
        mem_storage = make_mem_storage()
        repo = make_mem_entity_record_repository(mem_storage=mem_storage)
        first = make_entity_record(entity_id=entity_id, outcome="already_fetched")
        second = make_entity_record(entity_id=entity_id, outcome="expanded")

        await repo.save(record=first)
        await repo.save(record=second)

        assert mem_storage.entity_records == [first, second]


class TestMemEntityRecordRepositoryListByEntityId:
    @pytest.mark.asyncio
    async def test_returns_empty_tuple_for_an_unseen_entity(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_entity_record_repository: MakeMemEntityRecordRepository,
    ) -> None:
        repo = make_mem_entity_record_repository(mem_storage=make_mem_storage())

        assert await repo.list_by_entity_id(entity_id=uuid4()) == ()

    @pytest.mark.asyncio
    async def test_returns_only_records_for_the_requested_entity(
        self,
        make_entity_record: MakeEntityRecord,
        make_mem_storage: MakeMemStorage,
        make_mem_entity_record_repository: MakeMemEntityRecordRepository,
    ) -> None:
        target_id = uuid4()
        target_record = make_entity_record(entity_id=target_id)
        other_record = make_entity_record(entity_id=uuid4())
        mem_storage = make_mem_storage(entity_records=[target_record, other_record])
        repo = make_mem_entity_record_repository(mem_storage=mem_storage)

        found = await repo.list_by_entity_id(entity_id=target_id)

        assert found == (target_record,)

    @pytest.mark.asyncio
    async def test_returns_every_attempt_including_blocked_ones(
        self,
        make_entity_record: MakeEntityRecord,
        make_mem_storage: MakeMemStorage,
        make_mem_entity_record_repository: MakeMemEntityRecordRepository,
    ) -> None:
        entity_id = uuid4()
        blocked = make_entity_record(entity_id=entity_id, outcome="already_fetched")
        expanded = make_entity_record(entity_id=entity_id, outcome="expanded")
        mem_storage = make_mem_storage(entity_records=[expanded, blocked])
        repo = make_mem_entity_record_repository(mem_storage=mem_storage)

        found = await repo.list_by_entity_id(entity_id=entity_id)

        assert set(found) == {expanded, blocked}


class TestMemEntityRecordRepositoryListAll:
    @pytest.mark.asyncio
    async def test_returns_empty_tuple_when_nothing_was_ever_recorded(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_entity_record_repository: MakeMemEntityRecordRepository,
    ) -> None:
        repo = make_mem_entity_record_repository(mem_storage=make_mem_storage())

        assert await repo.list_all() == ()

    @pytest.mark.asyncio
    async def test_returns_records_across_every_entity(
        self,
        make_entity_record: MakeEntityRecord,
        make_mem_storage: MakeMemStorage,
        make_mem_entity_record_repository: MakeMemEntityRecordRepository,
    ) -> None:
        first = make_entity_record(entity_id=uuid4())
        second = make_entity_record(entity_id=uuid4())
        mem_storage = make_mem_storage(entity_records=[first, second])
        repo = make_mem_entity_record_repository(mem_storage=mem_storage)

        found = await repo.list_all()

        assert set(found) == {first, second}
