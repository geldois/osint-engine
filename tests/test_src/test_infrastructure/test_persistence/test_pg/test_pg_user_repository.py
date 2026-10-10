from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest

from osint_engine.infrastructure.persistence.pg.repositories.pg_user_repository import (
    PgUserRepository,
)

if TYPE_CHECKING:
    import asyncpg

    from tests.fixtures.application import MakeUser

pytestmark = pytest.mark.usefixtures("clean_tables")


@pytest.fixture
def repository(postgres_pool: asyncpg.Pool) -> PgUserRepository:
    return PgUserRepository(pool=postgres_pool)


class TestPgUserRepositorySave:
    @pytest.mark.asyncio(loop_scope="session")
    async def test_save_then_find_round_trips_the_user(
        self, repository: PgUserRepository, make_user: MakeUser
    ) -> None:
        user = make_user(username="alice", hashed_password="hash-a")

        inserted = await repository.save(user=user)
        found = await repository.find(username="alice")

        assert inserted is True
        assert found == user

    @pytest.mark.asyncio(loop_scope="session")
    async def test_saving_an_existing_username_returns_false_and_keeps_the_first_hash(
        self, repository: PgUserRepository, make_user: MakeUser
    ) -> None:
        first = make_user(username="alice", hashed_password="first-hash")
        second = make_user(username="alice", hashed_password="second-hash")

        await repository.save(user=first)
        inserted = await repository.save(user=second)
        found = await repository.find(username="alice")

        assert inserted is False
        assert found == first

    @pytest.mark.asyncio(loop_scope="session")
    async def test_concurrent_saves_of_one_username_insert_exactly_once(
        self, repository: PgUserRepository, make_user: MakeUser
    ) -> None:
        contenders = [
            make_user(username="alice", hashed_password=f"hash-{index}")
            for index in range(8)
        ]

        outcomes = await asyncio.gather(
            *(repository.save(user=contender) for contender in contenders)
        )

        assert outcomes.count(True) == 1
        assert outcomes.count(False) == 7

    @pytest.mark.asyncio(loop_scope="session")
    async def test_usernames_are_case_sensitive(
        self, repository: PgUserRepository, make_user: MakeUser
    ) -> None:
        await repository.save(user=make_user(username="alice"))

        assert await repository.find(username="Alice") is None


class TestPgUserRepositoryFind:
    @pytest.mark.asyncio(loop_scope="session")
    async def test_find_returns_none_for_an_unknown_username(
        self, repository: PgUserRepository
    ) -> None:
        assert await repository.find(username="nobody") is None
