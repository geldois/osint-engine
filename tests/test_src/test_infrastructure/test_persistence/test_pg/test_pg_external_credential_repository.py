from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pytest
from cryptography.fernet import Fernet

from osint_engine.application.auth.external_credential import Provider
from osint_engine.infrastructure.persistence.pg.repositories.pg_external_credential_repository import (  # noqa: E501
    PgExternalCredentialRepository,
)

if TYPE_CHECKING:
    import asyncpg

    from tests.conftest import MakeExternalCredential


@pytest.fixture
def repository(postgres_pool: asyncpg.Pool) -> PgExternalCredentialRepository:
    return PgExternalCredentialRepository(
        pool=postgres_pool, encryption_key=Fernet.generate_key().decode()
    )


class TestPgExternalCredentialRepository:
    @pytest.mark.asyncio(loop_scope="session")
    async def test_save_and_find_round_trip_returns_decrypted_credential(
        self,
        repository: PgExternalCredentialRepository,
        make_external_credential: MakeExternalCredential,
    ) -> None:
        credential = make_external_credential(api_key="plain-api-key")

        await repository.save(credential=credential)

        found = await repository.find(
            username=credential.username, provider=credential.provider
        )

        assert found == credential

    @pytest.mark.asyncio(loop_scope="session")
    async def test_save_upserts_existing_username_and_provider(
        self,
        postgres_pool: asyncpg.Pool,
        repository: PgExternalCredentialRepository,
        make_external_credential: MakeExternalCredential,
    ) -> None:
        original = make_external_credential(
            api_key="original-key", username="same-user"
        )
        replacement = make_external_credential(
            api_key="replacement-key", username="same-user"
        )

        await repository.save(credential=original)
        await repository.save(credential=replacement)

        found = await repository.find(
            username=replacement.username,
            provider=replacement.provider,
        )
        row_count = cast(
            "int",
            await postgres_pool.fetchval(  # pyright: ignore[reportUnknownMemberType]
                """
                SELECT count(*)
                FROM external_credentials
                WHERE username = $1 AND provider = $2
                """,
                replacement.username,
                replacement.provider.value,
            ),
        )

        assert found == replacement
        assert row_count == 1

    @pytest.mark.asyncio(loop_scope="session")
    async def test_find_missing_pair_returns_none(
        self, repository: PgExternalCredentialRepository
    ) -> None:
        found = await repository.find(
            username="missing-user",
            provider=Provider.PORTAL_TRANSPARENCIA,
        )

        assert found is None

    @pytest.mark.asyncio(loop_scope="session")
    async def test_stored_api_key_is_never_plaintext(
        self,
        postgres_pool: asyncpg.Pool,
        repository: PgExternalCredentialRepository,
        make_external_credential: MakeExternalCredential,
    ) -> None:
        credential = make_external_credential(api_key="plaintext-secret")

        await repository.save(credential=credential)

        stored_api_key = cast(
            "str",
            await postgres_pool.fetchval(  # pyright: ignore[reportUnknownMemberType]
                """
                SELECT api_key
                FROM external_credentials
                WHERE username = $1 AND provider = $2
                """,
                credential.username,
                credential.provider.value,
            ),
        )

        assert isinstance(stored_api_key, str)
        assert stored_api_key != credential.api_key

    @pytest.mark.asyncio(loop_scope="session")
    async def test_list_configured_providers_returns_providers_for_username(
        self,
        repository: PgExternalCredentialRepository,
        make_external_credential: MakeExternalCredential,
    ) -> None:
        credential = make_external_credential(username="analyst")

        await repository.save(credential=credential)

        providers = await repository.list_configured_providers(
            username=credential.username
        )

        assert providers == frozenset({credential.provider})

    @pytest.mark.asyncio(loop_scope="session")
    async def test_list_configured_providers_returns_empty_for_unknown_username(
        self, repository: PgExternalCredentialRepository
    ) -> None:
        providers = await repository.list_configured_providers(username="unknown-user")

        assert providers == frozenset()
