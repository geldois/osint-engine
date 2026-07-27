from __future__ import annotations

from typing import TYPE_CHECKING, override

from structlog.stdlib import get_logger

from osint_engine.application.auth.external_credential import Provider
from osint_engine.application.contracts.use_case import Query

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.application.contracts.uow import UoW

_logger = get_logger()


class ListExternalCredentials(Query[frozenset[Provider]]):
    uow_factory: Callable[[], UoW]
    username: str

    @override
    def __init__(self, *, uow_factory: Callable[[], UoW], username: str) -> None:
        super().__init__(uow_factory=uow_factory, username=username)

    @override
    async def execute(self) -> frozenset[Provider]:
        _logger.info("external_credential.list.start", username=self.username)

        async with self.uow_factory() as uow:
            providers = await uow.external_credentials.list_configured_providers(
                username=self.username
            )

        _logger.info(
            "external_credential.list.success",
            username=self.username,
            provider_count=len(providers),
        )

        return providers
