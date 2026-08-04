from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.domain.entities.nodes.person import Person
from osint_engine.infrastructure.sources.portal_transparencia.endpoints.cpf_mapper import (  # noqa: E501
    _map_person,  # pyright: ignore[reportPrivateUsage]
    map_graph,
)

if TYPE_CHECKING:
    from tests.test_src.test_infrastructure.test_sources.conftest import MakePayload


_PF_DATA: dict[str, object] = {
    "cpf": "128.734.***-**",
    "nome": "TARCIANA PAULA GOMES MEDEIROS",
    "sancionadoCEIS": False,
    "sancionadoCNEP": False,
    "servidor": True,
}


class TestMapPerson:
    def test_maps_field_values_and_leaves_age_range_unset(
        self, make_payload: MakePayload
    ) -> None:
        person = _map_person(
            payload=make_payload(source="portal_transparencia", data=_PF_DATA)
        )

        assert isinstance(person, Person)
        assert person.cpf == "128.734.***-**"
        assert person.name == "TARCIANA PAULA GOMES MEDEIROS"
        assert person.age_range is None


class TestMapGraph:
    def test_returns_a_single_node_graph_rooted_at_the_person(
        self, make_payload: MakePayload
    ) -> None:
        graph = map_graph(
            payload=make_payload(source="portal_transparencia", data=_PF_DATA)
        )

        assert len(graph.nodes) == 1
        assert not graph.edges

        person = next(iter(graph.nodes))

        assert isinstance(person, Person)
        assert graph.root_id == person.id

    def test_ignores_the_categorical_flag_fields(
        self, make_payload: MakePayload
    ) -> None:
        graph = map_graph(
            payload=make_payload(source="portal_transparencia", data=_PF_DATA)
        )

        assert len(graph.nodes) == 1
