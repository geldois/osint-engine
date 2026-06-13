from __future__ import annotations

from typing import TYPE_CHECKING, NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

if TYPE_CHECKING:
    from osint_engine.domain.entities.nodes.person import PersonID
    from osint_engine.domain.entities.nodes.sanction import SanctionID

PersonReceivedSanctionID = NewType("PersonReceivedSanctionID", UUID)


class PersonReceivedSanction(
    Edge[PersonReceivedSanctionID], namespace=EntityNAMESPACE.PERSON_SANCTION
):
    source_id: PersonID
    target_id: SanctionID

    @override
    def __init__(self, *, source_id: PersonID, target_id: SanctionID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
