from __future__ import annotations

from typing import TYPE_CHECKING, override

from structlog.stdlib import get_logger

from osint_engine.application.contracts.use_case import Command

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.application.auth.external_credential import ExternalCredential
    from osint_engine.application.contracts.uow import UoW

_logger = get_logger()


class SaveExternalCredential(Command):
    uow_factory: Callable[[], UoW]
    credential: ExternalCredential

    @override
    def __init__(
        self, *, uow_factory: Callable[[], UoW], credential: ExternalCredential
    ) -> None:
        super().__init__(uow_factory=uow_factory, credential=credential)

    @override
    async def execute(self) -> None:
        _logger.info(
            "external_credential.save.start",
            username=self.credential.username,
            provider=self.credential.provider,
        )

        async with self.uow_factory() as uow:
            await uow.external_credentials.save(credential=self.credential)

        _logger.info(
            "external_credential.save.success",
            username=self.credential.username,
            provider=self.credential.provider,
        )
