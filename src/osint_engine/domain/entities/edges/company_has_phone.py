from typing import NewType
from uuid import UUID

from osint_engine.domain.entities.entity import Edge
from osint_engine.domain.entities.nodes.company import CompanyID
from osint_engine.domain.entities.nodes.phone import PhoneID
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

CompanyHasPhoneID = NewType("CompanyHasPhoneID", UUID)


class CompanyHasPhone(
    Edge[CompanyHasPhoneID], namespace=EntityNAMESPACE.COMPANY_PHONE
):
    __slots__ = ()

    source_id: CompanyID
    target_id: PhoneID

    def __init__(self, *, source_id: CompanyID, target_id: PhoneID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
