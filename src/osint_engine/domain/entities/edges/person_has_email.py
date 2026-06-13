from __future__ import annotations

from typing import TYPE_CHECKING, NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

if TYPE_CHECKING:
    from osint_engine.domain.entities.nodes.email import EmailID
    from osint_engine.domain.entities.nodes.person import PersonID

PersonHasEmailID = NewType("PersonHasEmailID", UUID)


class PersonHasEmail(Edge[PersonHasEmailID], namespace=EntityNAMESPACE.PERSON_EMAIL):
    source_id: PersonID
    target_id: EmailID

    @override
    def __init__(self, *, source_id: PersonID, target_id: EmailID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
