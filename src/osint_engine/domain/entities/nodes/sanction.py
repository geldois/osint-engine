from typing import Literal, NewType
from uuid import UUID

from osint_engine.domain.entities.entity import Node
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

SanctionID = NewType("SanctionID", UUID)


class Sanction(Node[SanctionID], namespace=EntityNAMESPACE.SANCTION):
    __slots__ = ("organ",)

    organ: Literal["CEIS", "CNEP"]

    def __init__(self, *, organ: Literal["CEIS", "CNEP"]) -> None:
        super().__init__(organ=organ)
