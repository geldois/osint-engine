from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.domain.entities.nodes.person import Person
from osint_engine.infrastructure.providers.kipflow.endpoints.cpf_mapper import (
    _map_person,  # pyright: ignore[reportPrivateUsage]
    map_graph,
)

if TYPE_CHECKING:
    from tests.test_src.test_infrastructure.test_providers.conftest import MakePayload

_TEST_CPF = "52998224563"

_FULL_DATA: dict[str, object] = {
    "cpf": _TEST_CPF,
    "nome": "FULANO DE TAL",
    "nasc": "1990-01-01",
    "situacao_cadastral": "REGULAR",
    "data_inscricao": "2010-05-20",
}

_MINIMAL_DATA: dict[str, object] = {"cpf": _TEST_CPF}


class TestMapPerson:
    def test_maps_every_field_when_all_are_present(
        self, make_payload: MakePayload
    ) -> None:
        person = _map_person(payload=make_payload(provider="kipflow", data=_FULL_DATA))

        assert isinstance(person, Person)
        assert person.cpf == _TEST_CPF
        assert person.name == "FULANO DE TAL"
        assert person.birthdate == "1990-01-01"
        assert person.registration_status == "REGULAR"
        assert person.registration_date == "2010-05-20"
        assert person.age_range is None

    def test_leaves_optional_fields_none_when_only_cpf_is_present(
        self, make_payload: MakePayload
    ) -> None:
        person = _map_person(
            payload=make_payload(provider="kipflow", data=_MINIMAL_DATA)
        )

        assert person.cpf == _TEST_CPF
        assert person.name is None
        assert person.birthdate is None
        assert person.registration_status is None
        assert person.registration_date is None


class TestMapGraph:
    def test_returns_a_single_node_graph_rooted_at_the_person(
        self, make_payload: MakePayload
    ) -> None:
        graph = map_graph(payload=make_payload(provider="kipflow", data=_FULL_DATA))

        assert len(graph.nodes) == 1
        assert not graph.edges

        person = next(iter(graph.nodes))

        assert isinstance(person, Person)
        assert graph.root_id == person.id
