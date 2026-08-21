from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.domain.entities.edges.address_mentioned_in_text import (
    AddressMentionedInText,
)
from osint_engine.domain.entities.edges.company_has_cnae import CompanyHasCnae
from osint_engine.domain.entities.edges.company_has_email import CompanyHasEmail
from osint_engine.domain.entities.edges.company_has_member import CompanyHasMember
from osint_engine.domain.entities.edges.company_has_phone import CompanyHasPhone
from osint_engine.domain.entities.edges.company_located_at import CompanyLocatedAt
from osint_engine.domain.entities.edges.company_mentioned_in_text import (
    CompanyMentionedInText,
)
from osint_engine.domain.entities.edges.company_owns_company import CompanyOwnsCompany
from osint_engine.domain.entities.edges.company_received_sanction import (
    CompanyReceivedSanction,
)
from osint_engine.domain.entities.edges.person_has_email import PersonHasEmail
from osint_engine.domain.entities.edges.person_has_phone import PersonHasPhone
from osint_engine.domain.entities.edges.person_mentioned_in_text import (
    PersonMentionedInText,
)
from osint_engine.domain.entities.edges.person_owns_company import PersonOwnsCompany
from osint_engine.domain.entities.edges.person_received_sanction import (
    PersonReceivedSanction,
)
from osint_engine.domain.entities.edges.person_reside_at import PersonResideAt
from osint_engine.domain.entities.edges.possibly_matches import PossiblyMatches
from osint_engine.interface.http.errors.schema_error import UnmappedTypeSchemaError
from osint_engine.interface.http.schemas.edge_schema import (
    AddressMentionedInTextSchema,
    CompanyHasCnaeSchema,
    CompanyHasEmailSchema,
    CompanyHasMemberSchema,
    CompanyHasPhoneSchema,
    CompanyLocatedAtSchema,
    CompanyMentionedInTextSchema,
    CompanyOwnsCompanySchema,
    CompanyReceivedSanctionSchema,
    EdgeSchemaUnion,
    PersonHasEmailSchema,
    PersonHasPhoneSchema,
    PersonMentionedInTextSchema,
    PersonOwnsCompanySchema,
    PersonReceivedSanctionSchema,
    PersonResideAtSchema,
    PossiblyMatchesSchema,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from osint_engine.domain.entities.bases.edge import Edge
    from osint_engine.interface.http.schemas.revision_schema import RevisionSchema


def address_mentioned_in_text_to_schema(
    *, edge: AddressMentionedInText, revision: RevisionSchema
) -> AddressMentionedInTextSchema:
    return AddressMentionedInTextSchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        matched_field=edge.matched_field,
        pattern_name=edge.pattern_name.name,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def company_has_cnae_to_schema(
    *, edge: CompanyHasCnae, revision: RevisionSchema
) -> CompanyHasCnaeSchema:
    return CompanyHasCnaeSchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def company_has_email_to_schema(
    *, edge: CompanyHasEmail, revision: RevisionSchema
) -> CompanyHasEmailSchema:
    return CompanyHasEmailSchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def company_has_member_to_schema(
    *, edge: CompanyHasMember, revision: RevisionSchema
) -> CompanyHasMemberSchema:
    return CompanyHasMemberSchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def company_has_phone_to_schema(
    *, edge: CompanyHasPhone, revision: RevisionSchema
) -> CompanyHasPhoneSchema:
    return CompanyHasPhoneSchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def company_located_at_to_schema(
    *, edge: CompanyLocatedAt, revision: RevisionSchema
) -> CompanyLocatedAtSchema:
    return CompanyLocatedAtSchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def company_mentioned_in_text_to_schema(
    *, edge: CompanyMentionedInText, revision: RevisionSchema
) -> CompanyMentionedInTextSchema:
    return CompanyMentionedInTextSchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        matched_field=edge.matched_field,
        pattern_name=edge.pattern_name.name,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def company_owns_company_to_schema(
    *, edge: CompanyOwnsCompany, revision: RevisionSchema
) -> CompanyOwnsCompanySchema:
    return CompanyOwnsCompanySchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        entry_date=edge.entry_date,
        role=edge.role,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def company_received_sanction_to_schema(
    *, edge: CompanyReceivedSanction, revision: RevisionSchema
) -> CompanyReceivedSanctionSchema:
    return CompanyReceivedSanctionSchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def person_has_email_to_schema(
    *, edge: PersonHasEmail, revision: RevisionSchema
) -> PersonHasEmailSchema:
    return PersonHasEmailSchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def person_has_phone_to_schema(
    *, edge: PersonHasPhone, revision: RevisionSchema
) -> PersonHasPhoneSchema:
    return PersonHasPhoneSchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def person_mentioned_in_text_to_schema(
    *, edge: PersonMentionedInText, revision: RevisionSchema
) -> PersonMentionedInTextSchema:
    return PersonMentionedInTextSchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        matched_field=edge.matched_field,
        pattern_name=edge.pattern_name.name,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def person_owns_company_to_schema(
    *, edge: PersonOwnsCompany, revision: RevisionSchema
) -> PersonOwnsCompanySchema:
    return PersonOwnsCompanySchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        entry_date=edge.entry_date,
        role=edge.role,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def person_received_sanction_to_schema(
    *, edge: PersonReceivedSanction, revision: RevisionSchema
) -> PersonReceivedSanctionSchema:
    return PersonReceivedSanctionSchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def person_reside_at_to_schema(
    *, edge: PersonResideAt, revision: RevisionSchema
) -> PersonResideAtSchema:
    return PersonResideAtSchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def possibly_matches_to_schema(
    *, edge: PossiblyMatches[UUID], revision: RevisionSchema
) -> PossiblyMatchesSchema:
    return PossiblyMatchesSchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        confidence=edge.confidence,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


_EDGE_MAP: dict[type[Edge[UUID, UUID, UUID]], Callable[..., EdgeSchemaUnion]] = {
    AddressMentionedInText: address_mentioned_in_text_to_schema,
    CompanyHasCnae: company_has_cnae_to_schema,
    CompanyHasEmail: company_has_email_to_schema,
    CompanyHasMember: company_has_member_to_schema,
    CompanyHasPhone: company_has_phone_to_schema,
    CompanyLocatedAt: company_located_at_to_schema,
    CompanyMentionedInText: company_mentioned_in_text_to_schema,
    CompanyOwnsCompany: company_owns_company_to_schema,
    CompanyReceivedSanction: company_received_sanction_to_schema,
    PersonHasEmail: person_has_email_to_schema,
    PersonHasPhone: person_has_phone_to_schema,
    PersonMentionedInText: person_mentioned_in_text_to_schema,
    PersonOwnsCompany: person_owns_company_to_schema,
    PersonReceivedSanction: person_received_sanction_to_schema,
    PersonResideAt: person_reside_at_to_schema,
    PossiblyMatches: possibly_matches_to_schema,
}


def edge_to_schema(
    edge: Edge[UUID, UUID, UUID], /, *, revision: RevisionSchema
) -> EdgeSchemaUnion:
    try:
        return _EDGE_MAP[type(edge)](edge=edge, revision=revision)
    except KeyError:
        raise UnmappedTypeSchemaError(subject=type(edge)) from None
