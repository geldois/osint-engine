from typing import NewType
from uuid import UUID

from osint_engine.domain.entities.entity import Edge
from osint_engine.domain.entities.nodes.company import CompanyID
from osint_engine.domain.entities.nodes.person import PersonID

PersonOwnsCompanyID = NewType("PersonOwnsCompanyID", UUID)


class PersonOwnsCompany(Edge[PersonOwnsCompanyID]):
    __slots__ = ()

    def __init__(self, *, source_id: PersonID, target_id: CompanyID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
