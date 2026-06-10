from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.entity import Edge
from osint_engine.domain.entities.nodes.company import CompanyID
from osint_engine.domain.entities.nodes.person import PersonID
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

CompanyHasMemberID = NewType("CompanyHasMemberID", UUID)


class CompanyHasMember(
    Edge[CompanyHasMemberID], namespace=EntityNAMESPACE.COMPANY_PERSON
):
    source_id: CompanyID
    target_id: PersonID

    @override
    def __init__(self, *, source_id: CompanyID, target_id: PersonID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
