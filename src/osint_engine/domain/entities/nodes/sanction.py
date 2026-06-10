from typing import Literal, NewType, override
from uuid import UUID

from osint_engine.domain.entities.entity import Node
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

SanctionID = NewType("SanctionID", UUID)


class Sanction(Node[SanctionID], namespace=EntityNAMESPACE.SANCTION):
    organ: Literal["CEIS", "CNEP"]

    @override
    def __init__(self, *, organ: Literal["CEIS", "CNEP"]) -> None:
        super().__init__(organ=organ)
