from __future__ import annotations

from osint_engine.domain.entities.entity import Entity, IDType_co
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE


class Node(Entity[IDType_co], namespace=EntityNAMESPACE.NODE): ...
