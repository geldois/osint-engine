from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, override

from osint_engine.domain.entities.entity import Entity, IDType_co
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

if TYPE_CHECKING:
    from uuid import UUID


class Edge(Entity[IDType_co], namespace=EntityNAMESPACE.EDGE):
    @override
    @abstractmethod
    def __init__(self, *, source_id: UUID, target_id: UUID, **kwargs: object) -> None:
        super().__init__(source_id=source_id, target_id=target_id, **kwargs)
