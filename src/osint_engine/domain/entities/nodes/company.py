from __future__ import annotations

from typing import TYPE_CHECKING, NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

if TYPE_CHECKING:
    from decimal import Decimal

CompanyID = NewType("CompanyID", UUID)


class Company(
    Node[CompanyID], id_fields=frozenset({"cnpj"}), namespace=EntityNAMESPACE.COMPANY
):
    activity_start_date: str
    cnpj: str
    is_headquarters: bool
    legal_name: str
    legal_nature: str
    registration_status: str
    registration_status_date: str
    registration_status_reason: str
    share_capital: Decimal
    size_category: str
    trade_name: str

    @override
    def __init__(
        self,
        *,
        activity_start_date: str,
        cnpj: str,
        is_headquarters: bool,
        legal_name: str,
        legal_nature: str,
        registration_status: str,
        registration_status_date: str,
        registration_status_reason: str,
        share_capital: Decimal,
        size_category: str,
        trade_name: str,
    ) -> None:
        super().__init__(
            **{
                key: value
                for key, value in locals().items()
                if key not in {"__class__", "self"}
            }
        )
