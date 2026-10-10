from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal  # noqa: TC003
from inspect import isabstract
from typing import Annotated, ClassVar, Literal, get_origin, override
from uuid import UUID

from pydantic import BaseModel, Field

from osint_engine.domain.entities.bases.edge import Edge
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
from osint_engine.interface.http.errors.schema_error import (
    DuplicateSchemaRegistrationError,
    MissingDiscriminatorFieldError,
    UnmappedTypeSchemaError,
)
from osint_engine.interface.http.schemas.revision_schema import (  # noqa: TC001
    RevisionSchema,
)


class EdgeSchema[EdgeType_co: Edge[UUID, UUID, UUID]](ABC, BaseModel):
    content_id: UUID
    id: UUID
    revision: RevisionSchema
    source_id: UUID
    target_id: UUID

    @classmethod
    @override
    def __pydantic_init_subclass__(cls, **kwargs: object) -> None:
        super().__pydantic_init_subclass__(**kwargs)

        if isabstract(cls):
            return

        type_ = cls.model_fields.get("type")

        if type_ is None or get_origin(type_.annotation) is not Literal:
            raise MissingDiscriminatorFieldError(subject=cls)

    @classmethod
    @abstractmethod
    def domain(cls) -> type[EdgeType_co]: ...


class AddressMentionedInTextSchema(EdgeSchema[AddressMentionedInText]):
    type: Literal["address_mentioned_in_text"] = "address_mentioned_in_text"

    matched_field: str
    pattern_name: str

    @classmethod
    @override
    def domain(cls) -> type[AddressMentionedInText]:
        return AddressMentionedInText


class CompanyHasCnaeSchema(EdgeSchema[CompanyHasCnae]):
    type: Literal["company_has_cnae"] = "company_has_cnae"

    @classmethod
    @override
    def domain(cls) -> type[CompanyHasCnae]:
        return CompanyHasCnae


class CompanyHasEmailSchema(EdgeSchema[CompanyHasEmail]):
    type: Literal["company_has_email"] = "company_has_email"

    @classmethod
    @override
    def domain(cls) -> type[CompanyHasEmail]:
        return CompanyHasEmail


class CompanyHasMemberSchema(EdgeSchema[CompanyHasMember]):
    type: Literal["company_has_member"] = "company_has_member"

    @classmethod
    @override
    def domain(cls) -> type[CompanyHasMember]:
        return CompanyHasMember


class CompanyHasPhoneSchema(EdgeSchema[CompanyHasPhone]):
    type: Literal["company_has_phone"] = "company_has_phone"

    @classmethod
    @override
    def domain(cls) -> type[CompanyHasPhone]:
        return CompanyHasPhone


class CompanyLocatedAtSchema(EdgeSchema[CompanyLocatedAt]):
    type: Literal["company_located_at"] = "company_located_at"

    @classmethod
    @override
    def domain(cls) -> type[CompanyLocatedAt]:
        return CompanyLocatedAt


class CompanyMentionedInTextSchema(EdgeSchema[CompanyMentionedInText]):
    type: Literal["company_mentioned_in_text"] = "company_mentioned_in_text"

    matched_field: str
    pattern_name: str

    @classmethod
    @override
    def domain(cls) -> type[CompanyMentionedInText]:
        return CompanyMentionedInText


class CompanyOwnsCompanySchema(EdgeSchema[CompanyOwnsCompany]):
    type: Literal["company_owns_company"] = "company_owns_company"

    entry_date: str
    role: str

    @classmethod
    @override
    def domain(cls) -> type[CompanyOwnsCompany]:
        return CompanyOwnsCompany


class CompanyReceivedSanctionSchema(EdgeSchema[CompanyReceivedSanction]):
    type: Literal["company_received_sanction"] = "company_received_sanction"

    @classmethod
    @override
    def domain(cls) -> type[CompanyReceivedSanction]:
        return CompanyReceivedSanction


class CompanyIsPartyInLegalProcessSchema(EdgeSchema[CompanyIsPartyInLegalProcess]):
    type: Literal["company_is_party_in_legal_process"] = (
        "company_is_party_in_legal_process"
    )

    @classmethod
    @override
    def domain(cls) -> type[CompanyIsPartyInLegalProcess]:
        return CompanyIsPartyInLegalProcess


