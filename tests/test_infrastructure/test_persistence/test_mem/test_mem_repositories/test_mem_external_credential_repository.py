from __future__ import annotations

import pytest

from osint_engine.application.auth.external_credential import (
    ExternalCredential,
    Provider,
)
from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage
from osint_engine.infrastructure.persistence.mem.repositories.mem_external_credential_repository import (  # noqa: E501
    MemExternalCredentialRepository,
)

# TEST DOUBLES


_CREDENTIAL = ExternalCredential(
    api_key="secret-key",
    provider=Provider.PORTAL_TRANSPARENCIA,
    username="analyst",
)


# TESTS


class TestMemExternalCredentialRepositoryFind:
    @pytest.mark.asyncio
    async def test_find_returns_credential_when_it_exists_for_username_and_provider(
        self,
    ) -> None:
        mem_storage = MemStorage(
            external_credentials={
                (_CREDENTIAL.username, _CREDENTIAL.provider): _CREDENTIAL
            }
        )
        repo = MemExternalCredentialRepository(mem_storage=mem_storage)

        found = await repo.find(
            username=_CREDENTIAL.username, provider=_CREDENTIAL.provider
        )

        assert found is _CREDENTIAL

    @pytest.mark.asyncio
    async def test_find_returns_none_when_credential_does_not_exist(self) -> None:
        mem_storage = MemStorage()
        repo = MemExternalCredentialRepository(mem_storage=mem_storage)

        found = await repo.find(
            username=_CREDENTIAL.username, provider=_CREDENTIAL.provider
        )

        assert found is None

    @pytest.mark.asyncio
    async def test_find_does_not_match_across_different_providers(self) -> None:
        mem_storage = MemStorage(
            external_credentials={
                (_CREDENTIAL.username, _CREDENTIAL.provider): _CREDENTIAL
            }
        )
        repo = MemExternalCredentialRepository(mem_storage=mem_storage)

        found = await repo.find(
            username=_CREDENTIAL.username, provider=Provider.PORTAL_TRANSPARENCIA
        )

        assert found is _CREDENTIAL


class TestMemExternalCredentialRepositorySave:
    @pytest.mark.asyncio
    async def test_save_stores_credential_keyed_by_username_and_provider(
        self,
    ) -> None:
        mem_storage = MemStorage()
        repo = MemExternalCredentialRepository(mem_storage=mem_storage)

        await repo.save(credential=_CREDENTIAL)

        key = (_CREDENTIAL.username, _CREDENTIAL.provider)

        assert mem_storage.external_credentials[key] is _CREDENTIAL

    @pytest.mark.asyncio
    async def test_save_overwrites_existing_credential_for_the_same_key(self) -> None:
        mem_storage = MemStorage()
        repo = MemExternalCredentialRepository(mem_storage=mem_storage)

        stale = ExternalCredential(
            api_key="stale-key",
            provider=_CREDENTIAL.provider,
            username=_CREDENTIAL.username,
        )

        await repo.save(credential=stale)
        await repo.save(credential=_CREDENTIAL)

        key = (_CREDENTIAL.username, _CREDENTIAL.provider)

        assert mem_storage.external_credentials[key] is _CREDENTIAL
