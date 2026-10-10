from __future__ import annotations

from typing import TYPE_CHECKING, override

from structlog.stdlib import get_logger

from osint_engine.application.consumption.entity_record import EntityRecord
from osint_engine.application.contracts.use_case import Query
from osint_engine.domain.entities.nodes import Person

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.application.contracts.uow import UoW

_logger = get_logger()


class ListEntityRecordsByCPF(Query[tuple[EntityRecord, ...]]):
    uow_factory: Callable[[], UoW]
    cpf: str
    username: str

    @override
    def __init__(
        self, *, uow_factory: Callable[[], UoW], cpf: str, username: str
    ) -> None:
        super().__init__(uow_factory=uow_factory, cpf=cpf, username=username)

    @override
    async def execute(self) -> tuple[EntityRecord, ...]:
        _logger.info(
            "entity_records.list_by_cpf.start", cpf=self.cpf, username=self.username
        )

        stub = Person(
            age_range=None,
            birthdate=None,
            cpf=self.cpf,
            name=None,
            registration_date=None,
            registration_status=None,
        )

        async with self.uow_factory() as uow:
            records = await uow.entity_records.list_by_entity_id(entity_id=stub.id)

        own_records = (record for record in records if record.username == self.username)
        ordered = tuple(sorted(own_records, key=lambda record: record.requested_at))

        _logger.info(
            "entity_records.list_by_cpf.success",
            cpf=self.cpf,
            username=self.username,
            record_count=len(ordered),
        )

        return ordered
