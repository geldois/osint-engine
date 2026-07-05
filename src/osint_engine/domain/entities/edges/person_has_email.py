from __future__ import annotations

from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.entities.nodes.email import EmailID
from osint_engine.domain.entities.nodes.person import PersonID
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

PersonHasEmailID = NewType("PersonHasEmailID", UUID)


class PersonHasEmail(
    Edge[PersonHasEmailID, PersonID, EmailID], namespace=EntityNAMESPACE.PERSON_EMAIL
):
    @override
    def __init__(self, *, source_id: PersonID, target_id: EmailID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
