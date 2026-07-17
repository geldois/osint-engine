from __future__ import annotations

from osint_engine.domain.entities.bases.entity import Entity, IDType_co
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE


class Node(Entity[IDType_co], id_fields=None, namespace=EntityNAMESPACE.NODE): ...
