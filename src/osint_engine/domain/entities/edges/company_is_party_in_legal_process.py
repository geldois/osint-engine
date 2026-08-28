from __future__ import annotations

from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.entities.nodes.company import CompanyID
from osint_engine.domain.entities.nodes.legal_process import LegalProcessID
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

CompanyIsPartyInLegalProcessID = NewType("CompanyIsPartyInLegalProcessID", UUID)


class CompanyIsPartyInLegalProcess(
    Edge[CompanyIsPartyInLegalProcessID, CompanyID, LegalProcessID],
    id_fields=None,
    namespace=EntityNAMESPACE.COMPANY_LEGAL_PROCESS,
):
    @override
    def __init__(self, *, source_id: CompanyID, target_id: LegalProcessID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
