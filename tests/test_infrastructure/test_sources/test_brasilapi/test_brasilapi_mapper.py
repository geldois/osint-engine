from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from osint_engine.domain.entities.edges.company_has_email import CompanyHasEmail
from osint_engine.domain.entities.nodes.address import Address
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.email import Email
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.infrastructure.errors.data_source_error import UnexpectedPayloadError
from osint_engine.infrastructure.sources.brasilapi.brasilapi_mapper import (
    _map_address,  # pyright: ignore[reportPrivateUsage]
    _map_cnaes,  # pyright: ignore[reportPrivateUsage]
    _map_company,  # pyright: ignore[reportPrivateUsage]
    _map_email,  # pyright: ignore[reportPrivateUsage]
    _map_persons_and_ownerships,  # pyright: ignore[reportPrivateUsage]
    _map_phones,  # pyright: ignore[reportPrivateUsage]
    map_graph,
)
from tests.test_infrastructure.test_sources.test_brasilapi._data import (
    ADDRESS_DATA,
    CNAE_DATA,
    COMPANY_DATA,
    COMPLETE_PAYLOAD_DATA,
    PARTNER_PERSON,
)

if TYPE_CHECKING:
    from osint_engine.infrastructure.sources.payload import Payload
    from tests.conftest import MakePayload


# TEST DOUBLES

_COMPANY_ID = Company(
    activity_start_date="1966-08-01",
    cnpj="00000000000191",
    is_headquarters=True,
    legal_name="BANCO DO BRASIL SA",
    legal_nature="Sociedade de Economia Mista",
    registration_status="ATIVA",
    registration_status_date="2005-11-03",
    registration_status_reason="SEM MOTIVO",
    share_capital=Decimal("120000000000"),
    size_category="DEMAIS",
    trade_name="DIRECAO GERAL",
).id


# TESTS


class TestMapAddress:
    def test_maps_field_values_from_payload(self, make_payload: MakePayload) -> None:
        address = _map_address(
            payload=make_payload(source="brasilapi", data=ADDRESS_DATA)
        )

        assert isinstance(address, Address)

        assert address.cep == "70040912"

        assert address.city == "BRASILIA"

        assert address.street == "SAUN QUADRA 5 BLOCO B"

        assert address.complement == "ANDAR T I"

        assert address.neighborhood == "ASA NORTE"

        assert address.number == "SN"

        assert address.state == "DF"

    def test_raises_when_required_field_is_missing(
        self, make_payload: MakePayload
    ) -> None:
        data = {k: v for k, v in ADDRESS_DATA.items() if k != "cep"}

        with pytest.raises(UnexpectedPayloadError):
            _map_address(payload=make_payload(source="brasilapi", data=data))


class TestMapCnaes:
    def test_primary_cnae_code_is_int_converted_to_string(
        self, make_payload: MakePayload
    ) -> None:
        cnaes = _map_cnaes(payload=make_payload(source="brasilapi", data=CNAE_DATA))

        codes = {cnae.code for cnae in cnaes}

        assert "6422100" in codes

    def test_primary_cnae_description_is_mapped(
        self, make_payload: MakePayload
    ) -> None:
        cnaes = _map_cnaes(payload=make_payload(source="brasilapi", data=CNAE_DATA))

        primary = next(c for c in cnaes if c.code == "6422100")

        assert primary.description == "Bancos múltiplos, com carteira comercial"

    def test_includes_secondary_cnaes(self, make_payload: MakePayload) -> None:
        cnaes = _map_cnaes(payload=make_payload(source="brasilapi", data=CNAE_DATA))

        codes = {cnae.code for cnae in cnaes}

        assert "6499999" in codes

    def test_count_is_primary_plus_secondary(self, make_payload: MakePayload) -> None:
        cnaes = _map_cnaes(payload=make_payload(source="brasilapi", data=CNAE_DATA))

        assert len(cnaes) == 2

    def test_returns_only_primary_when_secondary_list_is_empty(
        self, make_payload: MakePayload
    ) -> None:
        data: dict[str, object] = {**CNAE_DATA, "cnaes_secundarios": []}

        cnaes = _map_cnaes(payload=make_payload(source="brasilapi", data=data))

        assert len(cnaes) == 1

        assert next(iter(cnaes)).code == "6422100"

    def test_skips_falsy_entries_in_secondary_cnaes(
        self, make_payload: MakePayload
    ) -> None:
        data = {
            **CNAE_DATA,
            "cnaes_secundarios": [{}, {"codigo": 6499999, "descricao": "Other"}],
        }

        cnaes = _map_cnaes(payload=make_payload(source="brasilapi", data=data))

        assert len(cnaes) == 2


