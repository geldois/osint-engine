from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from osint_engine.domain.entities.edges.person_has_political_exposure import (
    PersonHasPoliticalExposure,
)
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.entities.nodes.political_exposure import PoliticalExposure
from osint_engine.infrastructure.providers.portal_transparencia.endpoints.pep_mapper import (  # noqa: E501
    _map_person_stub,  # pyright: ignore[reportPrivateUsage]
    _map_political_exposure,  # pyright: ignore[reportPrivateUsage]
    map_graph,
)

if TYPE_CHECKING:
    from osint_engine.infrastructure.providers.payload import Payload
    from tests.test_src.test_infrastructure.test_providers.conftest import MakePayload

_PEP_DATA: dict[str, object] = {
    "cpf": "100.000.000-00",
    "nome": "FULANO DE TAL                    ",
    "sigla_funcao": "MIN   ",
    "descricao_funcao": "MINISTRO DE ESTADO",
    "nivel_funcao": "1",
    "cod_orgao": "26000",
    "nome_orgao": "MINISTERIO DA FAZENDA        ",
    "dt_inicio_exercicio": "2023-01-01",
    "dt_fim_exercicio": "",
    "dt_fim_carencia": "",
}


class TestMapPoliticalExposure:
    def test_maps_field_values_from_payload(self, make_payload: MakePayload) -> None:
        political_exposure = _map_political_exposure(
            payload=make_payload(provider="portal_transparencia", data=_PEP_DATA)
        )

        assert isinstance(political_exposure, PoliticalExposure)
        assert political_exposure.cpf == "100.000.000-00"
        assert political_exposure.function_acronym == "MIN"
        assert political_exposure.function_description == "MINISTRO DE ESTADO"
        assert political_exposure.function_level == "1"
        assert political_exposure.government_body_code == "26000"
        assert political_exposure.government_body_name == "MINISTERIO DA FAZENDA"
        assert political_exposure.exercise_start_date == "2023-01-01"
        assert political_exposure.exercise_end_date is None
        assert political_exposure.grace_period_end_date is None


class TestMapPersonStub:
    def test_maps_field_values_and_leaves_enrichment_fields_unset(
        self, make_payload: MakePayload
    ) -> None:
        person = _map_person_stub(
            payload=make_payload(provider="portal_transparencia", data=_PEP_DATA)
        )

        assert isinstance(person, Person)
        assert person.cpf == "100.000.000-00"
        assert person.name == "FULANO DE TAL"
        assert person.age_range is None


class TestMapGraph:
    def test_builds_a_person_and_political_exposure_with_an_edge_between_them(
        self, make_payload: MakePayload
    ) -> None:
        graph = map_graph(
            payload=make_payload(provider="portal_transparencia", data=_PEP_DATA)
        )

        assert any(isinstance(node, Person) for node in graph.nodes)
        assert any(isinstance(node, PoliticalExposure) for node in graph.nodes)
        assert any(isinstance(edge, PersonHasPoliticalExposure) for edge in graph.edges)

    def test_root_id_is_the_person_not_the_political_exposure(
        self, make_payload: MakePayload
    ) -> None:
        graph = map_graph(
            payload=make_payload(provider="portal_transparencia", data=_PEP_DATA)
        )

        political_exposure_ids = {
            node.id for node in graph.nodes if isinstance(node, PoliticalExposure)
        }

        assert graph.root_id not in political_exposure_ids

    def test_all_edge_endpoints_are_in_node_set(
        self, make_payload: MakePayload
    ) -> None:
        graph = map_graph(
            payload=make_payload(provider="portal_transparencia", data=_PEP_DATA)
        )

        node_ids = {node.id for node in graph.nodes}

        for edge in graph.edges:
            assert edge.source_id in node_ids
            assert edge.target_id in node_ids

    def test_graph_has_exactly_two_nodes(self, make_payload: MakePayload) -> None:
        graph = map_graph(
            payload=make_payload(provider="portal_transparencia", data=_PEP_DATA)
        )

        assert len(graph.nodes) == 2


@pytest.mark.real_api_snapshot
class TestMapGraphWithRealAPISnapshot:
    def test_does_not_raise_with_real_api_snapshot(
        self, portal_transparencia_pep_valid_payload: Payload
    ) -> None:
        map_graph(payload=portal_transparencia_pep_valid_payload)
