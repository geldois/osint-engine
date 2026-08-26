from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.edges.person_received_sanction import (
    PersonReceivedSanction,
)
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.entities.nodes.sanction import Sanction

if TYPE_CHECKING:
    from osint_engine.infrastructure.providers.payload import Payload


def _map_sanction(*, payload: Payload) -> Sanction:
    tipo_punicao = payload.scope(
        data=payload.require(key="tipoPunicao", expected_type=dict[str, object])
    )
    orgao_lotacao = payload.scope(
        data=payload.require(key="orgaoLotacao", expected_type=dict[str, object])
    )
    punicao = payload.scope(
        data=payload.require(key="punicao", expected_type=dict[str, object])
    )

    fundamentacao = (
        payload.optional(key="fundamentacao", expected_type=list[dict[str, object]])
        or []
    )

    return Sanction(
        end_date=None,
        fine_amount=None,
        legal_basis=tuple(
            payload.scope(data=item).require(key="descricao", expected_type=str)
            for item in fundamentacao
        ),
        organ="CEAF",
        process_number=punicao.optional(key="processo", expected_type=str),
        publication_date=payload.optional(key="dataPublicacao", expected_type=str),
        publication_link="",
        sanction_type=tipo_punicao.require(key="descricao", expected_type=str),
        sanctioning_body=orgao_lotacao.require(key="nome", expected_type=str),
        source_id=str(payload.require(key="id", expected_type=int)),
        start_date=None,
    )


def _map_person_stub(*, payload: Payload) -> Person:
    return Person(
        age_range=None,
        birthdate=None,
        cpf=payload.require(key="cpfFormatado", expected_type=str),
        name=payload.require(key="nome", expected_type=str),
        registration_date=None,
        registration_status=None,
    )


def map_graph(*, payload: Payload) -> Graph:
    sanction = _map_sanction(payload=payload)
    person = _map_person_stub(
        payload=payload.scope(
            data=payload.require(key="pessoa", expected_type=dict[str, object])
        )
    )
    edge = PersonReceivedSanction(source_id=person.id, target_id=sanction.id)

    return Graph(
        edges=frozenset({edge}), nodes=frozenset({sanction, person}), root_id=person.id
    )
