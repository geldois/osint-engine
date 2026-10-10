from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.domain.entities.edges import (
    AddressHostsCompany,
    AddressHostsPerson,
    AddressMentionedInText,
    CnaeClassifiesCompany,
    CompanyHasCnae,
    CompanyHasEmail,
    CompanyHasMember,
    CompanyHasPhone,
    CompanyIsPartyInLegalProcess,
    CompanyLocatedAt,
    CompanyMentionedInText,
    CompanyOwnedByCompany,
    CompanyOwnsCompany,
    CompanyReceivedSanction,
    EmailBelongsToCompany,
    EmailBelongsToPerson,
    LegalProcessHasCompany,
    LegalProcessHasPerson,
    PersonHasEmail,
    PersonHasPhone,
    PersonHasPoliticalExposure,
    PersonIsPartyInLegalProcess,
    PersonMentionedInText,
    PersonOwnsCompany,
    PersonReceivedSanction,
    PersonResideAt,
    PhoneBelongsToCompany,
    PhoneBelongsToPerson,
    PoliticalExposureOfPerson,
    PossiblyMatches,
    SanctionAppliedToCompany,
    SanctionAppliedToPerson,
    TextSourceMentionsAddress,
    TextSourceMentionsCompany,
    TextSourceMentionsPerson,
)
from osint_engine.interface.http.errors.schema_error import UnmappedTypeSchemaError
from osint_engine.interface.http.presenters.revision_presenter import (
    revision_to_schema,
)
from osint_engine.interface.http.schemas.edge_schema import (
    AddressHostsCompanySchema,
    AddressHostsPersonSchema,
    AddressMentionedInTextSchema,
    CnaeClassifiesCompanySchema,
    CompanyHasCnaeSchema,
    CompanyHasEmailSchema,
    CompanyHasMemberSchema,
    CompanyHasPhoneSchema,
    CompanyIsPartyInLegalProcessSchema,
    CompanyLocatedAtSchema,
    CompanyMentionedInTextSchema,
    CompanyOwnedByCompanySchema,
    CompanyOwnsCompanySchema,
    CompanyReceivedSanctionSchema,
    EdgeSchemaUnion,
    EmailBelongsToCompanySchema,
    EmailBelongsToPersonSchema,
    LegalProcessHasCompanySchema,
    LegalProcessHasPersonSchema,
    PersonHasEmailSchema,
    PersonHasPhoneSchema,
    PersonHasPoliticalExposureSchema,
    PersonIsPartyInLegalProcessSchema,
    PersonMentionedInTextSchema,
    PersonOwnsCompanySchema,
    PersonReceivedSanctionSchema,
    PersonResideAtSchema,
    PhoneBelongsToCompanySchema,
    PhoneBelongsToPersonSchema,
    PoliticalExposureOfPersonSchema,
    PossiblyMatchesSchema,
    SanctionAppliedToCompanySchema,
    SanctionAppliedToPersonSchema,
    TextSourceMentionsAddressSchema,
    TextSourceMentionsCompanySchema,
    TextSourceMentionsPersonSchema,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from osint_engine.application.revision.entity_revision import EntityRevision
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


def company_is_party_in_legal_process_to_schema(
    *, edge: CompanyIsPartyInLegalProcess, revision: RevisionSchema
) -> CompanyIsPartyInLegalProcessSchema:
    return CompanyIsPartyInLegalProcessSchema(
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


def person_has_political_exposure_to_schema(
    *, edge: PersonHasPoliticalExposure, revision: RevisionSchema
) -> PersonHasPoliticalExposureSchema:
    return PersonHasPoliticalExposureSchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def person_is_party_in_legal_process_to_schema(
    *, edge: PersonIsPartyInLegalProcess, revision: RevisionSchema
) -> PersonIsPartyInLegalProcessSchema:
    return PersonIsPartyInLegalProcessSchema(
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


def address_hosts_company_to_schema(
    *, edge: AddressHostsCompany, revision: RevisionSchema
) -> AddressHostsCompanySchema:
    return AddressHostsCompanySchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def address_hosts_person_to_schema(
    *, edge: AddressHostsPerson, revision: RevisionSchema
) -> AddressHostsPersonSchema:
    return AddressHostsPersonSchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def cnae_classifies_company_to_schema(
    *, edge: CnaeClassifiesCompany, revision: RevisionSchema
) -> CnaeClassifiesCompanySchema:
    return CnaeClassifiesCompanySchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def company_owned_by_company_to_schema(
    *, edge: CompanyOwnedByCompany, revision: RevisionSchema
) -> CompanyOwnedByCompanySchema:
    return CompanyOwnedByCompanySchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        entry_date=edge.entry_date,
        role=edge.role,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def email_belongs_to_company_to_schema(
    *, edge: EmailBelongsToCompany, revision: RevisionSchema
) -> EmailBelongsToCompanySchema:
    return EmailBelongsToCompanySchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def email_belongs_to_person_to_schema(
    *, edge: EmailBelongsToPerson, revision: RevisionSchema
) -> EmailBelongsToPersonSchema:
    return EmailBelongsToPersonSchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def legal_process_has_company_to_schema(
    *, edge: LegalProcessHasCompany, revision: RevisionSchema
) -> LegalProcessHasCompanySchema:
    return LegalProcessHasCompanySchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def legal_process_has_person_to_schema(
    *, edge: LegalProcessHasPerson, revision: RevisionSchema
) -> LegalProcessHasPersonSchema:
    return LegalProcessHasPersonSchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def phone_belongs_to_company_to_schema(
    *, edge: PhoneBelongsToCompany, revision: RevisionSchema
) -> PhoneBelongsToCompanySchema:
    return PhoneBelongsToCompanySchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def phone_belongs_to_person_to_schema(
    *, edge: PhoneBelongsToPerson, revision: RevisionSchema
) -> PhoneBelongsToPersonSchema:
    return PhoneBelongsToPersonSchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def political_exposure_of_person_to_schema(
    *, edge: PoliticalExposureOfPerson, revision: RevisionSchema
) -> PoliticalExposureOfPersonSchema:
    return PoliticalExposureOfPersonSchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def sanction_applied_to_company_to_schema(
    *, edge: SanctionAppliedToCompany, revision: RevisionSchema
) -> SanctionAppliedToCompanySchema:
    return SanctionAppliedToCompanySchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def sanction_applied_to_person_to_schema(
    *, edge: SanctionAppliedToPerson, revision: RevisionSchema
) -> SanctionAppliedToPersonSchema:
    return SanctionAppliedToPersonSchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def text_source_mentions_address_to_schema(
    *, edge: TextSourceMentionsAddress, revision: RevisionSchema
) -> TextSourceMentionsAddressSchema:
    return TextSourceMentionsAddressSchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        matched_field=edge.matched_field,
        pattern_name=edge.pattern_name.name,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def text_source_mentions_company_to_schema(
    *, edge: TextSourceMentionsCompany, revision: RevisionSchema
) -> TextSourceMentionsCompanySchema:
    return TextSourceMentionsCompanySchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        matched_field=edge.matched_field,
        pattern_name=edge.pattern_name.name,
        source_id=edge.source_id,
        target_id=edge.target_id,
    )


def text_source_mentions_person_to_schema(
    *, edge: TextSourceMentionsPerson, revision: RevisionSchema
) -> TextSourceMentionsPersonSchema:
    return TextSourceMentionsPersonSchema(
        content_id=edge.content_id,
        id=edge.id,
        revision=revision,
        matched_field=edge.matched_field,
        pattern_name=edge.pattern_name.name,
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
    CompanyIsPartyInLegalProcess: company_is_party_in_legal_process_to_schema,
    CompanyOwnsCompany: company_owns_company_to_schema,
    CompanyReceivedSanction: company_received_sanction_to_schema,
    PersonHasEmail: person_has_email_to_schema,
    PersonHasPhone: person_has_phone_to_schema,
    PersonHasPoliticalExposure: person_has_political_exposure_to_schema,
    PersonIsPartyInLegalProcess: person_is_party_in_legal_process_to_schema,
    PersonMentionedInText: person_mentioned_in_text_to_schema,
    PersonOwnsCompany: person_owns_company_to_schema,
    PersonReceivedSanction: person_received_sanction_to_schema,
    PersonResideAt: person_reside_at_to_schema,
    AddressHostsCompany: address_hosts_company_to_schema,
    AddressHostsPerson: address_hosts_person_to_schema,
    CnaeClassifiesCompany: cnae_classifies_company_to_schema,
    CompanyOwnedByCompany: company_owned_by_company_to_schema,
    EmailBelongsToCompany: email_belongs_to_company_to_schema,
    EmailBelongsToPerson: email_belongs_to_person_to_schema,
    LegalProcessHasCompany: legal_process_has_company_to_schema,
    LegalProcessHasPerson: legal_process_has_person_to_schema,
    PhoneBelongsToCompany: phone_belongs_to_company_to_schema,
    PhoneBelongsToPerson: phone_belongs_to_person_to_schema,
    PoliticalExposureOfPerson: political_exposure_of_person_to_schema,
    SanctionAppliedToCompany: sanction_applied_to_company_to_schema,
    SanctionAppliedToPerson: sanction_applied_to_person_to_schema,
    TextSourceMentionsAddress: text_source_mentions_address_to_schema,
    TextSourceMentionsCompany: text_source_mentions_company_to_schema,
    TextSourceMentionsPerson: text_source_mentions_person_to_schema,
    PossiblyMatches: possibly_matches_to_schema,
}


def edge_to_schema(
    edge: Edge[UUID, UUID, UUID], /, *, revision: RevisionSchema
) -> EdgeSchemaUnion:
    try:
        return _EDGE_MAP[type(edge)](edge=edge, revision=revision)
    except KeyError:
        raise UnmappedTypeSchemaError(subject=type(edge)) from None


def edge_history_to_schema(
    revisions: tuple[EntityRevision[Edge[UUID, UUID, UUID]], ...], /
) -> list[EdgeSchemaUnion]:
    return [
        edge_to_schema(revision.entity, revision=revision_to_schema(revision))
        for revision in revisions
    ]
