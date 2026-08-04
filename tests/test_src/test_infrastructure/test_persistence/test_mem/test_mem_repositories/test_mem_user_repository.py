from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage
from osint_engine.infrastructure.persistence.mem.repositories.mem_user_repository import (  # noqa: E501
    MemUserRepository,
)

if TYPE_CHECKING:
    from tests.conftest import MakeMemStorage, MakeUser


class TestMemUserRepositoryFind:
    @pytest.mark.asyncio
    async def test_find_returns_user_when_user_exists(
        self, make_user: MakeUser, make_mem_storage: MakeMemStorage
    ) -> None:
        user = make_user()
        mem_storage = make_mem_storage(users=[user])
        repo = MemUserRepository(mem_storage=mem_storage)

        found = await repo.find(username=user.username)

        assert found is user

    @pytest.mark.asyncio
    async def test_find_returns_none_when_user_does_not_exist(
        self, make_user: MakeUser, make_mem_storage: MakeMemStorage
    ) -> None:
        user = make_user()
        mem_storage = make_mem_storage()
        repo = MemUserRepository(mem_storage=mem_storage)

        found = await repo.find(username=user.username)

        assert found is None


class TestMemUserRepositorySave:
    @pytest.mark.asyncio
    async def test_save_stores_user_in_storage(
        self, make_user: MakeUser, make_mem_storage: MakeMemStorage
    ) -> None:
        user = make_user()
        mem_storage = make_mem_storage()
        repo = MemUserRepository(mem_storage=mem_storage)

        await repo.save(user=user)

        assert user.username in mem_storage.users

    @pytest.mark.asyncio
    async def test_save_is_idempotent_and_does_not_overwrite(
        self, make_user: MakeUser
    ) -> None:
        username = "test_user"

        user_a = make_user(username=username)
        user_b = make_user(username=username)

        assert user_a.username == user_b.username

        mem_storage = MemStorage(users={user_a.username: user_a})
        repo = MemUserRepository(mem_storage=mem_storage)

        await repo.save(user=user_a)

        await repo.save(user=user_b)

        assert mem_storage.users[user_a.username] is user_a

        assert mem_storage.users[user_a.username] is not user_b

        assert mem_storage.users[user_b.username] is user_a

        assert mem_storage.users[user_b.username] is not user_b
