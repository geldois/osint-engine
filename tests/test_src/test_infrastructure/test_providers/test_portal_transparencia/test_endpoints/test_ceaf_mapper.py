from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.domain.entities.edges.person_received_sanction import (
    PersonReceivedSanction,
)
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.entities.nodes.sanction import Sanction
from osint_engine.infrastructure.providers.portal_transparencia.endpoints.ceaf_mapper import (  # noqa: E501
    _map_person_stub,  # pyright: ignore[reportPrivateUsage]
    _map_sanction,  # pyright: ignore[reportPrivateUsage]
    map_graph,
)

if TYPE_CHECKING:
    from osint_engine.infrastructure.providers.payload import Payload
    from tests.test_src.test_infrastructure.test_providers.conftest import MakePayload

_SANCTION_DATA: dict[str, object] = {
    "dataPublicacao": "2024-01-15",
    "fundamentacao": [{"codigo": "1", "descricao": "Lei 8.112/1990, art. 132"}],
    "id": 9911,
    "orgaoLotacao": {"nome": "Ministério da Fazenda"},
    "punicao": {"processo": "999/2024"},
    "tipoPunicao": {"descricao": "Demissão"},
}

_PERSON_SANCIONADO_DATA: dict[str, object] = {
    "cpfFormatado": "128.734.***-**",
    "nome": "TARCIANA PAULA GOMES MEDEIROS",
}


def _ceaf_payload_data(*, pessoa: dict[str, object]) -> dict[str, object]:
    return {**_SANCTION_DATA, "pessoa": pessoa}


class TestMapSanction:
    def test_maps_field_values_from_payload(self, make_payload: MakePayload) -> None:
        sanction = _map_sanction(
            payload=make_payload(provider="portal_transparencia", data=_SANCTION_DATA)
        )

        assert isinstance(sanction, Sanction)
        assert sanction.organ == "CEAF"
        assert sanction.source_id == "9911"
        assert sanction.sanction_type == "Demissão"
        assert sanction.sanctioning_body == "Ministério da Fazenda"
        assert sanction.process_number == "999/2024"
        assert sanction.publication_date == "2024-01-15"
        assert sanction.legal_basis == ("Lei 8.112/1990, art. 132",)
        assert sanction.start_date is None
        assert sanction.end_date is None
        assert sanction.fine_amount is None
        assert sanction.publication_link == ""

    def test_process_number_is_none_when_punicao_has_no_processo(
        self, make_payload: MakePayload
    ) -> None:
        data: dict[str, object] = {**_SANCTION_DATA, "punicao": {}}

        sanction = _map_sanction(
            payload=make_payload(provider="portal_transparencia", data=data)
        )

        assert sanction.process_number is None

    def test_legal_basis_is_empty_when_fundamentacao_is_absent(
        self, make_payload: MakePayload
    ) -> None:
        data = {
            key: value
            for key, value in _SANCTION_DATA.items()
            if key != "fundamentacao"
        }

        sanction = _map_sanction(
            payload=make_payload(provider="portal_transparencia", data=data)
        )

        assert sanction.legal_basis == ()


class TestMapPersonStub:
    def test_maps_field_values_and_leaves_age_range_unset(
        self, make_payload: MakePayload
    ) -> None:
        person = _map_person_stub(
            payload=make_payload(
                provider="portal_transparencia", data=_PERSON_SANCIONADO_DATA
            )
        )

        assert isinstance(person, Person)
        assert person.cpf == "128.734.***-**"
        assert person.name == "TARCIANA PAULA GOMES MEDEIROS"
        assert person.age_range is None


class TestMapGraph:
    def test_builds_a_person_and_a_sanction_with_a_received_sanction_edge(
        self, make_payload: MakePayload
    ) -> None:
        graph = map_graph(
            payload=make_payload(
                provider="portal_transparencia",
                data=_ceaf_payload_data(pessoa=_PERSON_SANCIONADO_DATA),
            )
        )

        assert any(isinstance(node, Person) for node in graph.nodes)
        assert any(isinstance(node, Sanction) for node in graph.nodes)
        assert any(isinstance(edge, PersonReceivedSanction) for edge in graph.edges)

    def test_root_id_is_the_person_not_the_sanction(
        self, make_payload: MakePayload
    ) -> None:
        graph = map_graph(
            payload=make_payload(
                provider="portal_transparencia",
                data=_ceaf_payload_data(pessoa=_PERSON_SANCIONADO_DATA),
            )
        )

        sanction_ids = {node.id for node in graph.nodes if isinstance(node, Sanction)}

        assert graph.root_id not in sanction_ids

    def test_all_edge_endpoints_are_in_node_set(
        self, make_payload: MakePayload
    ) -> None:
        graph = map_graph(
            payload=make_payload(
                provider="portal_transparencia",
                data=_ceaf_payload_data(pessoa=_PERSON_SANCIONADO_DATA),
            )
        )

        node_ids = {node.id for node in graph.nodes}

        for edge in graph.edges:
            assert edge.source_id in node_ids
            assert edge.target_id in node_ids

    def test_graph_has_exactly_two_nodes(self, make_payload: MakePayload) -> None:
        graph = map_graph(
            payload=make_payload(
                provider="portal_transparencia",
                data=_ceaf_payload_data(pessoa=_PERSON_SANCIONADO_DATA),
            )
        )

        assert len(graph.nodes) == 2


class TestMapGraphWithRealAPISnapshot:
    def test_does_not_raise_with_real_api_snapshot(
        self, portal_transparencia_ceaf_valid_payload: Payload
    ) -> None:
        map_graph(payload=portal_transparencia_ceaf_valid_payload)
