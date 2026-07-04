from __future__ import annotations

from abc import abstractmethod
from typing import override

from osint_engine.domain.entities.entity import Entity, IDType_co
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE


class Node(Entity[IDType_co], namespace=EntityNAMESPACE.NODE):
    @override
    @abstractmethod
    def __init__(
        self, identity_fields: frozenset[str] | None = None, **kwargs: object
    ) -> None:
        super().__init__(identity_fields=identity_fields, **kwargs)
