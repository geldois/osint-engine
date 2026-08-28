from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.edges.company_is_party_in_legal_process import (
    CompanyIsPartyInLegalProcess,
)
from osint_engine.domain.entities.edges.person_is_party_in_legal_process import (
    PersonIsPartyInLegalProcess,
)
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.legal_process import LegalProcess
from osint_engine.domain.entities.nodes.person import Person

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.domain.entities.bases.edge import Edge
    from osint_engine.infrastructure.providers.payload import Payload

_CPF_LENGTH = 11


def _map_legal_process(*, payload: Payload) -> LegalProcess:
    classe_processual = payload.optional(
        key="classeProcessual", expected_type=dict[str, object]
    )
    valor_causa = payload.optional(key="valorCausa", expected_type=dict[str, object])
    status_predictus = payload.optional(
        key="statusPredictus", expected_type=dict[str, object]
    )

    process_class = (
        payload.scope(data=classe_processual).optional(key="nome", expected_type=str)
        if classe_processual is not None
        else None
    )
    lawsuit_value = (
        payload.scope(data=valor_causa).optional(
            key="valor",
            expected_type=int | float,
            cast_to=lambda value: Decimal(str(value)),
        )
        if valor_causa is not None
        else None
    )
    lawsuit_value_currency = (
        payload.scope(data=valor_causa).optional(key="moeda", expected_type=str)
        if valor_causa is not None
        else None
    )
    current_status = (
        payload.scope(data=status_predictus).optional(
            key="statusProcesso", expected_type=str
        )
        if status_predictus is not None
        else None
    )
    execution_value = (
        payload.scope(data=status_predictus).optional(
            key="valorExecucao",
            expected_type=int | float,
            cast_to=lambda value: Decimal(str(value)),
        )
        if status_predictus is not None
        else None
    )

    return LegalProcess(
        court=payload.optional(key="tribunal", expected_type=str),
        current_status=current_status,
        distribution_date=payload.optional(key="dataDistribuicao", expected_type=str),
        execution_value=execution_value,
        is_secret_of_justice=payload.optional(
            key="eSegredoJustica", expected_type=bool
        ),
        lawsuit_value=lawsuit_value,
        lawsuit_value_currency=lawsuit_value_currency,
        process_class=process_class,
        process_number=payload.require(key="numeroProcessoUnico", expected_type=str),
        process_url=payload.optional(key="urlProcesso", expected_type=str),
        state=payload.optional(key="uf", expected_type=str),
    )


def _map_person_stub(*, cpf: str) -> Person:
    return Person(
        age_range=None,
        birthdate=None,
        cpf=cpf,
        name=None,
        registration_date=None,
        registration_status=None,
    )


def _map_company_stub(*, cnpj: str) -> Company:
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


def map_graph(*, cpf_or_cnpj: str, payload: Payload) -> Graph:
    legal_process = _map_legal_process(payload=payload)

    party: Company | Person
    edge: Edge[UUID, UUID, UUID]

    if len(cpf_or_cnpj) == _CPF_LENGTH:
        party = _map_person_stub(cpf=cpf_or_cnpj)
        edge = PersonIsPartyInLegalProcess(
            source_id=party.id, target_id=legal_process.id
        )
    else:
        party = _map_company_stub(cnpj=cpf_or_cnpj)
        edge = CompanyIsPartyInLegalProcess(
            source_id=party.id, target_id=legal_process.id
        )

    nodes = frozenset({legal_process, party})

    return Graph(edges=frozenset({edge}), nodes=nodes, root_id=party.id)
