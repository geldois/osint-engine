from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.entity import Edge
from osint_engine.domain.entities.nodes.email import EmailID
from osint_engine.domain.entities.nodes.person import PersonID
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

PersonHasEmailID = NewType("PersonHasEmailID", UUID)


class PersonHasEmail(Edge[PersonHasEmailID], namespace=EntityNAMESPACE.PERSON_EMAIL):
    source_id: PersonID
    target_id: EmailID

    @override
    def __init__(self, *, source_id: PersonID, target_id: EmailID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
