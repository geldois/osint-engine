from __future__ import annotations

from typing import TYPE_CHECKING, NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

if TYPE_CHECKING:
    from osint_engine.domain.entities.nodes.company import CompanyID
    from osint_engine.domain.entities.nodes.person import PersonID

PersonOwnsCompanyID = NewType("PersonOwnsCompanyID", UUID)


class PersonOwnsCompany(
    Edge[PersonOwnsCompanyID], namespace=EntityNAMESPACE.PERSON_COMPANY
):
    source_id: PersonID
    target_id: CompanyID

    @override
    def __init__(self, *, source_id: PersonID, target_id: CompanyID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
