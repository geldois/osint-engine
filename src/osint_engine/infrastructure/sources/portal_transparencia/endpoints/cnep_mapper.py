from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING

from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.edges.company_received_sanction import (
    CompanyReceivedSanction,
)
from osint_engine.domain.entities.edges.person_received_sanction import (
    PersonReceivedSanction,
)
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.entities.nodes.sanction import Sanction
from osint_engine.infrastructure.errors.data_source_error import (
    UnexpectedFieldFormatError,
)

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.domain.entities.bases.edge import Edge
    from osint_engine.infrastructure.sources.payload import Payload


def _parse_fine_amount(*, value: str, source: str, key: str) -> Decimal:
    normalized = value.replace(".", "").replace(",", ".")

    try:
        return Decimal(normalized)
    except InvalidOperation as exception:
        raise UnexpectedFieldFormatError(
            source=source,
            key=key,
            raw_value=value,
            reason="not a valid pt-BR monetary amount",
        ) from exception


def _map_sanction(*, payload: Payload) -> Sanction:
    tipo_sancao = payload.scope(
        data=payload.require(key="tipoSancao", expected_type=dict[str, object])
    )
    orgao_sancionador = payload.scope(
        data=payload.require(key="orgaoSancionador", expected_type=dict[str, object])
    )

    return Sanction(
        end_date=payload.optional(key="dataFimSancao", expected_type=str),
        fine_amount=payload.optional(
            key="valorMulta",
            expected_type=str,
            cast_to=lambda value: _parse_fine_amount(
                value=value, source=payload.source, key="valorMulta"
            ),
        ),
        organ="CNEP",
        process_number=payload.optional(key="numeroProcesso", expected_type=str),
        publication_date=payload.optional(
            key="dataPublicacaoSancao", expected_type=str
        ),
        sanction_type=tipo_sancao.require(key="descricaoResumida", expected_type=str),
        sanctioning_body=orgao_sancionador.require(key="nome", expected_type=str),
        start_date=payload.optional(key="dataInicioSancao", expected_type=str),
    )


def _map_company_stub(*, payload: Payload) -> Company:
    return Company(
        activity_start_date=None,
        cnpj=payload.require(key="cnpjFormatado", expected_type=str),
        is_headquarters=None,
        legal_name=payload.optional(key="razaoSocialReceita", expected_type=str),
        legal_nature=None,
        registration_status=None,
        registration_status_date=None,
        registration_status_reason=None,
        share_capital=None,
        size_category=None,
        trade_name=payload.optional(key="nomeFantasiaReceita", expected_type=str),
    )


def _map_person_stub(*, payload: Payload) -> Person:
    return Person(
        age_range=None,
        cpf=payload.require(key="cpfFormatado", expected_type=str),
        name=payload.require(key="nome", expected_type=str),
    )


def map_graph(*, payload: Payload) -> Graph:
    sanction = _map_sanction(payload=payload)

    sancionado_payload = payload.scope(
        data=payload.require(key="pessoa", expected_type=dict[str, object])
    )

    sancionado: Company | Person
    edge: Edge[UUID, UUID, UUID]

    if sancionado_payload.optional(key="cnpjFormatado", expected_type=str) is not None:
        sancionado = _map_company_stub(payload=sancionado_payload)
        edge = CompanyReceivedSanction(source_id=sancionado.id, target_id=sanction.id)
    else:
        sancionado = _map_person_stub(payload=sancionado_payload)
        edge = PersonReceivedSanction(source_id=sancionado.id, target_id=sanction.id)

    nodes = frozenset({sanction, sancionado})

    return Graph(edges=frozenset({edge}), nodes=nodes, root_id=sancionado.id)
