from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.application.auth.user import User
from osint_engine.application.contracts.repositories.user_repository import (
    UserRepository,
)
from osint_engine.infrastructure.persistence.pg.generated.models import (
    User as UserRow,
)

if TYPE_CHECKING:
    from asyncpg import Pool

_FIND_BY_USERNAME = """
SELECT username, hashed_password
FROM users
WHERE username = $1
"""

_INSERT_IF_ABSENT = """
INSERT INTO users (username, hashed_password)
VALUES ($1, $2)
ON CONFLICT (username) DO NOTHING
"""

_INSERTED_ONE_ROW = "INSERT 0 1"


class PgUserRepository(UserRepository):
    @override
    def __init__(self, *, pool: Pool) -> None:
        self._pool = pool

    @override
    async def find(self, *, username: str) -> User | None:
        record = await self._pool.fetchrow(_FIND_BY_USERNAME, username)

        if record is None:
            return None

        row = UserRow(**record)

        return User(hashed_password=row.hashed_password, username=row.username)

    @override
    async def save(self, *, user: User) -> bool:
        status = await self._pool.execute(
            _INSERT_IF_ABSENT, user.username, user.hashed_password
        )

        return status == _INSERTED_ONE_ROW
