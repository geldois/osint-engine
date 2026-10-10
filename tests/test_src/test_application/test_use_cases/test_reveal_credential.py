from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from osint_engine.application.auth.external_credential import Provider
from osint_engine.application.errors.external_credential_error import (
    ExternalCredentialNotFoundError,
)
from osint_engine.application.use_cases.credentials.reveal_credential import (
    RevealExternalCredential,
)

if TYPE_CHECKING:
    from tests.fixtures.application import MakeExternalCredential
    from tests.fixtures.persistence import MakeMemStorage, MakeMemUoW
    from tests.test_src.test_application.conftest import MakeMemUoWFactory


class TestRevealExternalCredentialExecution:
    @pytest.mark.asyncio
    async def test_returns_the_callers_saved_key(
        self,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        credential = make_external_credential(
            api_key="alice-secret", provider=Provider.KIPFLOW, username="alice"
        )
        mem_uow = make_mem_uow(
            mem_storage=make_mem_storage(external_credentials=[credential])
        )

        api_key = await RevealExternalCredential(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            provider=Provider.KIPFLOW,
            username="alice",
        ).execute()

        assert api_key == "alice-secret"

    @pytest.mark.asyncio
    async def test_raises_not_found_when_the_caller_never_saved_that_provider(
        self,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        other_provider = make_external_credential(
            provider=Provider.PORTAL_TRANSPARENCIA, username="alice"
        )
        mem_uow = make_mem_uow(
            mem_storage=make_mem_storage(external_credentials=[other_provider])
        )

        with pytest.raises(ExternalCredentialNotFoundError) as exception:
            await RevealExternalCredential(
                uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
                provider=Provider.KIPFLOW,
                username="alice",
            ).execute()

        assert exception.value.username == "alice"
        assert exception.value.provider is Provider.KIPFLOW

    @pytest.mark.asyncio
    async def test_never_reveals_another_users_key(
        self,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        bobs = make_external_credential(
            api_key="bob-secret", provider=Provider.KIPFLOW, username="bob"
        )
        mem_uow = make_mem_uow(
            mem_storage=make_mem_storage(external_credentials=[bobs])
        )

        with pytest.raises(ExternalCredentialNotFoundError):
            await RevealExternalCredential(
                uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
                provider=Provider.KIPFLOW,
                username="alice",
            ).execute()
