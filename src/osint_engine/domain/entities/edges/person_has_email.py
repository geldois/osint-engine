from typing import NewType
from uuid import UUID

from osint_engine.domain.entities.entity import Edge
from osint_engine.domain.entities.nodes.email import EmailID
from osint_engine.domain.entities.nodes.person import PersonID

PersonHasEmailID = NewType("PersonHasEmailID", UUID)


class PersonHasEmail(Edge[PersonHasEmailID]):
    __slots__ = ()

    def __init__(self, *, source_id: PersonID, target_id: EmailID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