class TestMapCompany:
    def test_maps_field_values_from_payload(self, make_payload: MakePayload) -> None:
        company = _map_company(
            payload=make_payload(source="brasilapi", data=COMPANY_DATA)
        )

        assert isinstance(company, Company)

        assert company.activity_start_date == "1966-08-01"

        assert company.cnpj == "00000000000191"

        assert company.legal_name == "BANCO DO BRASIL SA"

        assert company.legal_nature == "Sociedade de Economia Mista"

        assert company.registration_status == "ATIVA"

        assert company.registration_status_date == "2005-11-03"

        assert company.registration_status_reason == "SEM MOTIVO"

        assert company.size_category == "DEMAIS"

        assert company.trade_name == "DIRECAO GERAL"

    def test_is_headquarters_true_when_indicator_is_1(
        self, make_payload: MakePayload
    ) -> None:
        data = {**COMPANY_DATA, "identificador_matriz_filial": 1}

        company = _map_company(payload=make_payload(source="brasilapi", data=data))

        assert company.is_headquarters is True

    def test_is_headquarters_false_when_indicator_is_not_1(
        self, make_payload: MakePayload
    ) -> None:
        data = {**COMPANY_DATA, "identificador_matriz_filial": 2}

        company = _map_company(payload=make_payload(source="brasilapi", data=data))

        assert company.is_headquarters is False

    def test_share_capital_as_int_converts_to_decimal(
        self, make_payload: MakePayload
    ) -> None:
        data = {**COMPANY_DATA, "capital_social": 120000000000}

        company = _map_company(payload=make_payload(source="brasilapi", data=data))

        assert company.share_capital == Decimal("120000000000")

    def test_share_capital_as_float_converts_to_decimal(
        self, make_payload: MakePayload
    ) -> None:
        data = {**COMPANY_DATA, "capital_social": 1.5}

        company = _map_company(payload=make_payload(source="brasilapi", data=data))

        assert company.share_capital == Decimal("1.5")


class TestMapEmail:
    def test_returns_none_when_key_is_absent(self, make_payload: MakePayload) -> None:
        result = _map_email(payload=make_payload(source="brasilapi", data={}))

        assert result is None

    def test_returns_none_when_value_is_null(self, make_payload: MakePayload) -> None:
        result = _map_email(
            payload=make_payload(source="brasilapi", data={"email": None})
        )

        assert result is None

    def test_returns_email_when_address_is_present(
        self, make_payload: MakePayload
    ) -> None:
        result = _map_email(
            payload=make_payload(
                source="brasilapi", data={"email": "contato@bb.com.br"}
            )
        )

        assert isinstance(result, Email)

        assert result.address == "contato@bb.com.br"


class TestMapPhones:
    def test_returns_both_phones_when_both_present(
        self, make_payload: MakePayload
    ) -> None:
        data: dict[str, object] = {
            "ddd_telefone_1": "6134939002",
            "ddd_telefone_2": "6134931040",
        }

        phones = _map_phones(payload=make_payload(source="brasilapi", data=data))

        assert len(phones) == 2

        numbers = {p.number for p in phones}

        assert "6134939002" in numbers

        assert "6134931040" in numbers

    def test_filters_empty_second_phone(self, make_payload: MakePayload) -> None:
        data: dict[str, object] = {"ddd_telefone_1": "6134939002", "ddd_telefone_2": ""}

        phones = _map_phones(payload=make_payload(source="brasilapi", data=data))

        assert len(phones) == 1

        assert next(iter(phones)).number == "6134939002"

    def test_returns_only_second_phone_when_first_is_absent(
        self, make_payload: MakePayload
    ) -> None:
        data: dict[str, object] = {"ddd_telefone_2": "6134931040"}

        phones = _map_phones(payload=make_payload(source="brasilapi", data=data))

        assert len(phones) == 1

        assert next(iter(phones)).number == "6134931040"

    def test_returns_empty_set_when_no_phones_present(
        self, make_payload: MakePayload
    ) -> None:
        phones = _map_phones(payload=make_payload(source="brasilapi", data={}))

        assert phones == set()


