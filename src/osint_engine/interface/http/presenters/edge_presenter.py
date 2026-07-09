from __future__ import annotations

from typing import TYPE_CHECKING

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
from osint_engine.interface.http.errors.schema_error import UnmappedTypeSchemaError
from osint_engine.interface.http.schemas.edge_schema import (
    CompanyHasCnaeSchema,
    CompanyHasEmailSchema,
    CompanyHasMemberSchema,
    CompanyHasPhoneSchema,
    CompanyLocatedAtSchema,
    CompanyReceivedSanctionSchema,
    EdgeSchemaUnion,
    PersonHasEmailSchema,
    PersonHasPhoneSchema,
    PersonOwnsCompanySchema,
    PersonReceivedSanctionSchema,
    PersonResideAtSchema,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from osint_engine.domain.entities.bases.edge import Edge


def company_has_cnae_to_schema(*, edge: CompanyHasCnae) -> CompanyHasCnaeSchema:
    return CompanyHasCnaeSchema(
        id=edge.id, source_id=edge.source_id, target_id=edge.target_id
    )


def company_has_email_to_schema(*, edge: CompanyHasEmail) -> CompanyHasEmailSchema:
    return CompanyHasEmailSchema(
        id=edge.id, source_id=edge.source_id, target_id=edge.target_id
    )


def company_has_member_to_schema(*, edge: CompanyHasMember) -> CompanyHasMemberSchema:
    return CompanyHasMemberSchema(
        id=edge.id, source_id=edge.source_id, target_id=edge.target_id
    )


def company_has_phone_to_schema(*, edge: CompanyHasPhone) -> CompanyHasPhoneSchema:
    return CompanyHasPhoneSchema(
        id=edge.id, source_id=edge.source_id, target_id=edge.target_id
    )


def company_located_at_to_schema(*, edge: CompanyLocatedAt) -> CompanyLocatedAtSchema:
    return CompanyLocatedAtSchema(
        id=edge.id, source_id=edge.source_id, target_id=edge.target_id
    )


def company_received_sanction_to_schema(
    *, edge: CompanyReceivedSanction
) -> CompanyReceivedSanctionSchema:
    return CompanyReceivedSanctionSchema(
        id=edge.id, source_id=edge.source_id, target_id=edge.target_id
    )


def person_has_email_to_schema(*, edge: PersonHasEmail) -> PersonHasEmailSchema:
    return PersonHasEmailSchema(
        id=edge.id, source_id=edge.source_id, target_id=edge.target_id
    )


def person_has_phone_to_schema(*, edge: PersonHasPhone) -> PersonHasPhoneSchema:
    return PersonHasPhoneSchema(
        id=edge.id, source_id=edge.source_id, target_id=edge.target_id
    )


def person_owns_company_to_schema(
    *, edge: PersonOwnsCompany
) -> PersonOwnsCompanySchema:
    return PersonOwnsCompanySchema(
        id=edge.id,
        entry_date=edge.entry_date,
        role=edge.role,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def person_received_sanction_to_schema(
    *, edge: PersonReceivedSanction
) -> PersonReceivedSanctionSchema:
    return PersonReceivedSanctionSchema(
        id=edge.id, source_id=edge.source_id, target_id=edge.target_id
    )


def person_reside_at_to_schema(*, edge: PersonResideAt) -> PersonResideAtSchema:
    return PersonResideAtSchema(
        id=edge.id, source_id=edge.source_id, target_id=edge.target_id
    )


_EDGE_MAP: dict[type, Callable[..., EdgeSchemaUnion]] = {
    CompanyHasCnae: company_has_cnae_to_schema,
    CompanyHasEmail: company_has_email_to_schema,
    CompanyHasMember: company_has_member_to_schema,
    CompanyHasPhone: company_has_phone_to_schema,
    CompanyLocatedAt: company_located_at_to_schema,
    CompanyReceivedSanction: company_received_sanction_to_schema,
    PersonHasEmail: person_has_email_to_schema,
    PersonHasPhone: person_has_phone_to_schema,
    PersonOwnsCompany: person_owns_company_to_schema,
    PersonReceivedSanction: person_received_sanction_to_schema,
    PersonResideAt: person_reside_at_to_schema,
}


def edge_to_schema(edge: Edge[UUID, UUID, UUID], /) -> EdgeSchemaUnion:
    try:
        return _EDGE_MAP[type(edge)](edge=edge)
    except KeyError:
        raise UnmappedTypeSchemaError(subject=type(edge)) from None
