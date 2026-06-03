from typing import NewType
from uuid import UUID

from osint_engine.domain.entities.entity import Edge
from osint_engine.domain.entities.nodes.person import PersonID
from osint_engine.domain.entities.nodes.sanction import SanctionID

PersonReceivedSanctionID = NewType("PersonReceivedSanctionID", UUID)


class PersonReceivedSanction(Edge[PersonReceivedSanctionID]):
    __slots__ = ()

    def __init__(self, *, source_id: PersonID, target_id: SanctionID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
