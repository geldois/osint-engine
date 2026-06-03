from typing import NewType
from uuid import UUID

from osint_engine.domain.entities.entity import Edge
from osint_engine.domain.entities.nodes.person import PersonID
from osint_engine.domain.entities.nodes.phone import PhoneID

PersonHasPhoneID = NewType("PersonHasPhoneID", UUID)


class PersonHasPhone(Edge[PersonHasPhoneID]):
    __slots__ = ()

    def __init__(self, *, source_id: PersonID, target_id: PhoneID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
