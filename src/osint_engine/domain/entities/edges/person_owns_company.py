from __future__ import annotations

from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.entities.nodes.company import CompanyID
from osint_engine.domain.entities.nodes.person import PersonID
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

PersonOwnsCompanyID = NewType("PersonOwnsCompanyID", UUID)


class PersonOwnsCompany(
    Edge[PersonOwnsCompanyID, PersonID, CompanyID],
    id_fields=None,
    namespace=EntityNAMESPACE.PERSON_COMPANY,
):
    entry_date: str
    role: str

    @override
    def __init__(
        self, *, source_id: PersonID, target_id: CompanyID, entry_date: str, role: str
    ) -> None:
        super().__init__(
            source_id=source_id,
            target_id=target_id,
            entry_date=entry_date,
            role=role,
        )
