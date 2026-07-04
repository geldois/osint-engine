from __future__ import annotations

from typing import TYPE_CHECKING, NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

if TYPE_CHECKING:
    from decimal import Decimal

CompanyID = NewType("CompanyID", UUID)


class Company(Node[CompanyID], namespace=EntityNAMESPACE.COMPANY):
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
            identity_fields=frozenset({"cnpj"}),
            activity_start_date=activity_start_date,
            cnpj=cnpj,
            is_headquarters=is_headquarters,
            legal_name=legal_name,
            legal_nature=legal_nature,
            registration_status=registration_status,
            registration_status_date=registration_status_date,
            registration_status_reason=registration_status_reason,
            share_capital=share_capital,
            size_category=size_category,
            trade_name=trade_name,
        )
