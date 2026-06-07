from typing import NewType
from uuid import UUID

from osint_engine.domain.entities.entity import Node
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

AddressID = NewType("AddressID", UUID)


class Address(Node[AddressID], namespace=EntityNAMESPACE.ADDRESS):
    __slots__ = ("cep",)

    cep: str

    def __init__(self, *, cep: "str") -> None:
        super().__init__(cep=cep)
