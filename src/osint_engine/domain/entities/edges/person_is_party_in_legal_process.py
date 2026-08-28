from __future__ import annotations

from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.entities.nodes.legal_process import LegalProcessID
from osint_engine.domain.entities.nodes.person import PersonID
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

PersonIsPartyInLegalProcessID = NewType("PersonIsPartyInLegalProcessID", UUID)


class PersonIsPartyInLegalProcess(
    Edge[PersonIsPartyInLegalProcessID, PersonID, LegalProcessID],
    id_fields=None,
    namespace=EntityNAMESPACE.PERSON_LEGAL_PROCESS,
):
    @override
    def __init__(self, *, source_id: PersonID, target_id: LegalProcessID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
