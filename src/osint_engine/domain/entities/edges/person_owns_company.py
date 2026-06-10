from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.entity import Edge
from osint_engine.domain.entities.nodes.company import CompanyID
from osint_engine.domain.entities.nodes.person import PersonID
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

PersonOwnsCompanyID = NewType("PersonOwnsCompanyID", UUID)


class PersonOwnsCompany(
    Edge[PersonOwnsCompanyID], namespace=EntityNAMESPACE.PERSON_COMPANY
):
    source_id: PersonID
    target_id: CompanyID

    @override
    def __init__(self, *, source_id: PersonID, target_id: CompanyID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
