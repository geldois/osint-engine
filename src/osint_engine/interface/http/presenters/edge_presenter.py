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
    from uuid import UUID

    from osint_engine.domain.entities.bases.edge import Edge


def edge_to_schema(edge: Edge[UUID], /) -> EdgeSchemaUnion:  # noqa: C901
    schema = EdgeSchemaUnion

    match edge:
        case CompanyHasCnae():
            schema = company_has_cnae_to_schema(edge=edge)
        case CompanyHasEmail():
            schema = company_has_email_to_schema(edge=edge)
        case CompanyHasMember():
            schema = company_has_member_to_schema(edge=edge)
        case CompanyHasPhone():
            schema = company_has_phone_to_schema(edge=edge)
        case CompanyLocatedAt():
            schema = company_located_at_to_schema(edge=edge)
        case CompanyReceivedSanction():
            schema = company_received_sanction_to_schema(edge=edge)
        case PersonHasEmail():
            schema = person_has_email_to_schema(edge=edge)
        case PersonHasPhone():
            schema = person_has_phone_to_schema(edge=edge)
        case PersonOwnsCompany():
            schema = person_owns_company_to_schema(edge=edge)
        case PersonReceivedSanction():
            schema = person_received_sanction_to_schema(edge=edge)
        case PersonResideAt():
            schema = person_reside_at_to_schema(edge=edge)
        case _:
            raise UnmappedTypeSchemaError(subject=type(edge))

    return schema


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
        id=edge.id, source_id=edge.source_id, target_id=edge.target_id
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
