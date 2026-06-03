from typing import NewType
from uuid import UUID

from osint_engine.domain.entities.entity import Node

AddressID = NewType("AddressID", UUID)


class Address(Node[AddressID]):
    __slots__ = ("cep",)

    def __init__(self, *, cep: "str") -> None:
        super().__init__(cep=cep)
