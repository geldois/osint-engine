from __future__ import annotations

from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

CompanyID = NewType("CompanyID", UUID)


class Company(Node[CompanyID], namespace=EntityNAMESPACE.COMPANY):
    cnpj: str
    company_status: str
    name: str

    @override
    def __init__(self, *, cnpj: str, company_status: str, name: str) -> None:
        super().__init__(cnpj=cnpj, company_status=company_status, name=name)
