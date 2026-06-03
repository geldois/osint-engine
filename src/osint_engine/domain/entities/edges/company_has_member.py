from typing import NewType
from uuid import UUID

from osint_engine.domain.entities.entity import Edge
from osint_engine.domain.entities.nodes.company import CompanyID
from osint_engine.domain.entities.nodes.person import PersonID

CompanyHasMemberID = NewType("CompanyHasMemberID", UUID)


class CompanyHasMember(Edge[CompanyHasMemberID]):
    __slots__ = ()

    def __init__(self, *, source_id: CompanyID, target_id: PersonID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
