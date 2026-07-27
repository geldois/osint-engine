from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from osint_engine.application.auth.external_credential import Provider
from osint_engine.application.use_cases.credentials.list_credentials import (
    ListExternalCredentials,
)

if TYPE_CHECKING:
    from tests.conftest import MakeExternalCredential, MakeMemStorage, MakeMemUoW
    from tests.test_application.conftest import MakeMemUoWFactory


class TestListExternalCredentialsOrchestration:
    @pytest.mark.asyncio
    async def test_returns_providers_configured_for_the_given_username(
        self,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        credential = make_external_credential(username="alice")
        mem_storage = make_mem_storage(external_credentials=[credential])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = ListExternalCredentials(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            username=credential.username,
        )

        providers = await use_case.execute()

        assert providers == frozenset({Provider.PORTAL_TRANSPARENCIA})

    @pytest.mark.asyncio
    async def test_returns_empty_frozenset_when_username_has_no_credentials(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        mem_storage = make_mem_storage()
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = ListExternalCredentials(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow), username="alice"
        )

        providers = await use_case.execute()

        assert providers == frozenset()
