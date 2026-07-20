from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from osint_engine.application.use_cases.credentials.save_credential import (
    SaveExternalCredential,
)

if TYPE_CHECKING:
    from tests.conftest import MakeExternalCredential, MakeMemStorage, MakeMemUoW
    from tests.test_application.conftest import MakeMemUoWFactory


class TestSaveExternalCredentialOrchestration:
    @pytest.mark.asyncio
    async def test_persists_the_credential_to_storage(
        self,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        credential = make_external_credential(username="alice")
        mem_storage = make_mem_storage()
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = SaveExternalCredential(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow), credential=credential
        )

        await use_case.execute()

        assert (
            mem_storage.external_credentials[(credential.username, credential.provider)]
            is credential
        )
