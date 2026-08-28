from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.edges.person_has_political_exposure import (
    PersonHasPoliticalExposure,
)
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.entities.nodes.political_exposure import PoliticalExposure

if TYPE_CHECKING:
    from osint_engine.infrastructure.providers.payload import Payload


def _map_political_exposure(*, payload: Payload) -> PoliticalExposure:
    return PoliticalExposure(
        cpf=payload.require(key="cpf", expected_type=str),
        exercise_end_date=payload.optional(key="dt_fim_exercicio", expected_type=str),
        exercise_start_date=payload.optional(
            key="dt_inicio_exercicio", expected_type=str
        ),
        function_acronym=payload.optional(key="sigla_funcao", expected_type=str),
        function_description=payload.require(key="descricao_funcao", expected_type=str),
        function_level=payload.optional(key="nivel_funcao", expected_type=str),
        government_body_code=payload.optional(key="cod_orgao", expected_type=str),
        government_body_name=payload.require(key="nome_orgao", expected_type=str),
        grace_period_end_date=payload.optional(
            key="dt_fim_carencia", expected_type=str
        ),
    )


def _map_person_stub(*, payload: Payload) -> Person:
    return Person(
        age_range=None,
        birthdate=None,
        cpf=payload.require(key="cpf", expected_type=str),
        name=payload.require(key="nome", expected_type=str),
        registration_date=None,
        registration_status=None,
    )


def map_graph(*, payload: Payload) -> Graph:
    political_exposure = _map_political_exposure(payload=payload)
    person = _map_person_stub(payload=payload)

    edge = PersonHasPoliticalExposure(
        source_id=person.id, target_id=political_exposure.id
    )

    return Graph(
        edges=frozenset({edge}),
        nodes=frozenset({person, political_exposure}),
        root_id=person.id,
    )
