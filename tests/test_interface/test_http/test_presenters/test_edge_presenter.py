from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import pytest

from osint_engine.domain.entities.edges.company_has_cnae import CompanyHasCnae
from osint_engine.domain.entities.edges.company_has_email import CompanyHasEmail
from osint_engine.domain.entities.edges.company_has_member import CompanyHasMember
from osint_engine.domain.entities.edges.company_has_phone import CompanyHasPhone
from osint_engine.domain.entities.edges.company_located_at import CompanyLocatedAt
from osint_engine.domain.entities.edges.company_received_sanction import (
    CompanyReceivedSanction,
)
from osint_engine.domain.entities.edges.person_has_email import PersonHasEmail
from osint_engine.domain.entities.edges.person_has_phone import PersonHasPhone
from osint_engine.domain.entities.edges.person_owns_company import PersonOwnsCompany
from osint_engine.domain.entities.edges.person_received_sanction import (
    PersonReceivedSanction,
)
from osint_engine.domain.entities.edges.person_reside_at import PersonResideAt
from osint_engine.domain.entities.nodes.address import AddressID
from osint_engine.domain.entities.nodes.cnae import CnaeID
from osint_engine.domain.entities.nodes.company import CompanyID
from osint_engine.domain.entities.nodes.email import EmailID
from osint_engine.domain.entities.nodes.person import PersonID
from osint_engine.domain.entities.nodes.phone import PhoneID
from osint_engine.domain.entities.nodes.sanction import SanctionID
from osint_engine.interface.http.errors.schema_error import UnmappedTypeSchemaError
from osint_engine.interface.http.presenters.edge_presenter import edge_to_schema
from osint_engine.interface.http.schemas.edge_schema import (
    CompanyHasCnaeSchema,
    CompanyHasEmailSchema,
    CompanyHasMemberSchema,
    CompanyHasPhoneSchema,
    CompanyLocatedAtSchema,
    CompanyReceivedSanctionSchema,
    EdgeSchema,
    PersonHasEmailSchema,
    PersonHasPhoneSchema,
    PersonOwnsCompanySchema,
    PersonReceivedSanctionSchema,
    PersonResideAtSchema,
)

if TYPE_CHECKING:
    from osint_engine.domain.entities.bases.edge import Edge
    from tests.conftest import MakeFakeEdge

_address_id = AddressID(uuid4())

_cnae_id = CnaeID(uuid4())
_company_id = CompanyID(uuid4())
_email_id = EmailID(uuid4())
_person_id = PersonID(uuid4())
_phone_id = PhoneID(uuid4())
_sanction_id = SanctionID(uuid4())

_COMPANY_HAS_CNAE = CompanyHasCnae(source_id=_company_id, target_id=_cnae_id)

_COMPANY_HAS_EMAIL = CompanyHasEmail(source_id=_company_id, target_id=_email_id)

_COMPANY_HAS_MEMBER = CompanyHasMember(source_id=_company_id, target_id=_person_id)

_COMPANY_HAS_PHONE = CompanyHasPhone(source_id=_company_id, target_id=_phone_id)

_COMPANY_LOCATED_AT = CompanyLocatedAt(source_id=_company_id, target_id=_address_id)

_COMPANY_RECEIVED_SANCTION = CompanyReceivedSanction(
    source_id=_company_id, target_id=_sanction_id
)

_PERSON_HAS_EMAIL = PersonHasEmail(source_id=_person_id, target_id=_email_id)

_PERSON_HAS_PHONE = PersonHasPhone(source_id=_person_id, target_id=_phone_id)

_PERSON_OWNS_COMPANY = PersonOwnsCompany(
    entry_date="2021-03-15",
    role="SÓCIO-ADMINISTRADOR",
    source_id=_person_id,
    target_id=_company_id,
)

_PERSON_RECEIVED_SANCTION = PersonReceivedSanction(
    source_id=_person_id, target_id=_sanction_id
)

_PERSON_RESIDE_AT = PersonResideAt(source_id=_person_id, target_id=_address_id)


class TestEdgePresenterDispatch:
    @pytest.mark.parametrize(
        ("edge", "expected_schema_class"),
        [
            pytest.param(
                _COMPANY_HAS_CNAE, CompanyHasCnaeSchema, id="company_has_cnae"
            ),
            pytest.param(
                _COMPANY_HAS_EMAIL, CompanyHasEmailSchema, id="company_has_email"
            ),
            pytest.param(
                _COMPANY_HAS_MEMBER, CompanyHasMemberSchema, id="company_has_member"
            ),
            pytest.param(
                _COMPANY_HAS_PHONE, CompanyHasPhoneSchema, id="company_has_phone"
            ),
            pytest.param(
                _COMPANY_LOCATED_AT, CompanyLocatedAtSchema, id="company_located_at"
            ),
            pytest.param(
                _COMPANY_RECEIVED_SANCTION,
                CompanyReceivedSanctionSchema,
                id="company_received_sanction",
            ),
            pytest.param(
                _PERSON_HAS_EMAIL, PersonHasEmailSchema, id="person_has_email"
            ),
            pytest.param(
                _PERSON_HAS_PHONE, PersonHasPhoneSchema, id="person_has_phone"
            ),
            pytest.param(
                _PERSON_OWNS_COMPANY, PersonOwnsCompanySchema, id="person_owns_company"
            ),
            pytest.param(
                _PERSON_RECEIVED_SANCTION,
                PersonReceivedSanctionSchema,
                id="person_received_sanction",
            ),
            pytest.param(
                _PERSON_RESIDE_AT, PersonResideAtSchema, id="person_reside_at"
            ),
        ],
    )
    def test_dispatches_to_correct_schema_type(
        self,
        edge: Edge[UUID, UUID, UUID],
        expected_schema_class: type[EdgeSchema[Edge[UUID, UUID, UUID]]],
    ) -> None:
        assert isinstance(edge_to_schema(edge), expected_schema_class)


class TestEdgePresenterFieldMapping:
    def test_base_edge_fields_are_correctly_mapped(self) -> None:
        result = edge_to_schema(_COMPANY_HAS_CNAE)

        assert isinstance(result, CompanyHasCnaeSchema)

        assert result.id == _COMPANY_HAS_CNAE.id

        assert result.source_id == _COMPANY_HAS_CNAE.source_id

        assert result.target_id == _COMPANY_HAS_CNAE.target_id

    def test_person_owns_company_extra_fields_are_correctly_mapped(self) -> None:
        result = edge_to_schema(_PERSON_OWNS_COMPANY)

        assert isinstance(result, PersonOwnsCompanySchema)

        assert result.id == _PERSON_OWNS_COMPANY.id

        assert result.source_id == _PERSON_OWNS_COMPANY.source_id

        assert result.target_id == _PERSON_OWNS_COMPANY.target_id

        assert result.entry_date == _PERSON_OWNS_COMPANY.entry_date

        assert result.role == _PERSON_OWNS_COMPANY.role


class TestEdgePresenterErrors:
    def test_raises_for_unmapped_edge_type(self, make_fake_edge: MakeFakeEdge) -> None:
        edge = make_fake_edge()

        with pytest.raises(UnmappedTypeSchemaError):
            edge_to_schema(edge)
