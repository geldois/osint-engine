from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from osint_engine.domain.entities.nodes.address import Address
from osint_engine.domain.entities.nodes.cnae import Cnae
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.email import Email
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.entities.nodes.phone import Phone
from osint_engine.domain.entities.nodes.sanction import Sanction
from osint_engine.domain.entities.nodes.text_source import TextSource
from osint_engine.interface.http.errors.schema_error import UnmappedTypeSchemaError
from osint_engine.interface.http.presenters.node_presenter import (
    node_history_to_schema,
    node_to_schema,
)
from osint_engine.interface.http.schemas.node_schema import (
    AddressSchema,
    CnaeSchema,
    CompanySchema,
    EmailSchema,
    NodeSchema,
    PersonSchema,
    PhoneSchema,
    SanctionSchema,
    TextSourceSchema,
)

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.domain.entities.bases.node import Node
    from osint_engine.interface.http.schemas.revision_schema import RevisionSchema
    from tests.conftest import MakeEntityRevision, MakeFakeNode


_ADDRESS = Address(
    cep="01310-100",
    city="São Paulo",
    complement="Apto 42",
    neighborhood="Bela Vista",
    number="1578",
    state="SP",
    street="Av Paulista",
)

_CNAE = Cnae(code="0101-3/01", description="Cultivo de arroz")

_COMPANY = Company(
    activity_start_date="2020-01-01",
    cnpj="11222333000181",
    is_headquarters=True,
    legal_name="Acme LTDA",
    legal_nature="206-2",
    registration_status="ATIVA",
    registration_status_date="2020-01-01",
    registration_status_reason="",
    share_capital=Decimal("10000.00"),
    size_category="MICRO",
    trade_name="Acme",
)

_EMAIL = Email(address="user@example.com")

_PERSON = Person(
    age_range="31 a 40 anos",
    birthdate="1990-01-01",
    cpf="123.456.789-09",
    name="João Silva",
    registration_date="2010-05-20",
    registration_status="REGULAR",
)

_PHONE = Phone(number="+5511999999999")

_SANCTION = Sanction(
    end_date="2024-12-31",
    fine_amount=Decimal("1000.00"),
    legal_basis=("Lei 8.666/1993, art. 87",),
    organ="CEIS",
    process_number="12345/2024",
    publication_date="2024-01-01",
    publication_link="https://portaldatransparencia.gov.br/sancoes/ceis/12345",
    sanction_type="Suspensão",
    sanctioning_body="CEIS",
    source_id="12345",
    start_date="2024-01-01",
)

_TEXT_SOURCE = TextSource(text="CPF 123.456.789-09 mencionado no documento.")


class TestNodePresenterDispatch:
    @pytest.mark.parametrize(
        ("node", "expected_schema_class"),
        [
            pytest.param(_ADDRESS, AddressSchema, id="address"),
            pytest.param(_CNAE, CnaeSchema, id="cnae"),
            pytest.param(_COMPANY, CompanySchema, id="company"),
            pytest.param(_EMAIL, EmailSchema, id="email"),
            pytest.param(_PERSON, PersonSchema, id="person"),
            pytest.param(_PHONE, PhoneSchema, id="phone"),
            pytest.param(_SANCTION, SanctionSchema, id="sanction"),
            pytest.param(_TEXT_SOURCE, TextSourceSchema, id="text_source"),
        ],
    )
    def test_dispatches_to_correct_schema_type(
        self,
        node: Node[UUID],
        expected_schema_class: type[NodeSchema[Node[UUID]]],
        revision_schema: RevisionSchema,
    ) -> None:
        assert isinstance(
            node_to_schema(node, revision=revision_schema), expected_schema_class
        )


