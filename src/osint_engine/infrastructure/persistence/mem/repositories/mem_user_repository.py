from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.application.contracts.repositories.user_repository import (
    UserRepository,
)
from osint_engine.infrastructure.errors.auth_error import NotFoundUserAuthError

if TYPE_CHECKING:
    from osint_engine.application.auth.user import User
    from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage


class MemUserRepository(UserRepository):
    @override
    def __init__(self, *, mem_storage: MemStorage) -> None:
        self.users = mem_storage.users

    @override
    async def find(self, *, username: str) -> User | None:
        return self.users.get(username)

    @override
    async def get(self, *, username: str) -> User:
        found = await self.find(username=username)

        if found is None:
            raise NotFoundUserAuthError(username=username)

        return found

    @override
    async def save(self, *, user: User) -> None:
        if user.username not in self.users:
            self.users[user.username] = user
