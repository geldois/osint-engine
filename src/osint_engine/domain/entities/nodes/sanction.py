from typing import Literal, NewType
from uuid import UUID

from osint_engine.domain.entities.entity import Node

SanctionID = NewType("SanctionID", UUID)


class Sanction(Node[SanctionID]):
    __slots__ = ("organ",)

    def __init__(self, *, organ: Literal["CEIS", "CNEP"]) -> None:
        super().__init__(organ=organ)
