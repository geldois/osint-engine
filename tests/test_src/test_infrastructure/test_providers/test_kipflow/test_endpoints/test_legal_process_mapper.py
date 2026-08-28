from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from osint_engine.domain.entities.edges.company_is_party_in_legal_process import (
    CompanyIsPartyInLegalProcess,
)
from osint_engine.domain.entities.edges.person_is_party_in_legal_process import (
    PersonIsPartyInLegalProcess,
)
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.legal_process import LegalProcess
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.infrastructure.providers.kipflow.endpoints.legal_process_mapper import (  # noqa: E501
    _map_company_stub,  # pyright: ignore[reportPrivateUsage]
    _map_legal_process,  # pyright: ignore[reportPrivateUsage]
    _map_person_stub,  # pyright: ignore[reportPrivateUsage]
    map_graph,
)

if TYPE_CHECKING:
    from tests.test_src.test_infrastructure.test_providers.conftest import MakePayload

_TEST_CPF = "52998224563"
_TEST_CNPJ = "35965725000107"

_LEGAL_PROCESS_DATA: dict[str, object] = {
    "numeroProcessoUnico": "0001234-56.2024.8.26.0100",
    "urlProcesso": "https://kipflow.io/processos/0001234",
    "tribunal": "TJSP",
    "uf": "SP",
    "classeProcessual": {"nome": "Execução de Título Extrajudicial"},
    "dataDistribuicao": "2024-03-10",
    "valorCausa": {"valor": 150000.50, "moeda": "BRL"},
    "eSegredoJustica": False,
    "statusPredictus": {"statusProcesso": "Em andamento", "valorExecucao": 150000.50},
}


class TestMapLegalProcess:
    def test_maps_field_values_from_payload(self, make_payload: MakePayload) -> None:
        legal_process = _map_legal_process(
            payload=make_payload(provider="kipflow", data=_LEGAL_PROCESS_DATA)
        )

        assert isinstance(legal_process, LegalProcess)
        assert legal_process.process_number == "0001234-56.2024.8.26.0100"
        assert legal_process.process_url == "https://kipflow.io/processos/0001234"
        assert legal_process.court == "TJSP"
        assert legal_process.state == "SP"
        assert legal_process.process_class == "Execução de Título Extrajudicial"
        assert legal_process.distribution_date == "2024-03-10"
        assert legal_process.lawsuit_value == Decimal("150000.5")
        assert legal_process.lawsuit_value_currency == "BRL"
        assert legal_process.is_secret_of_justice is False
        assert legal_process.current_status == "Em andamento"
        assert legal_process.execution_value == Decimal("150000.5")

    def test_tolerates_missing_nested_objects(self, make_payload: MakePayload) -> None:
        data = {
            "numeroProcessoUnico": "0001234-56.2024.8.26.0100",
        }

        legal_process = _map_legal_process(
            payload=make_payload(provider="kipflow", data=data)
        )

        assert legal_process.process_class is None
        assert legal_process.lawsuit_value is None
        assert legal_process.current_status is None
        assert legal_process.execution_value is None


class TestMapPersonStub:
    def test_maps_the_cpf_and_leaves_enrichment_fields_unset(self) -> None:
        person = _map_person_stub(cpf=_TEST_CPF)

        assert isinstance(person, Person)
        assert person.cpf == _TEST_CPF
        assert person.name is None


class TestMapCompanyStub:
    def test_maps_the_cnpj_and_leaves_enrichment_fields_unset(self) -> None:
        company = _map_company_stub(cnpj=_TEST_CNPJ)

        assert isinstance(company, Company)
        assert company.cnpj == _TEST_CNPJ
        assert company.legal_name is None


class TestMapGraphDiscriminator:
    def test_builds_a_person_stub_and_edge_for_an_11_digit_document(
        self, make_payload: MakePayload
    ) -> None:
        graph = map_graph(
            cpf_or_cnpj=_TEST_CPF,
            payload=make_payload(provider="kipflow", data=_LEGAL_PROCESS_DATA),
        )

        assert any(isinstance(node, Person) for node in graph.nodes)
        assert not any(isinstance(node, Company) for node in graph.nodes)
        assert any(
            isinstance(edge, PersonIsPartyInLegalProcess) for edge in graph.edges
        )

    def test_builds_a_company_stub_and_edge_for_a_14_digit_document(
        self, make_payload: MakePayload
    ) -> None:
        graph = map_graph(
            cpf_or_cnpj=_TEST_CNPJ,
            payload=make_payload(provider="kipflow", data=_LEGAL_PROCESS_DATA),
        )

        assert any(isinstance(node, Company) for node in graph.nodes)
        assert not any(isinstance(node, Person) for node in graph.nodes)
        assert any(
            isinstance(edge, CompanyIsPartyInLegalProcess) for edge in graph.edges
        )

    def test_root_id_is_the_party_not_the_legal_process(
        self, make_payload: MakePayload
    ) -> None:
        graph = map_graph(
            cpf_or_cnpj=_TEST_CPF,
            payload=make_payload(provider="kipflow", data=_LEGAL_PROCESS_DATA),
        )

        legal_process_ids = {
            node.id for node in graph.nodes if isinstance(node, LegalProcess)
        }

        assert graph.root_id not in legal_process_ids

    def test_all_edge_endpoints_are_in_node_set(
        self, make_payload: MakePayload
    ) -> None:
        graph = map_graph(
            cpf_or_cnpj=_TEST_CPF,
            payload=make_payload(provider="kipflow", data=_LEGAL_PROCESS_DATA),
        )

        node_ids = {node.id for node in graph.nodes}

        for edge in graph.edges:
            assert edge.source_id in node_ids
            assert edge.target_id in node_ids

    def test_graph_has_exactly_two_nodes(self, make_payload: MakePayload) -> None:
        graph = map_graph(
            cpf_or_cnpj=_TEST_CPF,
            payload=make_payload(provider="kipflow", data=_LEGAL_PROCESS_DATA),
        )

        assert len(graph.nodes) == 2
