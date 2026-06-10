from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.entity import Edge
from osint_engine.domain.entities.nodes.address import AddressID
from osint_engine.domain.entities.nodes.person import PersonID
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

PersonResideAtID = NewType("PersonResideAtID", UUID)


class PersonResideAt(Edge[PersonResideAtID], namespace=EntityNAMESPACE.PERSON_ADDRESS):
    source_id: PersonID
    target_id: AddressID

    @override
    def __init__(self, *, source_id: PersonID, target_id: AddressID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
