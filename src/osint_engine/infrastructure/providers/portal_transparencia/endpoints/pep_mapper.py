from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.domain.entities.edges import PersonHasPoliticalExposure
from osint_engine.domain.entities.graphs import CompositeGraph
from osint_engine.domain.entities.nodes import Person, PoliticalExposure

if TYPE_CHECKING:
    from osint_engine.infrastructure.providers.payload import Payload


def _stripped(*, payload: Payload, key: str) -> str:
    return payload.require(key=key, expected_type=str).strip()


def _stripped_or_none(*, payload: Payload, key: str) -> str | None:
    value = payload.optional(key=key, expected_type=str)

    return value.strip() or None if value is not None else None


def _map_political_exposure(*, payload: Payload) -> PoliticalExposure:
    return PoliticalExposure(
        cpf=payload.require(key="cpf", expected_type=str),
        exercise_end_date=_stripped_or_none(payload=payload, key="dt_fim_exercicio"),
        exercise_start_date=_stripped_or_none(
            payload=payload, key="dt_inicio_exercicio"
        ),
        function_acronym=_stripped_or_none(payload=payload, key="sigla_funcao"),
        function_description=_stripped(payload=payload, key="descricao_funcao"),
        function_level=_stripped_or_none(payload=payload, key="nivel_funcao"),
        government_body_code=_stripped_or_none(payload=payload, key="cod_orgao"),
        government_body_name=_stripped(payload=payload, key="nome_orgao"),
        grace_period_end_date=_stripped_or_none(payload=payload, key="dt_fim_carencia"),
    )


def _map_person_stub(*, payload: Payload) -> Person:
    return Person(
        age_range=None,
        birthdate=None,
        cpf=payload.require(key="cpf", expected_type=str),
        name=_stripped(payload=payload, key="nome"),
        registration_date=None,
        registration_status=None,
    )


def map_graph(*, payload: Payload) -> CompositeGraph:
    political_exposure = _map_political_exposure(payload=payload)
    person = _map_person_stub(payload=payload)

    edge = PersonHasPoliticalExposure(
        source_id=person.id, target_id=political_exposure.id
    )

    return CompositeGraph(
        edges=frozenset({edge}),
        nodes=frozenset({person, political_exposure}),
        root_id=person.id,
    )
