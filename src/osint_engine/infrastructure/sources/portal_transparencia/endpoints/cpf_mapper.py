from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.nodes.person import Person

if TYPE_CHECKING:
    from osint_engine.infrastructure.sources.payload import Payload


def _map_person(*, payload: Payload) -> Person:
    return Person(
        age_range=None,
        cpf=payload.require(key="cpf", expected_type=str),
        name=payload.require(key="nome", expected_type=str),
    )


def map_graph(*, payload: Payload) -> Graph:
    # The "/pf" endpoint's ~25 boolean flags (sancionadoCEIS, servidor,
    # favorecidoBolsaFamilia, ...) each index into a *different* Portal da
    # Transparência dataset rather than describing an attribute of the
    # person itself — CEIS/CNEP already have their own dedicated expansions,
    # and the rest are future expansions in that same shape, not fields to
    # collapse onto this node. This endpoint only anchors the Person node,
    # mirroring how "/cnpj" only anchors the Company node.
    person = _map_person(payload=payload)

    return Graph(edges=frozenset(), nodes=frozenset({person}), root_id=person.id)
