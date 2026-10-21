from __future__ import annotations

from typing import TYPE_CHECKING, Self, override

from osint_engine.infrastructure.persistence.hybrid_uow import HybridUoW

if TYPE_CHECKING:
    from asyncpg import Pool

    from osint_engine.application.revision.policies.revision_merge_policy import (
        RevisionMergePolicy,
    )
    from osint_engine.application.revision.policies.revision_selection_policy import (
        RevisionSelectionPolicy,
    )
    from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage


class RecordingHybridUoW(HybridUoW):
    @override
    def __init__(
        self,
        *,
        events: list[str],
        mem_storage: MemStorage,
        pg_pool: Pool,
        encryption_key: str,
        revision_merge_policy: RevisionMergePolicy,
        revision_selection_policy: RevisionSelectionPolicy,
    ) -> None:
        super().__init__(
            mem_storage=mem_storage,
            pg_pool=pg_pool,
            encryption_key=encryption_key,
            revision_merge_policy=revision_merge_policy,
            revision_selection_policy=revision_selection_policy,
        )
        self._events = events

    @override
    async def _prepare(self) -> None:
        self._events.append("uow:enter")
        await super()._prepare()

    @override
    async def _finish(self) -> None:
        await super()._finish()
        self._events.append("uow:exit")


class FakePgPool:
    def __init__(self) -> None:
        self.external_credentials: dict[tuple[str, str], str] = {}
        self.users: dict[str, str] = {}

    async def acquire(self) -> Self:
        return self

    async def release(self, connection: Self) -> None:
        assert connection is self

    async def fetchrow(self, query: str, *args: object) -> dict[str, str] | None:
        if "FROM users" in query:
            return self._fetch_user(args)

        assert "FROM external_credentials" in query
        assert len(args) == 2

        username, provider = args
        assert isinstance(username, str)
        assert isinstance(provider, str)

        api_key = self.external_credentials.get((username, provider))

        if api_key is None:
            return None

        return {"username": username, "provider": provider, "api_key": api_key}

    async def fetch(self, query: str, *args: object) -> list[dict[str, str]]:
        assert "FROM external_credentials" in query
        assert len(args) == 1

        (username,) = args
        assert isinstance(username, str)

        return [
            {"provider": provider}
            for stored_username, provider in self.external_credentials
            if stored_username == username
        ]

    async def execute(self, query: str, *args: object) -> str:
        if query == "SELECT 1":
            return "SELECT 1"

        if "INSERT INTO users" in query:
            return self._insert_user(args)

        assert "INSERT INTO external_credentials" in query
        assert len(args) == 3

        username, provider, api_key = args
        assert isinstance(username, str)
        assert isinstance(provider, str)
        assert isinstance(api_key, str)

        self.external_credentials[(username, provider)] = api_key

        return "INSERT 0 1"

    def _fetch_user(self, args: tuple[object, ...]) -> dict[str, str] | None:
        assert len(args) == 1

        (username,) = args
        assert isinstance(username, str)

        hashed_password = self.users.get(username)

        if hashed_password is None:
            return None

        return {"username": username, "hashed_password": hashed_password}

    def _insert_user(self, args: tuple[object, ...]) -> str:
        assert len(args) == 2

        username, hashed_password = args
        assert isinstance(username, str)
        assert isinstance(hashed_password, str)

        if username in self.users:
            return "INSERT 0 0"

        self.users[username] = hashed_password

        return "INSERT 0 1"
