from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.nodes.person import Person

if TYPE_CHECKING:
    from osint_engine.infrastructure.providers.payload import Payload


def _map_person(*, payload: Payload) -> Person:
    return Person(
        age_range=None,
        birthdate=payload.optional(key="nasc", expected_type=str),
        cpf=payload.require(key="cpf", expected_type=str),
        name=payload.optional(key="nome", expected_type=str),
        registration_date=payload.optional(key="data_inscricao", expected_type=str),
        registration_status=payload.optional(
            key="situacao_cadastral", expected_type=str
        ),
    )


def map_graph(*, payload: Payload) -> Graph:
    person = _map_person(payload=payload)

    return Graph(edges=frozenset(), nodes=frozenset({person}), root_id=person.id)