class TestMapPersonsAndOwnerships:
    def test_maps_person_fields(self, make_payload: MakePayload) -> None:
        persons, _ = _map_persons_and_ownerships(
            payload=make_payload(source="brasilapi", data={"qsa": [PARTNER_PERSON]}),
            company_id=_COMPANY_ID,
        )

        person = next(iter(persons))

        assert person.name == "TARCIANA PAULA GOMES MEDEIROS"

        assert person.cpf == "***128734**"

        assert person.age_range == "Entre 41 a 50 anos"

    def test_maps_ownership_fields(self, make_payload: MakePayload) -> None:
        _, ownerships = _map_persons_and_ownerships(
            payload=make_payload(source="brasilapi", data={"qsa": [PARTNER_PERSON]}),
            company_id=_COMPANY_ID,
        )

        ownership = next(iter(ownerships))

        assert ownership.entry_date == "2023-01-26"

        assert ownership.role == "Presidente"

        assert ownership.target_id == _COMPANY_ID

    def test_ownership_source_id_matches_person_id(
        self, make_payload: MakePayload
    ) -> None:
        persons, ownerships = _map_persons_and_ownerships(
            payload=make_payload(source="brasilapi", data={"qsa": [PARTNER_PERSON]}),
            company_id=_COMPANY_ID,
        )

        person = next(iter(persons))
        ownership = next(iter(ownerships))

        assert ownership.source_id == person.id

    def test_skips_partner_with_non_person_identifier(
        self, make_payload: MakePayload
    ) -> None:
        legal_entity: dict[str, object] = {
            **PARTNER_PERSON,
            "identificador_de_socio": 3,
        }

        persons, ownerships = _map_persons_and_ownerships(
            payload=make_payload(source="brasilapi", data={"qsa": [legal_entity]}),
            company_id=_COMPANY_ID,
        )

        assert persons == set()

        assert ownerships == set()

    def test_skips_empty_partner_dict(self, make_payload: MakePayload) -> None:
        persons, ownerships = _map_persons_and_ownerships(
            payload=make_payload(source="brasilapi", data={"qsa": [{}]}),
            company_id=_COMPANY_ID,
        )

        assert persons == set()

        assert ownerships == set()

    def test_returns_empty_sets_when_qsa_is_empty(
        self, make_payload: MakePayload
    ) -> None:
        persons, ownerships = _map_persons_and_ownerships(
            payload=make_payload(source="brasilapi", data={"qsa": []}),
            company_id=_COMPANY_ID,
        )

        assert persons == set()

        assert ownerships == set()


class TestMapGraph:
    def test_root_id_is_company_node(self, make_payload: MakePayload) -> None:
        graph = map_graph(
            payload=make_payload(source="brasilapi", data=COMPLETE_PAYLOAD_DATA)
        )

        company_ids = {n.id for n in graph.nodes if isinstance(n, Company)}

        assert graph.root_id in company_ids

    def test_address_node_is_present(self, make_payload: MakePayload) -> None:
        graph = map_graph(
            payload=make_payload(source="brasilapi", data=COMPLETE_PAYLOAD_DATA)
        )

        assert any(isinstance(n, Address) for n in graph.nodes)

    def test_email_node_present_when_payload_has_email(
        self, make_payload: MakePayload
    ) -> None:
        graph = map_graph(
            payload=make_payload(source="brasilapi", data=COMPLETE_PAYLOAD_DATA)
        )

        assert any(isinstance(n, Email) for n in graph.nodes)

    def test_no_email_node_when_payload_has_no_email(
        self, make_payload: MakePayload
    ) -> None:
        data = {k: v for k, v in COMPLETE_PAYLOAD_DATA.items() if k != "email"}

        graph = map_graph(payload=make_payload(source="brasilapi", data=data))

        assert not any(isinstance(n, Email) for n in graph.nodes)

    def test_email_edge_present_when_payload_has_email(
        self, make_payload: MakePayload
    ) -> None:
        graph = map_graph(
            payload=make_payload(source="brasilapi", data=COMPLETE_PAYLOAD_DATA)
        )

        assert any(isinstance(e, CompanyHasEmail) for e in graph.edges)

    def test_no_email_edge_when_payload_has_no_email(
        self, make_payload: MakePayload
    ) -> None:
        data = {k: v for k, v in COMPLETE_PAYLOAD_DATA.items() if k != "email"}

        graph = map_graph(payload=make_payload(source="brasilapi", data=data))

        assert not any(isinstance(e, CompanyHasEmail) for e in graph.edges)

    def test_all_edge_endpoints_are_in_node_set(
        self, make_payload: MakePayload
    ) -> None:
        graph = map_graph(
            payload=make_payload(source="brasilapi", data=COMPLETE_PAYLOAD_DATA)
        )

        node_ids = {n.id for n in graph.nodes}

        for edge in graph.edges:
            assert edge.source_id in node_ids, (
                f"edge source {edge.source_id} not in nodes"
            )

            assert edge.target_id in node_ids, (
                f"edge target {edge.target_id} not in nodes"
            )

    def test_person_node_count_matches_qsa_person_entries(
        self, make_payload: MakePayload
    ) -> None:
        graph = map_graph(
            payload=make_payload(source="brasilapi", data=COMPLETE_PAYLOAD_DATA)
        )

        person_nodes = {n for n in graph.nodes if isinstance(n, Person)}

        assert len(person_nodes) == 1


class TestMapGraphWithRealAPISnapshot:
    def test_does_not_raise_with_real_api_snapshot(
        self, brasilapi_cnpj_v1_valid_payload: Payload
    ) -> None:
        map_graph(payload=brasilapi_cnpj_v1_valid_payload)
