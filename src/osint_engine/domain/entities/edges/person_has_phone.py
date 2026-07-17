from __future__ import annotations

from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.entities.nodes.person import PersonID
from osint_engine.domain.entities.nodes.phone import PhoneID
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

PersonHasPhoneID = NewType("PersonHasPhoneID", UUID)


class PersonHasPhone(
    Edge[PersonHasPhoneID, PersonID, PhoneID],
    id_fields=None,
    namespace=EntityNAMESPACE.PERSON_PHONE,
):
    @override
    def __init__(self, *, source_id: PersonID, target_id: PhoneID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
