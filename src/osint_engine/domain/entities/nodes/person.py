from typing import NewType
from uuid import UUID

from osint_engine.domain.entities.entity import Node

PersonID = NewType("PersonID", UUID)


class Person(Node[PersonID]):
    __slots__ = ("cpf", "name")

    def __init__(self, *, cpf: str, name: str) -> None:
        super().__init__(cpf=cpf, name=name)
