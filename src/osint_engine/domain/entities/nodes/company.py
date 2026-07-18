from __future__ import annotations

from typing import TYPE_CHECKING, NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.errors.entity_error import EntityInvalidIdentifierError
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE
from osint_engine.domain.value_objects.normalization import normalize_str_to_digits_only

if TYPE_CHECKING:
    from decimal import Decimal

CompanyID = NewType("CompanyID", UUID)

_CNPJ_DIGIT_LENGTH = 14


class Company(
    Node[CompanyID], id_fields=frozenset({"cnpj"}), namespace=EntityNAMESPACE.COMPANY
):
    activity_start_date: str | None
    cnpj: str
    is_headquarters: bool | None
    legal_name: str | None
    legal_nature: str | None
    registration_status: str | None
    registration_status_date: str | None
    registration_status_reason: str | None
    share_capital: Decimal | None
    size_category: str | None
    trade_name: str | None

    @override
    def __init__(
        self,
        *,
        activity_start_date: str | None,
        cnpj: str,
        is_headquarters: bool | None,
        legal_name: str | None,
        legal_nature: str | None,
        registration_status: str | None,
        registration_status_date: str | None,
        registration_status_reason: str | None,
        share_capital: Decimal | None,
        size_category: str | None,
        trade_name: str | None,
    ) -> None:
        super().__init__(
            **{
                key: value
                for key, value in locals().items()
                if key not in {"__class__", "self"}
            }
        )

    @classmethod
    @override
    def _calculate_id(cls, **kwargs: object) -> CompanyID:
        cnpj = kwargs["cnpj"]

        if isinstance(cnpj, str):
            normalized = normalize_str_to_digits_only(value=cnpj)

            if len(normalized) != _CNPJ_DIGIT_LENGTH:
                raise EntityInvalidIdentifierError(
                    subject=cls,
                    field="cnpj",
                    raw_value=cnpj,
                    expected_length=_CNPJ_DIGIT_LENGTH,
                    actual_length=len(normalized),
                )

            kwargs["cnpj"] = normalized

        return super()._calculate_id(**kwargs)
