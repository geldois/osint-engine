from typing import NewType
from uuid import UUID

from osint_engine.domain.entities.entity import Edge
from osint_engine.domain.entities.nodes.address import AddressID
from osint_engine.domain.entities.nodes.company import CompanyID
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

CompanyLocatedAtID = NewType("CompanyLocatedAtID", UUID)


class CompanyLocatedAt(
    Edge[CompanyLocatedAtID], namespace=EntityNAMESPACE.COMPANY_ADDRESS
):
    __slots__ = ()

    source_id: CompanyID
    target_id: AddressID

    def __init__(self, *, source_id: CompanyID, target_id: AddressID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
