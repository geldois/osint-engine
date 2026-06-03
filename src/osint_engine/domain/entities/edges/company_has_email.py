from typing import NewType
from uuid import UUID

from osint_engine.domain.entities.entity import Edge
from osint_engine.domain.entities.nodes.company import CompanyID
from osint_engine.domain.entities.nodes.email import EmailID

CompanyHasEmailID = NewType("CompanyHasEmailID", UUID)


class CompanyHasEmail(Edge[CompanyHasEmailID]):
    __slots__ = ()

    def __init__(self, *, source_id: CompanyID, target_id: EmailID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
