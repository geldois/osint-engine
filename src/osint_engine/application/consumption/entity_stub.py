from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.person import Person

if TYPE_CHECKING:
    from uuid import UUID

_CPF_DIGIT_LENGTH = 11


def person_stub(cpf: str, /) -> Person:
    return Person(
        age_range=None,
        birthdate=None,
        cpf=cpf,
        name=None,
        registration_date=None,
        registration_status=None,
    )


def company_stub(cnpj: str, /) -> Company:
    return Company(
        activity_start_date=None,
        cnpj=cnpj,
        is_headquarters=None,
        legal_name=None,
        legal_nature=None,
        registration_status=None,
        registration_status_date=None,
        registration_status_reason=None,
        share_capital=None,
        size_category=None,
        trade_name=None,
    )


def stub_id_for(cpf_or_cnpj: str, /) -> UUID:
    if len(cpf_or_cnpj) == _CPF_DIGIT_LENGTH:
        return person_stub(cpf_or_cnpj).id

    return company_stub(cpf_or_cnpj).id
