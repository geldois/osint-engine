from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.application.consumption.entity_record import EntityRecord


class EntityRecordRepository(ABC):
    @abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def save(self, *, record: EntityRecord) -> EntityRecord:
        raise NotImplementedError

    @abstractmethod
    async def list_by_entity_id(self, *, entity_id: UUID) -> tuple[EntityRecord, ...]:
        raise NotImplementedError

    @abstractmethod
    async def list_all(self) -> tuple[EntityRecord, ...]:
        raise NotImplementedError
