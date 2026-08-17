from __future__ import annotations

from typing import TYPE_CHECKING, override

from cryptography.fernet import Fernet

from osint_engine.application.auth.external_credential import (
    ExternalCredential,
    Provider,
)
from osint_engine.application.contracts.repositories.external_credential_repository import (  # noqa: E501
    ExternalCredentialRepository,
)
from osint_engine.infrastructure.persistence.pg.generated.models import (
    ExternalCredential as ExternalCredentialRow,
)

if TYPE_CHECKING:
    from asyncpg import Pool

_FIND_BY_USERNAME_AND_PROVIDER = """
SELECT username, provider, api_key
FROM external_credentials
WHERE username = $1 AND provider = $2
"""

_UPSERT = """
INSERT INTO external_credentials (username, provider, api_key)
VALUES ($1, $2, $3)
ON CONFLICT (username, provider)
DO UPDATE SET api_key = excluded.api_key
"""

_LIST_PROVIDERS_BY_USERNAME = """
SELECT provider
FROM external_credentials
WHERE username = $1
"""


class PgExternalCredentialRepository(ExternalCredentialRepository):
    @override
    def __init__(self, *, pool: Pool, encryption_key: str) -> None:
        self._pool = pool
        self._fernet = Fernet(encryption_key)

    @override
    async def find(
        self, *, username: str, provider: Provider
    ) -> ExternalCredential | None:
        record = await self._pool.fetchrow(
            _FIND_BY_USERNAME_AND_PROVIDER, username, provider.value
        )

        if record is None:
            return None

        row = ExternalCredentialRow(**record)
        api_key = self._fernet.decrypt(row.api_key.encode()).decode()

        return ExternalCredential(
            api_key=api_key,
            provider=Provider(row.provider),
            username=row.username,
        )

    @override
    async def save(self, *, credential: ExternalCredential) -> None:
        encrypted_api_key = self._fernet.encrypt(credential.api_key.encode()).decode()

        await self._pool.execute(
            _UPSERT,
            credential.username,
            credential.provider.value,
            encrypted_api_key,
        )

    @override
    async def list_configured_providers(self, *, username: str) -> frozenset[Provider]:
        records = await self._pool.fetch(_LIST_PROVIDERS_BY_USERNAME, username)
        return frozenset(Provider(record["provider"]) for record in records)
