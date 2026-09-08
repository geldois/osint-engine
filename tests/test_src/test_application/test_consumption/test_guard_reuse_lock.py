from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest

from osint_engine.application.consumption.guard_reuse_lock import (
    find_already_fetched_error,
    is_already_fetched,
)
from osint_engine.application.contracts.use_case import Query, UseCaseRegistry
from osint_engine.application.errors.use_case_registry_error import (
    UnregisteredUseCaseError,
)
from osint_engine.domain.entities.nodes.person import Person

if TYPE_CHECKING:
    from tests.conftest import (
        MakeEntityRecord,
        MakeMemStorage,
        MakeMemUoW,
    )

_REQUESTED_AT = datetime(2026, 1, 1, tzinfo=UTC)
_USERNAME = "alice"


class _FakeGuardedUseCase(Query[None]):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)

    async def execute(self) -> None:
        return None


UseCaseRegistry.register(_FakeGuardedUseCase, provider="fake_guarded", billable=False)


class _FakeUnregisteredUseCase(Query[None]):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)

    async def execute(self) -> None:
        return None


def _make_stub() -> Person:
    return Person(
        age_range=None,
        birthdate=None,
        cpf="10000000000",
        name=None,
        registration_date=None,
        registration_status=None,
    )


class TestFindAlreadyFetchedError:
    @pytest.mark.asyncio
    async def test_returns_none_when_no_previous_attempt_exists(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
    ) -> None:
        mem_storage = make_mem_storage()
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        async with mem_uow as uow:
            error = await find_already_fetched_error(
                uow=uow,
                entity_id=_make_stub().id,
                use_case=_FakeGuardedUseCase,
                force=False,
                requested_at=_REQUESTED_AT,
                username=_USERNAME,
            )

        assert error is None

    @pytest.mark.asyncio
    async def test_returns_the_error_and_logs_the_blocked_attempt(
        self,
        make_entity_record: MakeEntityRecord,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
    ) -> None:
        previous = make_entity_record(
            entity_id=_make_stub().id, provider="fake_guarded"
        )
        mem_storage = make_mem_storage(entity_records=[previous])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        async with mem_uow as uow:
            error = await find_already_fetched_error(
                uow=uow,
                entity_id=_make_stub().id,
                use_case=_FakeGuardedUseCase,
                force=False,
                requested_at=_REQUESTED_AT,
                username=_USERNAME,
            )

        assert error is not None
        assert error.entity_id == _make_stub().id
        assert error.provider == "fake_guarded"
        assert error.fetched_at == previous.requested_at

        blocked = next(
            record
            for record in mem_storage.entity_records
            if record.outcome == "already_fetched"
        )

        assert blocked.provider == "fake_guarded"
        assert blocked.username == _USERNAME

    @pytest.mark.asyncio
    async def test_an_empty_previous_attempt_also_triggers_the_lock(
        self,
        make_entity_record: MakeEntityRecord,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
    ) -> None:
        previous = make_entity_record(
            entity_id=_make_stub().id, outcome="empty", provider="fake_guarded"
        )
        mem_storage = make_mem_storage(entity_records=[previous])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        async with mem_uow as uow:
            error = await find_already_fetched_error(
                uow=uow,
                entity_id=_make_stub().id,
                use_case=_FakeGuardedUseCase,
                force=False,
                requested_at=_REQUESTED_AT,
                username=_USERNAME,
            )

        assert error is not None

    @pytest.mark.asyncio
    async def test_a_failed_or_invalid_previous_attempt_does_not_trigger_the_lock(
        self,
        make_entity_record: MakeEntityRecord,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
    ) -> None:
        failed = make_entity_record(
            entity_id=_make_stub().id, outcome="failed", provider="fake_guarded"
        )
        invalid = make_entity_record(
            entity_id=_make_stub().id, outcome="invalid", provider="fake_guarded"
        )
        mem_storage = make_mem_storage(entity_records=[failed, invalid])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        async with mem_uow as uow:
            error = await find_already_fetched_error(
                uow=uow,
                entity_id=_make_stub().id,
                use_case=_FakeGuardedUseCase,
                force=False,
                requested_at=_REQUESTED_AT,
                username=_USERNAME,
            )

        assert error is None

    @pytest.mark.asyncio
    async def test_force_true_returns_none_even_with_a_previous_attempt(
        self,
        make_entity_record: MakeEntityRecord,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
    ) -> None:
        previous = make_entity_record(
            entity_id=_make_stub().id, provider="fake_guarded"
        )
        mem_storage = make_mem_storage(entity_records=[previous])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        async with mem_uow as uow:
            error = await find_already_fetched_error(
                uow=uow,
                entity_id=_make_stub().id,
                use_case=_FakeGuardedUseCase,
                force=True,
                requested_at=_REQUESTED_AT,
                username=_USERNAME,
            )

        assert error is None
        assert mem_storage.entity_records == [previous]

    @pytest.mark.asyncio
    async def test_a_different_provider_does_not_trigger_the_lock(
        self,
        make_entity_record: MakeEntityRecord,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
    ) -> None:
        previous = make_entity_record(entity_id=_make_stub().id, provider="some_other")
        mem_storage = make_mem_storage(entity_records=[previous])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        async with mem_uow as uow:
            error = await find_already_fetched_error(
                uow=uow,
                entity_id=_make_stub().id,
                use_case=_FakeGuardedUseCase,
                force=False,
                requested_at=_REQUESTED_AT,
                username=_USERNAME,
            )

        assert error is None

    @pytest.mark.asyncio
    async def test_raises_unregistered_use_case_error_before_touching_storage(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
    ) -> None:
        mem_storage = make_mem_storage()
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        async with mem_uow as uow:
            with pytest.raises(UnregisteredUseCaseError) as exception:
                await find_already_fetched_error(
                    uow=uow,
                    entity_id=_make_stub().id,
                    use_case=_FakeUnregisteredUseCase,
                    force=False,
                    requested_at=_REQUESTED_AT,
                    username=_USERNAME,
                )

        assert exception.value.subject is _FakeUnregisteredUseCase


class TestIsAlreadyFetched:
    @pytest.mark.asyncio
    async def test_returns_false_when_no_previous_attempt_exists(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
    ) -> None:
        mem_storage = make_mem_storage()
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        async with mem_uow as uow:
            fetched = await is_already_fetched(
                uow=uow, entity_id=_make_stub().id, use_case=_FakeGuardedUseCase
            )

        assert fetched is False

    @pytest.mark.asyncio
    async def test_returns_true_and_never_writes_when_a_previous_attempt_exists(
        self,
        make_entity_record: MakeEntityRecord,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
    ) -> None:
        previous = make_entity_record(
            entity_id=_make_stub().id, provider="fake_guarded"
        )
        mem_storage = make_mem_storage(entity_records=[previous])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        async with mem_uow as uow:
            fetched = await is_already_fetched(
                uow=uow, entity_id=_make_stub().id, use_case=_FakeGuardedUseCase
            )

        assert fetched is True
        assert mem_storage.entity_records == [previous]

    @pytest.mark.asyncio
    async def test_raises_unregistered_use_case_error(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
    ) -> None:
        mem_storage = make_mem_storage()
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        async with mem_uow as uow:
            with pytest.raises(UnregisteredUseCaseError):
                await is_already_fetched(
                    uow=uow,
                    entity_id=_make_stub().id,
                    use_case=_FakeUnregisteredUseCase,
                )
