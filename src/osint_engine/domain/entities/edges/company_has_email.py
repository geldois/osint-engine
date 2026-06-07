from typing import NewType
from uuid import UUID

from osint_engine.domain.entities.entity import Edge
from osint_engine.domain.entities.nodes.company import CompanyID
from osint_engine.domain.entities.nodes.email import EmailID
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

CompanyHasEmailID = NewType("CompanyHasEmailID", UUID)


class CompanyHasEmail(
    Edge[CompanyHasEmailID], namespace=EntityNAMESPACE.COMPANY_EMAIL
):
    __slots__ = ()

    source_id: CompanyID
    target_id: EmailID

    def __init__(self, *, source_id: CompanyID, target_id: EmailID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
