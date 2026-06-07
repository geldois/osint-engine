from typing import NewType
from uuid import UUID

from osint_engine.domain.entities.entity import Edge
from osint_engine.domain.entities.nodes.cnae import CnaeID
from osint_engine.domain.entities.nodes.company import CompanyID
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

CompanyHasCnaeID = NewType("CompanyHasCnaeID", UUID)


class CompanyHasCnae(
    Edge[CompanyHasCnaeID], namespace=EntityNAMESPACE.COMPANY_CNAE
):
    __slots__ = ()

    source_id: CompanyID
    target_id: CnaeID

    def __init__(self, *, source_id: CompanyID, target_id: CnaeID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
