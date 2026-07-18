from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.application.contracts.repositories.external_credential_repository import (  # noqa: E501
    ExternalCredentialRepository,
)

if TYPE_CHECKING:
    from osint_engine.application.auth.external_credential import (
        ExternalCredential,
        Provider,
    )
    from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage


class MemExternalCredentialRepository(ExternalCredentialRepository):
    @override
    def __init__(self, *, mem_storage: MemStorage) -> None:
        self.external_credentials = mem_storage.external_credentials

    @override
    async def find(
        self, *, username: str, provider: Provider
    ) -> ExternalCredential | None:
        return self.external_credentials.get((username, provider))

    @override
    async def save(self, *, credential: ExternalCredential) -> None:
        self.external_credentials[(credential.username, credential.provider)] = (
            credential
        )
