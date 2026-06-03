from typing import NewType
from uuid import UUID

from osint_engine.domain.entities.entity import Node

EmailID = NewType("EmailID", UUID)


class Email(Node[EmailID]):
    __slots__ = ("value",)

    def __init__(self, *, value: str) -> None:
        super().__init__(value=value)
