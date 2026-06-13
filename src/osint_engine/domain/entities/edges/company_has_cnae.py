from __future__ import annotations

from typing import TYPE_CHECKING, NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

if TYPE_CHECKING:
    from osint_engine.domain.entities.nodes.cnae import CnaeID
    from osint_engine.domain.entities.nodes.company import CompanyID

CompanyHasCnaeID = NewType("CompanyHasCnaeID", UUID)


class CompanyHasCnae(Edge[CompanyHasCnaeID], namespace=EntityNAMESPACE.COMPANY_CNAE):
    source_id: CompanyID
    target_id: CnaeID

    @override
    def __init__(self, *, source_id: CompanyID, target_id: CnaeID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
