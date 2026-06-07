from typing import NewType
from uuid import UUID

from osint_engine.domain.entities.entity import Node
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

EmailID = NewType("EmailID", UUID)


class Email(Node[EmailID], namespace=EntityNAMESPACE.EMAIL):
    __slots__ = ("value",)

    value: str

    def __init__(self, *, value: str) -> None:
        super().__init__(value=value)
