from typing import NewType
from uuid import UUID

from osint_engine.domain.entities.entity import Edge
from osint_engine.domain.entities.nodes.cnae import CnaeID
from osint_engine.domain.entities.nodes.company import CompanyID

CompanyHasCnaeID = NewType("CompanyHasCnaeID", UUID)


class CompanyHasCnae(Edge[CompanyHasCnaeID]):
    __slots__ = ()

    def __init__(self, *, source_id: CompanyID, target_id: CnaeID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
