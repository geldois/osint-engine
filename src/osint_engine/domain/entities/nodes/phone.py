from typing import NewType
from uuid import UUID

from osint_engine.domain.entities.entity import Node

PhoneID = NewType("PhoneID", UUID)


class Phone(Node[PhoneID]):
    __slots__ = ("value",)

    def __init__(self, *, value: str) -> None:
        super().__init__(value=value)
