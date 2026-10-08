from __future__ import annotations

from typing import TYPE_CHECKING, override

from structlog.stdlib import get_logger

from osint_engine.application.consumption.entity_record import EntityRecord
from osint_engine.application.contracts.use_case import Query

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.application.contracts.uow import UoW

_logger = get_logger()


class ListEntityRecordCatalog(Query[tuple[EntityRecord, ...]]):
    uow_factory: Callable[[], UoW]
    username: str

    @override
    def __init__(self, *, uow_factory: Callable[[], UoW], username: str) -> None:
        super().__init__(uow_factory=uow_factory, username=username)

    @override
    async def execute(self) -> tuple[EntityRecord, ...]:
        _logger.info("entity_records.list_catalog.start", username=self.username)

        async with self.uow_factory() as uow:
            records = await uow.entity_records.list_all()

        own_records = (record for record in records if record.username == self.username)
        ordered = tuple(
            sorted(own_records, key=lambda record: record.requested_at, reverse=True)
        )

        _logger.info(
            "entity_records.list_catalog.success",
            username=self.username,
            record_count=len(ordered),
        )

        return ordered
