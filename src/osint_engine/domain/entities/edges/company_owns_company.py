from __future__ import annotations

from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.entities.nodes.company import CompanyID
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

CompanyOwnsCompanyID = NewType("CompanyOwnsCompanyID", UUID)


class CompanyOwnsCompany(
    Edge[CompanyOwnsCompanyID, CompanyID, CompanyID],
    id_fields=None,
    namespace=EntityNAMESPACE.COMPANY_COMPANY,
):
    entry_date: str
    role: str

    @override
    def __init__(
        self, *, source_id: CompanyID, target_id: CompanyID, entry_date: str, role: str
    ) -> None:
        super().__init__(
            source_id=source_id, target_id=target_id, entry_date=entry_date, role=role
        )
