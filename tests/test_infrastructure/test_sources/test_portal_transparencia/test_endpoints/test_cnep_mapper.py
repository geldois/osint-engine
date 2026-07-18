from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from osint_engine.domain.entities.edges.company_received_sanction import (
    CompanyReceivedSanction,
)
from osint_engine.domain.entities.edges.person_received_sanction import (
    PersonReceivedSanction,
)
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.entities.nodes.sanction import Sanction
from osint_engine.infrastructure.errors.data_source_error import (
    UnexpectedFieldFormatError,
)
from osint_engine.infrastructure.sources.portal_transparencia.endpoints.cnep_mapper import (  # noqa: E501
    _map_company_stub,  # pyright: ignore[reportPrivateUsage]
    _map_person_stub,  # pyright: ignore[reportPrivateUsage]
    _map_sanction,  # pyright: ignore[reportPrivateUsage]
    _parse_fine_amount,  # pyright: ignore[reportPrivateUsage]
    map_graph,
)

if TYPE_CHECKING:
    from tests.test_infrastructure.test_sources.conftest import MakePayload

# TEST DOUBLES


_SANCTION_DATA: dict[str, object] = {
    "dataFimSancao": "2026-01-01",
    "dataInicioSancao": "2024-01-01",
    "dataPublicacaoSancao": "2024-01-15",
    "numeroProcesso": "123/2024",
    "orgaoSancionador": {"nome": "CGU"},
    "tipoSancao": {"descricaoResumida": "Suspensão"},
    "valorMulta": "1.000,50",
}

_COMPANY_SANCIONADO_DATA: dict[str, object] = {
    "cnpjFormatado": "33.754.482/0001-24",
    "nomeFantasiaReceita": "EMPRESA FANTASIA",
    "razaoSocialReceita": "EMPRESA LTDA",
}

_PERSON_SANCIONADO_DATA: dict[str, object] = {
    "cpfFormatado": "128.734.***-**",
    "nome": "TARCIANA PAULA GOMES MEDEIROS",
}


def _cnep_payload_data(*, pessoa: dict[str, object]) -> dict[str, object]:
    return {**_SANCTION_DATA, "pessoa": pessoa}


# TESTS


class TestParseFineAmount:
    def test_parses_pt_br_formatted_decimal(self) -> None:
        assert _parse_fine_amount(
            value="1.000,50", source="portal_transparencia", key="valorMulta"
        ) == Decimal("1000.50")

    def test_raises_unexpected_field_format_error_on_invalid_amount(self) -> None:
        with pytest.raises(UnexpectedFieldFormatError) as exception:
            _parse_fine_amount(
                value="not-a-number", source="portal_transparencia", key="valorMulta"
            )

        assert exception.value.source == "portal_transparencia"
        assert exception.value.key == "valorMulta"
        assert exception.value.raw_value == "not-a-number"


class TestMapSanction:
    def test_maps_field_values_from_payload(self, make_payload: MakePayload) -> None:
        sanction = _map_sanction(
            payload=make_payload(source="portal_transparencia", data=_SANCTION_DATA)
        )

        assert isinstance(sanction, Sanction)
        assert sanction.organ == "CNEP"
        assert sanction.process_number == "123/2024"
        assert sanction.sanction_type == "Suspensão"
        assert sanction.sanctioning_body == "CGU"
        assert sanction.fine_amount == Decimal("1000.50")
        assert sanction.start_date == "2024-01-01"
        assert sanction.end_date == "2026-01-01"
        assert sanction.publication_date == "2024-01-15"

    def test_fine_amount_is_none_when_absent(self, make_payload: MakePayload) -> None:
        data = {
            key: value for key, value in _SANCTION_DATA.items() if key != "valorMulta"
        }

        sanction = _map_sanction(
            payload=make_payload(source="portal_transparencia", data=data)
        )

        assert sanction.fine_amount is None

    def test_raises_when_fine_amount_is_not_a_valid_decimal(
        self, make_payload: MakePayload
    ) -> None:
        data = {**_SANCTION_DATA, "valorMulta": "not-a-number"}

        with pytest.raises(UnexpectedFieldFormatError):
            _map_sanction(
                payload=make_payload(source="portal_transparencia", data=data)
            )


class TestMapCompanyStub:
    def test_maps_field_values_and_leaves_enrichment_fields_unset(
        self, make_payload: MakePayload
    ) -> None:
        company = _map_company_stub(
            payload=make_payload(
                source="portal_transparencia", data=_COMPANY_SANCIONADO_DATA
            )
        )

        assert isinstance(company, Company)
        assert company.cnpj == "33.754.482/0001-24"
        assert company.legal_name == "EMPRESA LTDA"
        assert company.trade_name == "EMPRESA FANTASIA"
        assert company.activity_start_date is None
        assert company.is_headquarters is None
        assert company.share_capital is None


class TestMapPersonStub:
    def test_maps_field_values_and_leaves_age_range_unset(
        self, make_payload: MakePayload
    ) -> None:
        person = _map_person_stub(
            payload=make_payload(
                source="portal_transparencia", data=_PERSON_SANCIONADO_DATA
            )
        )

        assert isinstance(person, Person)
        assert person.cpf == "128.734.***-**"
        assert person.name == "TARCIANA PAULA GOMES MEDEIROS"
        assert person.age_range is None


class TestMapGraphDiscriminator:
    def test_builds_a_company_stub_and_edge_when_sancionado_has_a_cnpj(
        self, make_payload: MakePayload
    ) -> None:
        graph = map_graph(
            payload=make_payload(
                source="portal_transparencia",
                data=_cnep_payload_data(pessoa=_COMPANY_SANCIONADO_DATA),
            )
        )

        assert any(isinstance(node, Company) for node in graph.nodes)
        assert not any(isinstance(node, Person) for node in graph.nodes)
        assert any(isinstance(edge, CompanyReceivedSanction) for edge in graph.edges)

    def test_builds_a_person_stub_and_edge_when_sancionado_has_no_cnpj(
        self, make_payload: MakePayload
    ) -> None:
        graph = map_graph(
            payload=make_payload(
                source="portal_transparencia",
                data=_cnep_payload_data(pessoa=_PERSON_SANCIONADO_DATA),
            )
        )

        assert any(isinstance(node, Person) for node in graph.nodes)
        assert not any(isinstance(node, Company) for node in graph.nodes)
        assert any(isinstance(edge, PersonReceivedSanction) for edge in graph.edges)

    def test_root_id_is_the_sancionado_not_the_sanction(
        self, make_payload: MakePayload
    ) -> None:
        graph = map_graph(
            payload=make_payload(
                source="portal_transparencia",
                data=_cnep_payload_data(pessoa=_COMPANY_SANCIONADO_DATA),
            )
        )

        sanction_ids = {node.id for node in graph.nodes if isinstance(node, Sanction)}

        assert graph.root_id not in sanction_ids

    def test_all_edge_endpoints_are_in_node_set(
        self, make_payload: MakePayload
    ) -> None:
        graph = map_graph(
            payload=make_payload(
                source="portal_transparencia",
                data=_cnep_payload_data(pessoa=_COMPANY_SANCIONADO_DATA),
            )
        )

        node_ids = {node.id for node in graph.nodes}

        for edge in graph.edges:
            assert edge.source_id in node_ids
            assert edge.target_id in node_ids

    def test_graph_has_exactly_two_nodes(self, make_payload: MakePayload) -> None:
        graph = map_graph(
            payload=make_payload(
                source="portal_transparencia",
                data=_cnep_payload_data(pessoa=_PERSON_SANCIONADO_DATA),
            )
        )

        assert len(graph.nodes) == 2
