from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, override
from uuid import uuid4

from structlog.stdlib import get_logger

from osint_engine.application.consumption.entity_record import EntityRecord
from osint_engine.application.contracts.use_case import Command

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.application.contracts.uow import UoW

_logger = get_logger()


class RecordInvalidAttempt(Command):
    uow_factory: Callable[[], UoW]
    provider: str
    raw_input: str
    username: str

    @override
    def __init__(
        self,
        *,
        uow_factory: Callable[[], UoW],
        provider: str,
        raw_input: str,
        username: str,
    ) -> None:
        super().__init__(
            uow_factory=uow_factory,
            provider=provider,
            raw_input=raw_input,
            username=username,
        )

    @override
    async def execute(self) -> None:
        _logger.info(
            "consumption.invalid_attempt",
            provider=self.provider,
            raw_input=self.raw_input,
            username=self.username,
        )

        async with self.uow_factory() as uow:
            await uow.entity_records.save(
                record=EntityRecord(
                    id=uuid4(),
                    entity_id=None,
                    entity_ref=None,
                    outcome="invalid",
                    provider=self.provider,
                    requested_at=datetime.now(tz=UTC),
                    username=self.username,
                )
            )