class PersonHasEmailSchema(EdgeSchema[PersonHasEmail]):
    type: Literal["person_has_email"] = "person_has_email"

    @classmethod
    @override
    def domain(cls) -> type[PersonHasEmail]:
        return PersonHasEmail


class PersonHasPhoneSchema(EdgeSchema[PersonHasPhone]):
    type: Literal["person_has_phone"] = "person_has_phone"

    @classmethod
    @override
    def domain(cls) -> type[PersonHasPhone]:
        return PersonHasPhone


class PersonMentionedInTextSchema(EdgeSchema[PersonMentionedInText]):
    type: Literal["person_mentioned_in_text"] = "person_mentioned_in_text"

    matched_field: str
    pattern_name: str

    @classmethod
    @override
    def domain(cls) -> type[PersonMentionedInText]:
        return PersonMentionedInText


class PersonHasPoliticalExposureSchema(EdgeSchema[PersonHasPoliticalExposure]):
    type: Literal["person_has_political_exposure"] = "person_has_political_exposure"

    @classmethod
    @override
    def domain(cls) -> type[PersonHasPoliticalExposure]:
        return PersonHasPoliticalExposure


class PersonIsPartyInLegalProcessSchema(EdgeSchema[PersonIsPartyInLegalProcess]):
    type: Literal["person_is_party_in_legal_process"] = (
        "person_is_party_in_legal_process"
    )

    @classmethod
    @override
    def domain(cls) -> type[PersonIsPartyInLegalProcess]:
        return PersonIsPartyInLegalProcess


class PersonOwnsCompanySchema(EdgeSchema[PersonOwnsCompany]):
    type: Literal["person_owns_company"] = "person_owns_company"

    entry_date: str
    role: str

    @classmethod
    @override
    def domain(cls) -> type[PersonOwnsCompany]:
        return PersonOwnsCompany


class PersonReceivedSanctionSchema(EdgeSchema[PersonReceivedSanction]):
    type: Literal["person_received_sanction"] = "person_received_sanction"

    @classmethod
    @override
    def domain(cls) -> type[PersonReceivedSanction]:
        return PersonReceivedSanction


class PersonResideAtSchema(EdgeSchema[PersonResideAt]):
    type: Literal["person_reside_at"] = "person_reside_at"

    @classmethod
    @override
    def domain(cls) -> type[PersonResideAt]:
        return PersonResideAt


class AddressHostsCompanySchema(EdgeSchema[AddressHostsCompany]):
    type: Literal["address_hosts_company"] = "address_hosts_company"

    @classmethod
    @override
    def domain(cls) -> type[AddressHostsCompany]:
        return AddressHostsCompany


class AddressHostsPersonSchema(EdgeSchema[AddressHostsPerson]):
    type: Literal["address_hosts_person"] = "address_hosts_person"

    @classmethod
    @override
    def domain(cls) -> type[AddressHostsPerson]:
        return AddressHostsPerson


class CnaeClassifiesCompanySchema(EdgeSchema[CnaeClassifiesCompany]):
    type: Literal["cnae_classifies_company"] = "cnae_classifies_company"

    @classmethod
    @override
    def domain(cls) -> type[CnaeClassifiesCompany]:
        return CnaeClassifiesCompany


class CompanyOwnedByCompanySchema(EdgeSchema[CompanyOwnedByCompany]):
    type: Literal["company_owned_by_company"] = "company_owned_by_company"

    entry_date: str
    role: str

    @classmethod
    @override
    def domain(cls) -> type[CompanyOwnedByCompany]:
        return CompanyOwnedByCompany


class EmailBelongsToCompanySchema(EdgeSchema[EmailBelongsToCompany]):
    type: Literal["email_belongs_to_company"] = "email_belongs_to_company"

    @classmethod
    @override
    def domain(cls) -> type[EmailBelongsToCompany]:
        return EmailBelongsToCompany


class EmailBelongsToPersonSchema(EdgeSchema[EmailBelongsToPerson]):
    type: Literal["email_belongs_to_person"] = "email_belongs_to_person"

    @classmethod
    @override
    def domain(cls) -> type[EmailBelongsToPerson]:
        return EmailBelongsToPerson


class LegalProcessHasCompanySchema(EdgeSchema[LegalProcessHasCompany]):
    type: Literal["legal_process_has_company"] = "legal_process_has_company"

    @classmethod
    @override
    def domain(cls) -> type[LegalProcessHasCompany]:
        return LegalProcessHasCompany


