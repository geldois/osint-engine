from __future__ import annotations

from typing import Self


class FakePgPool:
    def __init__(self) -> None:
        self.external_credentials: dict[tuple[str, str], str] = {}

    async def acquire(self) -> Self:
        return self

    async def release(self, connection: Self) -> None:
        assert connection is self

    async def fetchrow(self, query: str, *args: object) -> dict[str, str] | None:
        assert "FROM external_credentials" in query
        assert len(args) == 2

        username, provider = args
        assert isinstance(username, str)
        assert isinstance(provider, str)

        api_key = self.external_credentials.get((username, provider))

        if api_key is None:
            return None

        return {"username": username, "provider": provider, "api_key": api_key}

    async def execute(self, query: str, *args: object) -> str:
        assert "INSERT INTO external_credentials" in query
        assert len(args) == 3

        username, provider, api_key = args
        assert isinstance(username, str)
        assert isinstance(provider, str)
        assert isinstance(api_key, str)

        self.external_credentials[(username, provider)] = api_key

        return "INSERT 0 1"
