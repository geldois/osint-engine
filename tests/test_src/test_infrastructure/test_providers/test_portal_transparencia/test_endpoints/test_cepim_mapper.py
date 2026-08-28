from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from osint_engine.domain.entities.edges.company_received_sanction import (
    CompanyReceivedSanction,
)
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.sanction import Sanction
from osint_engine.infrastructure.providers.portal_transparencia.endpoints.cepim_mapper import (  # noqa: E501
    _map_company_stub,  # pyright: ignore[reportPrivateUsage]
    _map_sanction,  # pyright: ignore[reportPrivateUsage]
    map_graph,
)

if TYPE_CHECKING:
    from osint_engine.infrastructure.providers.payload import Payload
    from tests.test_src.test_infrastructure.test_providers.conftest import MakePayload

_SANCTION_DATA: dict[str, object] = {
    "dataReferencia": "10/08/2026",
    "id": 4242,
    "motivo": "Prestação de contas rejeitada",
    "orgaoSuperior": {"nome": "Ministério da Cidadania"},
}

_COMPANY_SANCIONADO_DATA: dict[str, object] = {
    "cnpjFormatado": "33.754.482/0001-24",
    "nomeFantasiaReceita": "ONG FANTASIA",
    "razaoSocialReceita": "ONG SEM FINS LUCRATIVOS",
}


def _cepim_payload_data(*, pessoa_juridica: dict[str, object]) -> dict[str, object]:
    return {**_SANCTION_DATA, "pessoaJuridica": pessoa_juridica}


class TestMapSanction:
    def test_maps_field_values_from_payload(self, make_payload: MakePayload) -> None:
        sanction = _map_sanction(
            payload=make_payload(provider="portal_transparencia", data=_SANCTION_DATA)
        )

        assert isinstance(sanction, Sanction)
        assert sanction.organ == "CEPIM"
        assert sanction.source_id == "4242"
        assert sanction.sanction_type == "Prestação de contas rejeitada"
        assert sanction.sanctioning_body == "Ministério da Cidadania"
        assert sanction.publication_date == "10/08/2026"
        assert sanction.process_number is None
        assert sanction.start_date is None
        assert sanction.end_date is None
        assert sanction.fine_amount is None
        assert sanction.legal_basis == ()
        assert sanction.publication_link == ""

    def test_publication_date_is_none_when_absent(
        self, make_payload: MakePayload
    ) -> None:
        data = {
            key: value
            for key, value in _SANCTION_DATA.items()
            if key != "dataReferencia"
        }

        sanction = _map_sanction(
            payload=make_payload(provider="portal_transparencia", data=data)
        )

        assert sanction.publication_date is None


class TestMapCompanyStub:
    def test_maps_field_values_and_leaves_enrichment_fields_unset(
        self, make_payload: MakePayload
    ) -> None:
        company = _map_company_stub(
            payload=make_payload(
                provider="portal_transparencia", data=_COMPANY_SANCIONADO_DATA
            )
        )

        assert isinstance(company, Company)
        assert company.cnpj == "33.754.482/0001-24"
        assert company.legal_name == "ONG SEM FINS LUCRATIVOS"
        assert company.trade_name == "ONG FANTASIA"
        assert company.activity_start_date is None
        assert company.is_headquarters is None
        assert company.share_capital is None


class TestMapGraph:
    def test_builds_a_company_and_a_sanction_with_a_received_sanction_edge(
        self, make_payload: MakePayload
    ) -> None:
        graph = map_graph(
            payload=make_payload(
                provider="portal_transparencia",
                data=_cepim_payload_data(pessoa_juridica=_COMPANY_SANCIONADO_DATA),
            )
        )

        assert any(isinstance(node, Company) for node in graph.nodes)
        assert any(isinstance(node, Sanction) for node in graph.nodes)
        assert any(isinstance(edge, CompanyReceivedSanction) for edge in graph.edges)

    def test_root_id_is_the_company_not_the_sanction(
        self, make_payload: MakePayload
    ) -> None:
        graph = map_graph(
            payload=make_payload(
                provider="portal_transparencia",
                data=_cepim_payload_data(pessoa_juridica=_COMPANY_SANCIONADO_DATA),
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
                data=_cepim_payload_data(pessoa_juridica=_COMPANY_SANCIONADO_DATA),
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
                data=_cepim_payload_data(pessoa_juridica=_COMPANY_SANCIONADO_DATA),
            )
        )

        assert len(graph.nodes) == 2


@pytest.mark.real_api_snapshot
class TestMapGraphWithRealAPISnapshot:
    def test_does_not_raise_with_real_api_snapshot(
        self, portal_transparencia_cepim_valid_payload: Payload
    ) -> None:
        map_graph(payload=portal_transparencia_cepim_valid_payload)