class LegalProcessHasPersonSchema(EdgeSchema[LegalProcessHasPerson]):
    type: Literal["legal_process_has_person"] = "legal_process_has_person"

    @classmethod
    @override
    def domain(cls) -> type[LegalProcessHasPerson]:
        return LegalProcessHasPerson


class PhoneBelongsToCompanySchema(EdgeSchema[PhoneBelongsToCompany]):
    type: Literal["phone_belongs_to_company"] = "phone_belongs_to_company"

    @classmethod
    @override
    def domain(cls) -> type[PhoneBelongsToCompany]:
        return PhoneBelongsToCompany


class PhoneBelongsToPersonSchema(EdgeSchema[PhoneBelongsToPerson]):
    type: Literal["phone_belongs_to_person"] = "phone_belongs_to_person"

    @classmethod
    @override
    def domain(cls) -> type[PhoneBelongsToPerson]:
        return PhoneBelongsToPerson


class PoliticalExposureOfPersonSchema(EdgeSchema[PoliticalExposureOfPerson]):
    type: Literal["political_exposure_of_person"] = "political_exposure_of_person"

    @classmethod
    @override
    def domain(cls) -> type[PoliticalExposureOfPerson]:
        return PoliticalExposureOfPerson


class SanctionAppliedToCompanySchema(EdgeSchema[SanctionAppliedToCompany]):
    type: Literal["sanction_applied_to_company"] = "sanction_applied_to_company"

    @classmethod
    @override
    def domain(cls) -> type[SanctionAppliedToCompany]:
        return SanctionAppliedToCompany


class SanctionAppliedToPersonSchema(EdgeSchema[SanctionAppliedToPerson]):
    type: Literal["sanction_applied_to_person"] = "sanction_applied_to_person"

    @classmethod
    @override
    def domain(cls) -> type[SanctionAppliedToPerson]:
        return SanctionAppliedToPerson


class TextSourceMentionsAddressSchema(EdgeSchema[TextSourceMentionsAddress]):
    type: Literal["text_source_mentions_address"] = "text_source_mentions_address"

    matched_field: str
    pattern_name: str

    @classmethod
    @override
    def domain(cls) -> type[TextSourceMentionsAddress]:
        return TextSourceMentionsAddress


class TextSourceMentionsCompanySchema(EdgeSchema[TextSourceMentionsCompany]):
    type: Literal["text_source_mentions_company"] = "text_source_mentions_company"

    matched_field: str
    pattern_name: str

    @classmethod
    @override
    def domain(cls) -> type[TextSourceMentionsCompany]:
        return TextSourceMentionsCompany


class TextSourceMentionsPersonSchema(EdgeSchema[TextSourceMentionsPerson]):
    type: Literal["text_source_mentions_person"] = "text_source_mentions_person"

    matched_field: str
    pattern_name: str

    @classmethod
    @override
    def domain(cls) -> type[TextSourceMentionsPerson]:
        return TextSourceMentionsPerson


class PossiblyMatchesSchema(EdgeSchema[PossiblyMatches[UUID]]):
    type: Literal["possibly_matches"] = "possibly_matches"

    confidence: Decimal

    @classmethod
    @override
    def domain(cls) -> type[PossiblyMatches[UUID]]:
        return PossiblyMatches


EdgeSchemaUnion = (
    AddressMentionedInTextSchema
    | CompanyHasCnaeSchema
    | CompanyHasEmailSchema
    | CompanyHasMemberSchema
    | CompanyHasPhoneSchema
    | CompanyLocatedAtSchema
    | CompanyMentionedInTextSchema
    | CompanyIsPartyInLegalProcessSchema
    | CompanyOwnsCompanySchema
    | CompanyReceivedSanctionSchema
    | PersonHasEmailSchema
    | PersonHasPhoneSchema
    | PersonHasPoliticalExposureSchema
    | PersonIsPartyInLegalProcessSchema
    | PersonMentionedInTextSchema
    | PersonOwnsCompanySchema
    | PersonReceivedSanctionSchema
    | PersonResideAtSchema
    | AddressHostsCompanySchema
    | AddressHostsPersonSchema
    | CnaeClassifiesCompanySchema
    | CompanyOwnedByCompanySchema
    | EmailBelongsToCompanySchema
    | EmailBelongsToPersonSchema
    | LegalProcessHasCompanySchema
    | LegalProcessHasPersonSchema
    | PhoneBelongsToCompanySchema
    | PhoneBelongsToPersonSchema
    | PoliticalExposureOfPersonSchema
    | SanctionAppliedToCompanySchema
    | SanctionAppliedToPersonSchema
    | TextSourceMentionsAddressSchema
    | TextSourceMentionsCompanySchema
    | TextSourceMentionsPersonSchema
    | PossiblyMatchesSchema
)

