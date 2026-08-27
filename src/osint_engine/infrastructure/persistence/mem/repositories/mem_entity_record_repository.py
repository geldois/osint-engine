from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.application.contracts.repositories.entity_record_repository import (
    EntityRecordRepository,
)

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.application.consumption.entity_record import EntityRecord
    from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage


class MemEntityRecordRepository(EntityRecordRepository):
    @override
    def __init__(self, *, mem_storage: MemStorage) -> None:
        self.entity_records = mem_storage.entity_records

    @override
    async def save(self, *, record: EntityRecord) -> EntityRecord:
        self.entity_records.append(record)

        return record

    @override
    async def list_by_entity_id(self, *, entity_id: UUID) -> tuple[EntityRecord, ...]:
        return tuple(
            record for record in self.entity_records if record.entity_id == entity_id
        )

    @override
    async def list_all(self) -> tuple[EntityRecord, ...]:
        return tuple(self.entity_records)
