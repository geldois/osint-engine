from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.edges.company_received_sanction import (
    CompanyReceivedSanction,
)
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.sanction import Sanction

if TYPE_CHECKING:
    from osint_engine.infrastructure.providers.payload import Payload


def _map_sanction(*, payload: Payload) -> Sanction:
    orgao_superior = payload.scope(
        data=payload.require(key="orgaoSuperior", expected_type=dict[str, object])
    )

    return Sanction(
        end_date=None,
        fine_amount=None,
        legal_basis=(),
        organ="CEPIM",
        process_number=None,
        publication_date=payload.optional(key="dataReferencia", expected_type=str),
        publication_link="",
        sanction_type=payload.require(key="motivo", expected_type=str),
        sanctioning_body=orgao_superior.require(key="nome", expected_type=str),
        source_id=str(payload.require(key="id", expected_type=int)),
        start_date=None,
    )


def _map_company_stub(*, payload: Payload) -> Company:
    return Company(
        activity_start_date=None,
        cnpj=payload.require(key="cnpjFormatado", expected_type=str),
        is_headquarters=None,
        legal_name=payload.require(key="razaoSocialReceita", expected_type=str),
        legal_nature=None,
        registration_status=None,
        registration_status_date=None,
        registration_status_reason=None,
        share_capital=None,
        size_category=None,
        trade_name=payload.optional(key="nomeFantasiaReceita", expected_type=str),
    )


def map_graph(*, payload: Payload) -> Graph:
    sanction = _map_sanction(payload=payload)
    company = _map_company_stub(
        payload=payload.scope(
            data=payload.require(key="pessoaJuridica", expected_type=dict[str, object])
        )
    )
    edge = CompanyReceivedSanction(source_id=company.id, target_id=sanction.id)

    return Graph(
        edges=frozenset({edge}),
        nodes=frozenset({sanction, company}),
        root_id=company.id,
    )