EdgeUnion = Annotated[EdgeSchemaUnion, Field(discriminator="type")]


class EdgeSchemaRegistry:
    _REGISTRY: ClassVar[
        dict[type[Edge[UUID, UUID, UUID]], type[EdgeSchema[Edge[UUID, UUID, UUID]]]]
    ] = {}

    @classmethod
    def get_from_domain(
        cls, domain: type[Edge[UUID, UUID, UUID]], /
    ) -> type[EdgeSchema[Edge[UUID, UUID, UUID]]]:
        if domain not in cls._REGISTRY:
            raise UnmappedTypeSchemaError(subject=domain)

        return cls._REGISTRY[domain]

    @classmethod
    def register(cls, schema: type[EdgeSchema[Edge[UUID, UUID, UUID]]], /) -> None:
        key = schema.domain()

        if key in cls._REGISTRY:
            raise DuplicateSchemaRegistrationError(
                subject=key, existing_schema=cls._REGISTRY[key]
            )

        cls._REGISTRY[key] = schema


EdgeSchemaRegistry.register(AddressMentionedInTextSchema)
EdgeSchemaRegistry.register(CompanyHasCnaeSchema)
EdgeSchemaRegistry.register(CompanyHasEmailSchema)
EdgeSchemaRegistry.register(CompanyHasMemberSchema)
EdgeSchemaRegistry.register(CompanyHasPhoneSchema)
EdgeSchemaRegistry.register(CompanyLocatedAtSchema)
EdgeSchemaRegistry.register(CompanyMentionedInTextSchema)
EdgeSchemaRegistry.register(CompanyIsPartyInLegalProcessSchema)
EdgeSchemaRegistry.register(CompanyOwnsCompanySchema)
EdgeSchemaRegistry.register(CompanyReceivedSanctionSchema)
EdgeSchemaRegistry.register(PersonHasEmailSchema)
EdgeSchemaRegistry.register(PersonHasPhoneSchema)
EdgeSchemaRegistry.register(PersonHasPoliticalExposureSchema)
EdgeSchemaRegistry.register(PersonIsPartyInLegalProcessSchema)
EdgeSchemaRegistry.register(PersonMentionedInTextSchema)
EdgeSchemaRegistry.register(PersonOwnsCompanySchema)
EdgeSchemaRegistry.register(PersonReceivedSanctionSchema)
EdgeSchemaRegistry.register(PersonResideAtSchema)
EdgeSchemaRegistry.register(AddressHostsCompanySchema)
EdgeSchemaRegistry.register(AddressHostsPersonSchema)
EdgeSchemaRegistry.register(CnaeClassifiesCompanySchema)
EdgeSchemaRegistry.register(CompanyOwnedByCompanySchema)
EdgeSchemaRegistry.register(EmailBelongsToCompanySchema)
EdgeSchemaRegistry.register(EmailBelongsToPersonSchema)
EdgeSchemaRegistry.register(LegalProcessHasCompanySchema)
EdgeSchemaRegistry.register(LegalProcessHasPersonSchema)
EdgeSchemaRegistry.register(PhoneBelongsToCompanySchema)
EdgeSchemaRegistry.register(PhoneBelongsToPersonSchema)
EdgeSchemaRegistry.register(PoliticalExposureOfPersonSchema)
EdgeSchemaRegistry.register(SanctionAppliedToCompanySchema)
EdgeSchemaRegistry.register(SanctionAppliedToPersonSchema)
EdgeSchemaRegistry.register(TextSourceMentionsAddressSchema)
EdgeSchemaRegistry.register(TextSourceMentionsCompanySchema)
EdgeSchemaRegistry.register(TextSourceMentionsPersonSchema)
EdgeSchemaRegistry.register(PossiblyMatchesSchema)
