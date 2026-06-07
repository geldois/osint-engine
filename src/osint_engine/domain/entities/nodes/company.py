from typing import NewType
from uuid import UUID

from osint_engine.domain.entities.entity import Node
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

CompanyID = NewType("CompanyID", UUID)


class Company(Node[CompanyID], namespace=EntityNAMESPACE.COMPANY):
    __slots__ = ("cnpj", "company_status", "name")

    cnpj: str
    company_status: str
    name: str

    def __init__(self, *, cnpj: str, company_status: str, name: str) -> None:
        super().__init__(cnpj=cnpj, company_status=company_status, name=name)
