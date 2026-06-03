from typing import NewType
from uuid import UUID

from osint_engine.domain.entities.entity import Edge
from osint_engine.domain.entities.nodes.address import AddressID
from osint_engine.domain.entities.nodes.company import CompanyID

CompanyReceivedSanctionID = NewType("CompanyReceivedSanctionID", UUID)


class CompanyReceivedSanction(Edge[CompanyReceivedSanctionID]):
    __slots__ = ()

    def __init__(self, *, source_id: CompanyID, target_id: AddressID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