class TestNodePresenterFieldMapping:
    def test_address_fields_are_correctly_mapped(
        self, revision_schema: RevisionSchema
    ) -> None:
        result = node_to_schema(_ADDRESS, revision=revision_schema)

        assert isinstance(result, AddressSchema)

        assert result.id == _ADDRESS.id

        assert result.cep == _ADDRESS.cep

        assert result.city == _ADDRESS.city

        assert result.complement == _ADDRESS.complement

        assert result.neighborhood == _ADDRESS.neighborhood

        assert result.number == _ADDRESS.number

        assert result.state == _ADDRESS.state

        assert result.street == _ADDRESS.street

    def test_company_fields_are_correctly_mapped(
        self, revision_schema: RevisionSchema
    ) -> None:
        result = node_to_schema(_COMPANY, revision=revision_schema)

        assert isinstance(result, CompanySchema)

        assert result.id == _COMPANY.id

        assert result.cnpj == _COMPANY.cnpj

        assert result.is_headquarters == _COMPANY.is_headquarters

        assert result.share_capital == _COMPANY.share_capital

        assert result.legal_name == _COMPANY.legal_name

        assert result.trade_name == _COMPANY.trade_name

        assert result.activity_start_date == _COMPANY.activity_start_date

        assert result.legal_nature == _COMPANY.legal_nature

        assert result.registration_status == _COMPANY.registration_status

        assert result.registration_status_date == _COMPANY.registration_status_date

        assert result.registration_status_reason == _COMPANY.registration_status_reason

        assert result.size_category == _COMPANY.size_category

    def test_person_fields_are_correctly_mapped(
        self, revision_schema: RevisionSchema
    ) -> None:
        result = node_to_schema(_PERSON, revision=revision_schema)

        assert isinstance(result, PersonSchema)

        assert result.id == _PERSON.id

        assert result.age_range == _PERSON.age_range

        assert result.birthdate == _PERSON.birthdate

        assert result.cpf == _PERSON.cpf

        assert result.name == _PERSON.name

        assert result.registration_date == _PERSON.registration_date

        assert result.registration_status == _PERSON.registration_status

    def test_sanction_fields_are_correctly_mapped(
        self, revision_schema: RevisionSchema
    ) -> None:
        result = node_to_schema(_SANCTION, revision=revision_schema)

        assert isinstance(result, SanctionSchema)

        assert result.id == _SANCTION.id

        assert result.end_date == _SANCTION.end_date

        assert result.fine_amount == _SANCTION.fine_amount

        assert result.organ == _SANCTION.organ

        assert result.process_number == _SANCTION.process_number

        assert result.publication_date == _SANCTION.publication_date

        assert result.publication_link == _SANCTION.publication_link

        assert result.legal_basis == _SANCTION.legal_basis

        assert result.sanction_type == _SANCTION.sanction_type

        assert result.sanctioning_body == _SANCTION.sanctioning_body

        assert result.source_id == _SANCTION.source_id

        assert result.start_date == _SANCTION.start_date

    def test_text_provider_fields_are_correctly_mapped(
        self, revision_schema: RevisionSchema
    ) -> None:
        result = node_to_schema(_TEXT_SOURCE, revision=revision_schema)

        assert isinstance(result, TextSourceSchema)

        assert result.id == _TEXT_SOURCE.id

        assert result.text == _TEXT_SOURCE.text


class TestNodePresenterErrors:
    def test_raises_for_unmapped_node_type(
        self, make_fake_node: MakeFakeNode, revision_schema: RevisionSchema
    ) -> None:
        node = make_fake_node()

        with pytest.raises(UnmappedTypeSchemaError) as exception:
            node_to_schema(node, revision=revision_schema)

        assert type(node).__name__ in str(exception.value)


class TestNodeHistoryPresenter:
    def test_maps_every_revision_preserving_order(
        self, make_entity_revision: MakeEntityRevision
    ) -> None:
        first = make_entity_revision(entity=_PERSON)
        second = make_entity_revision(entity=_PERSON)

        result = node_history_to_schema((first, second))

        assert len(result) == 2
        assert all(isinstance(item, PersonSchema) for item in result)

    def test_each_item_carries_its_own_revision(
        self, make_entity_revision: MakeEntityRevision
    ) -> None:
        first = make_entity_revision(entity=_PERSON, provider="text_ingestion")
        second = make_entity_revision(entity=_PERSON, provider="kipflow")

        result = node_history_to_schema((first, second))

        assert result[0].revision.provider == "text_ingestion"
        assert result[1].revision.provider == "kipflow"

    def test_empty_history_maps_to_an_empty_list(self) -> None:
        assert node_history_to_schema(()) == []
