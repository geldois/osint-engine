from typing import NewType
from uuid import UUID

from osint_engine.domain.entities.entity import Node
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

PersonID = NewType("PersonID", UUID)


class Person(Node[PersonID], namespace=EntityNAMESPACE.PERSON):
    __slots__ = ("cpf", "name")

    cpf: str
    name: str

    def __init__(self, *, cpf: str, name: str) -> None:
        super().__init__(cpf=cpf, name=name)
