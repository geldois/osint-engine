from __future__ import annotations

from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.entities.nodes.address import AddressID
from osint_engine.domain.entities.nodes.company import CompanyID
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

CompanyLocatedAtID = NewType("CompanyLocatedAtID", UUID)


class CompanyLocatedAt(
    Edge[CompanyLocatedAtID, CompanyID, AddressID],
    namespace=EntityNAMESPACE.COMPANY_ADDRESS,
):
    @override
    def __init__(self, *, source_id: CompanyID, target_id: AddressID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
