from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.nodes.person import Person

if TYPE_CHECKING:
    from osint_engine.infrastructure.sources.payload import Payload


def _map_person(*, payload: Payload) -> Person:
    return Person(
        age_range=None,
        birthdate=None,
        cpf=payload.require(key="cpf", expected_type=str),
        name=payload.require(key="nome", expected_type=str),
    )


def map_graph(*, payload: Payload) -> Graph:
    person = _map_person(payload=payload)

    return Graph(edges=frozenset(), nodes=frozenset({person}), root_id=person.id)
