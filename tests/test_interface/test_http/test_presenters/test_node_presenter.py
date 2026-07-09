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
from osint_engine.interface.http.errors.schema_error import UnmappedTypeSchemaError
from osint_engine.interface.http.presenters.node_presenter import node_to_schema
from osint_engine.interface.http.schemas.node_schema import (
    AddressSchema,
    CnaeSchema,
    CompanySchema,
    EmailSchema,
    NodeSchema,
    PersonSchema,
    PhoneSchema,
    SanctionSchema,
)

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.domain.entities.bases.node import Node
    from tests.conftest import MakeFakeNode

# TEST DOUBLES


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

_PERSON = Person(age_range="31 a 40 anos", cpf="123.456.789-09", name="João Silva")

_PHONE = Phone(number="+5511999999999")

_SANCTION = Sanction(organ="CEIS")


# TESTS


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
        ],
    )
    def test_dispatches_to_correct_schema_type(
        self,
        node: Node[UUID],
        expected_schema_class: type[NodeSchema[Node[UUID]]],
    ) -> None:
        assert isinstance(node_to_schema(node), expected_schema_class)


class TestNodePresenterFieldMapping:
    def test_address_fields_are_correctly_mapped(self) -> None:
        result = node_to_schema(_ADDRESS)

        assert isinstance(result, AddressSchema)

        assert result.id == _ADDRESS.id

        assert result.cep == _ADDRESS.cep

        assert result.city == _ADDRESS.city

        assert result.complement == _ADDRESS.complement

        assert result.neighborhood == _ADDRESS.neighborhood

        assert result.number == _ADDRESS.number

        assert result.state == _ADDRESS.state

        assert result.street == _ADDRESS.street

    def test_company_fields_are_correctly_mapped(self) -> None:
        result = node_to_schema(_COMPANY)

        assert isinstance(result, CompanySchema)

        assert result.id == _COMPANY.id

        assert result.cnpj == _COMPANY.cnpj

        assert result.is_headquarters == _COMPANY.is_headquarters

        assert result.share_capital == _COMPANY.share_capital

        assert result.legal_name == _COMPANY.legal_name

        assert result.trade_name == _COMPANY.trade_name


class TestNodePresenterErrors:
    def test_raises_for_unmapped_node_type(self, make_fake_node: MakeFakeNode) -> None:
        node = make_fake_node()

        with pytest.raises(UnmappedTypeSchemaError):
            node_to_schema(node)
