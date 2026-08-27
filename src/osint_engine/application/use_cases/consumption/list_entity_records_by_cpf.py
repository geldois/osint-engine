from __future__ import annotations

from typing import TYPE_CHECKING, override

from structlog.stdlib import get_logger

from osint_engine.application.consumption.entity_record import EntityRecord
from osint_engine.application.contracts.use_case import Query
from osint_engine.domain.entities.nodes.person import Person

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.application.contracts.uow import UoW

_logger = get_logger()


class ListEntityRecordsByCPF(Query[tuple[EntityRecord, ...]]):
    uow_factory: Callable[[], UoW]
    cpf: str

    @override
    def __init__(self, *, uow_factory: Callable[[], UoW], cpf: str) -> None:
        super().__init__(uow_factory=uow_factory, cpf=cpf)

    @override
    async def execute(self) -> tuple[EntityRecord, ...]:
        _logger.info("entity_records.list_by_cpf.start", cpf=self.cpf)

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

        ordered = tuple(sorted(records, key=lambda record: record.requested_at))

        _logger.info(
            "entity_records.list_by_cpf.success",
            cpf=self.cpf,
            record_count=len(ordered),
        )

        return ordered
