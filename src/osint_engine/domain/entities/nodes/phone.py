from __future__ import annotations

from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

PhoneID = NewType("PhoneID", UUID)


class Phone(Node[PhoneID], namespace=EntityNAMESPACE.PHONE):
    number: str

    @override
    def __init__(self, *, number: str) -> None:
        super().__init__(identity_fields=frozenset({"number"}), number=number)
