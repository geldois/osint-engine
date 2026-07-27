from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol, TypedDict, cast, override

import aiosql
from cryptography.fernet import Fernet

from osint_engine.application.auth.external_credential import (
    ExternalCredential,
    Provider,
)
from osint_engine.application.contracts.repositories.external_credential_repository import (  # noqa: E501
    ExternalCredentialRepository,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from asyncpg import Pool


class _ExternalCredentialRow(TypedDict):
    api_key: str
    provider: str
    username: str


class _ProviderRow(TypedDict):
    provider: str


class _ExternalCredentialQueries(Protocol):
    async def find_by_username_and_provider(
        self, connection: Pool, *, username: str, provider: str
    ) -> _ExternalCredentialRow | None: ...

    async def upsert(
        self, connection: Pool, *, username: str, provider: str, api_key: str
    ) -> str: ...

    def list_providers_by_username(
        self, connection: Pool, *, username: str
    ) -> AsyncIterator[_ProviderRow]: ...


_QUERIES_PATH = Path(__file__).parent.parent / "queries" / "external_credentials.sql"

# aiosql builds this object's attributes dynamically from the .sql file, so its
# return type is inherently unknown to the type checker.
_queries = cast(
    "_ExternalCredentialQueries",
    aiosql.from_path(  # pyright: ignore[reportUnknownMemberType]
        _QUERIES_PATH, "asyncpg", mandatory_parameters=False
    ),
)


class PgExternalCredentialRepository(ExternalCredentialRepository):
    @override
    def __init__(self, *, pool: Pool, encryption_key: str) -> None:
        self._pool = pool
        self._fernet = Fernet(encryption_key)

    @override
    async def find(
        self, *, username: str, provider: Provider
    ) -> ExternalCredential | None:
        row = await _queries.find_by_username_and_provider(
            self._pool, username=username, provider=provider.value
        )

        if row is None:
            return None

        api_key = self._fernet.decrypt(row["api_key"].encode()).decode()

        return ExternalCredential(
            api_key=api_key,
            provider=Provider(row["provider"]),
            username=row["username"],
        )

    @override
    async def save(self, *, credential: ExternalCredential) -> None:
        encrypted_api_key = self._fernet.encrypt(credential.api_key.encode()).decode()

        await _queries.upsert(
            self._pool,
            username=credential.username,
            provider=credential.provider.value,
            api_key=encrypted_api_key,
        )

    @override
    async def list_configured_providers(self, *, username: str) -> frozenset[Provider]:
        return frozenset(
            [
                Provider(row["provider"])
                async for row in _queries.list_providers_by_username(
                    self._pool, username=username
                )
            ]
        )
