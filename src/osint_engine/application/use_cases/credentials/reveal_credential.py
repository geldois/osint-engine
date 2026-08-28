from __future__ import annotations

from typing import TYPE_CHECKING, override

from structlog.stdlib import get_logger

from osint_engine.application.contracts.use_case import Query
from osint_engine.application.errors.external_credential_error import (
    ExternalCredentialNotFoundError,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.application.auth.external_credential import Provider
    from osint_engine.application.contracts.uow import UoW

_logger = get_logger()


class RevealExternalCredential(Query[str]):
    uow_factory: Callable[[], UoW]
    provider: Provider
    username: str

    @override
    def __init__(
        self, *, uow_factory: Callable[[], UoW], provider: Provider, username: str
    ) -> None:
        super().__init__(uow_factory=uow_factory, provider=provider, username=username)

    @override
    async def execute(self) -> str:
        _logger.info(
            "external_credential.reveal.start",
            provider=self.provider,
            username=self.username,
        )

        async with self.uow_factory() as uow:
            credential = await uow.external_credentials.find(
                username=self.username, provider=self.provider
            )

        if credential is None:
            raise ExternalCredentialNotFoundError(
                username=self.username, provider=self.provider
            )

        _logger.info(
            "external_credential.reveal.success",
            provider=self.provider,
            username=self.username,
        )

        return credential.api_key
