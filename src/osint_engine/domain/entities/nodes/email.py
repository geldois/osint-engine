from __future__ import annotations

from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

EmailID = NewType("EmailID", UUID)


class Email(
    Node[EmailID], id_fields=frozenset({"address"}), namespace=EntityNAMESPACE.EMAIL
):
    address: str

    @override
    def __init__(self, *, address: str) -> None:
        super().__init__(
            **{
                key: value
                for key, value in locals().items()
                if key not in {"__class__", "self"}
            }
        )
