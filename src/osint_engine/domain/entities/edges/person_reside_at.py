from typing import NewType
from uuid import UUID

from osint_engine.domain.entities.entity import Edge
from osint_engine.domain.entities.nodes.address import AddressID
from osint_engine.domain.entities.nodes.person import PersonID

PersonResideAtID = NewType("PersonResideAtID", UUID)


class PersonResideAt(Edge[PersonResideAtID]):
    __slots__ = ()

    def __init__(self, *, source_id: PersonID, target_id: AddressID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
