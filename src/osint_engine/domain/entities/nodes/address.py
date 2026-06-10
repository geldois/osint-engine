from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.entity import Node
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

AddressID = NewType("AddressID", UUID)


class Address(Node[AddressID], namespace=EntityNAMESPACE.ADDRESS):
    cep: str

    @override
    def __init__(self, *, cep: "str") -> None:
        super().__init__(cep=cep)
