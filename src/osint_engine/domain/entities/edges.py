from __future__ import annotations

from typing import TYPE_CHECKING, NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.entities.nodes import (
    AddressID,
    CnaeID,
    CompanyID,
    EmailID,
    LegalProcessID,
    PersonID,
    PhoneID,
    PoliticalExposureID,
    SanctionID,
    TextSourceID,
)
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE
from osint_engine.domain.value_objects.text_pattern import TextPatternName

if TYPE_CHECKING:
    from decimal import Decimal

AddressHostsCompanyID = NewType("AddressHostsCompanyID", UUID)
AddressHostsPersonID = NewType("AddressHostsPersonID", UUID)
AddressMentionedInTextID = NewType("AddressMentionedInTextID", UUID)
CnaeClassifiesCompanyID = NewType("CnaeClassifiesCompanyID", UUID)
CompanyHasCnaeID = NewType("CompanyHasCnaeID", UUID)
CompanyHasEmailID = NewType("CompanyHasEmailID", UUID)
CompanyHasMemberID = NewType("CompanyHasMemberID", UUID)
CompanyHasPhoneID = NewType("CompanyHasPhoneID", UUID)
CompanyIsPartyInLegalProcessID = NewType("CompanyIsPartyInLegalProcessID", UUID)
CompanyLocatedAtID = NewType("CompanyLocatedAtID", UUID)
CompanyMentionedInTextID = NewType("CompanyMentionedInTextID", UUID)
CompanyOwnedByCompanyID = NewType("CompanyOwnedByCompanyID", UUID)
CompanyOwnsCompanyID = NewType("CompanyOwnsCompanyID", UUID)
CompanyReceivedSanctionID = NewType("CompanyReceivedSanctionID", UUID)
EmailBelongsToCompanyID = NewType("EmailBelongsToCompanyID", UUID)
EmailBelongsToPersonID = NewType("EmailBelongsToPersonID", UUID)
LegalProcessHasCompanyID = NewType("LegalProcessHasCompanyID", UUID)
LegalProcessHasPersonID = NewType("LegalProcessHasPersonID", UUID)
PersonHasEmailID = NewType("PersonHasEmailID", UUID)
PersonHasPhoneID = NewType("PersonHasPhoneID", UUID)
PersonHasPoliticalExposureID = NewType("PersonHasPoliticalExposureID", UUID)
PersonIsPartyInLegalProcessID = NewType("PersonIsPartyInLegalProcessID", UUID)
PersonMentionedInTextID = NewType("PersonMentionedInTextID", UUID)
PersonOwnsCompanyID = NewType("PersonOwnsCompanyID", UUID)
PersonReceivedSanctionID = NewType("PersonReceivedSanctionID", UUID)
PersonResideAtID = NewType("PersonResideAtID", UUID)
PhoneBelongsToCompanyID = NewType("PhoneBelongsToCompanyID", UUID)
PhoneBelongsToPersonID = NewType("PhoneBelongsToPersonID", UUID)
PoliticalExposureOfPersonID = NewType("PoliticalExposureOfPersonID", UUID)
PossiblyMatchesID = NewType("PossiblyMatchesID", UUID)
SanctionAppliedToCompanyID = NewType("SanctionAppliedToCompanyID", UUID)
SanctionAppliedToPersonID = NewType("SanctionAppliedToPersonID", UUID)
TextSourceMentionsAddressID = NewType("TextSourceMentionsAddressID", UUID)
TextSourceMentionsCompanyID = NewType("TextSourceMentionsCompanyID", UUID)
TextSourceMentionsPersonID = NewType("TextSourceMentionsPersonID", UUID)


def _pattern_name_as_text(kwargs: dict[str, object]) -> dict[str, object]:
    pattern_name = kwargs.get("pattern_name")

    if isinstance(pattern_name, TextPatternName):
        kwargs["pattern_name"] = pattern_name.name

    return kwargs


class AddressHostsCompany(
    Edge[AddressHostsCompanyID, AddressID, CompanyID],
    id_fields=None,
    namespace=EntityNAMESPACE.ADDRESS_COMPANY,
):
    @override
    def __init__(self, *, source_id: AddressID, target_id: CompanyID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> CompanyLocatedAt:
        return CompanyLocatedAt(source_id=self.target_id, target_id=self.source_id)


class AddressHostsPerson(
    Edge[AddressHostsPersonID, AddressID, PersonID],
    id_fields=None,
    namespace=EntityNAMESPACE.ADDRESS_PERSON,
):
    @override
    def __init__(self, *, source_id: AddressID, target_id: PersonID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> PersonResideAt:
        return PersonResideAt(source_id=self.target_id, target_id=self.source_id)


class AddressMentionedInText(
    Edge[AddressMentionedInTextID, AddressID, TextSourceID],
    id_fields=frozenset({"pattern_name"}),
    namespace=EntityNAMESPACE.ADDRESS_TEXT_SOURCE,
):
    matched_field: str
    pattern_name: TextPatternName

    @override
    def __init__(
        self,
        *,
        source_id: AddressID,
        target_id: TextSourceID,
        matched_field: str,
        pattern_name: TextPatternName,
    ) -> None:
        super().__init__(
            source_id=source_id,
            target_id=target_id,
            matched_field=matched_field,
            pattern_name=pattern_name,
        )

    @classmethod
    @override
    def _calculate_id(cls, **kwargs: object) -> AddressMentionedInTextID:
        return super()._calculate_id(**_pattern_name_as_text(kwargs))

    @override
    def invert(self) -> TextSourceMentionsAddress:
        return TextSourceMentionsAddress(
            source_id=self.target_id,
            target_id=self.source_id,
            matched_field=self.matched_field,
            pattern_name=self.pattern_name,
        )


class CnaeClassifiesCompany(
    Edge[CnaeClassifiesCompanyID, CnaeID, CompanyID],
    id_fields=None,
    namespace=EntityNAMESPACE.CNAE_COMPANY,
):
    @override
    def __init__(self, *, source_id: CnaeID, target_id: CompanyID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> CompanyHasCnae:
        return CompanyHasCnae(source_id=self.target_id, target_id=self.source_id)


class CompanyHasCnae(
    Edge[CompanyHasCnaeID, CompanyID, CnaeID],
    id_fields=None,
    namespace=EntityNAMESPACE.COMPANY_CNAE,
):
    @override
    def __init__(self, *, source_id: CompanyID, target_id: CnaeID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> CnaeClassifiesCompany:
        return CnaeClassifiesCompany(source_id=self.target_id, target_id=self.source_id)


class CompanyHasEmail(
    Edge[CompanyHasEmailID, CompanyID, EmailID],
    id_fields=None,
    namespace=EntityNAMESPACE.COMPANY_EMAIL,
):
    @override
    def __init__(self, *, source_id: CompanyID, target_id: EmailID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> EmailBelongsToCompany:
        return EmailBelongsToCompany(source_id=self.target_id, target_id=self.source_id)


class CompanyHasMember(
    Edge[CompanyHasMemberID, CompanyID, PersonID],
    id_fields=None,
    namespace=EntityNAMESPACE.COMPANY_PERSON,
):
    @override
    def __init__(self, *, source_id: CompanyID, target_id: PersonID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> None:
        return None


class CompanyHasPhone(
    Edge[CompanyHasPhoneID, CompanyID, PhoneID],
    id_fields=None,
    namespace=EntityNAMESPACE.COMPANY_PHONE,
):
    @override
    def __init__(self, *, source_id: CompanyID, target_id: PhoneID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> PhoneBelongsToCompany:
        return PhoneBelongsToCompany(source_id=self.target_id, target_id=self.source_id)


class CompanyIsPartyInLegalProcess(
    Edge[CompanyIsPartyInLegalProcessID, CompanyID, LegalProcessID],
    id_fields=None,
    namespace=EntityNAMESPACE.COMPANY_LEGAL_PROCESS,
):
    @override
    def __init__(self, *, source_id: CompanyID, target_id: LegalProcessID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> LegalProcessHasCompany:
        return LegalProcessHasCompany(
            source_id=self.target_id, target_id=self.source_id
        )


class CompanyLocatedAt(
    Edge[CompanyLocatedAtID, CompanyID, AddressID],
    id_fields=None,
    namespace=EntityNAMESPACE.COMPANY_ADDRESS,
):
    @override
    def __init__(self, *, source_id: CompanyID, target_id: AddressID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> AddressHostsCompany:
        return AddressHostsCompany(source_id=self.target_id, target_id=self.source_id)


class CompanyMentionedInText(
    Edge[CompanyMentionedInTextID, CompanyID, TextSourceID],
    id_fields=frozenset({"pattern_name"}),
    namespace=EntityNAMESPACE.COMPANY_TEXT_SOURCE,
):
    matched_field: str
    pattern_name: TextPatternName

    @override
    def __init__(
        self,
        *,
        source_id: CompanyID,
        target_id: TextSourceID,
        matched_field: str,
        pattern_name: TextPatternName,
    ) -> None:
        super().__init__(
            source_id=source_id,
            target_id=target_id,
            matched_field=matched_field,
            pattern_name=pattern_name,
        )

    @classmethod
    @override
    def _calculate_id(cls, **kwargs: object) -> CompanyMentionedInTextID:
        return super()._calculate_id(**_pattern_name_as_text(kwargs))

    @override
    def invert(self) -> TextSourceMentionsCompany:
        return TextSourceMentionsCompany(
            source_id=self.target_id,
            target_id=self.source_id,
            matched_field=self.matched_field,
            pattern_name=self.pattern_name,
        )


class CompanyOwnedByCompany(
    Edge[CompanyOwnedByCompanyID, CompanyID, CompanyID],
    id_fields=None,
    namespace=EntityNAMESPACE.COMPANY_OWNER_COMPANY,
):
    entry_date: str
    role: str

    @override
    def __init__(
        self, *, source_id: CompanyID, target_id: CompanyID, entry_date: str, role: str
    ) -> None:
        super().__init__(
            source_id=source_id, target_id=target_id, entry_date=entry_date, role=role
        )

    @override
    def invert(self) -> CompanyOwnsCompany:
        return CompanyOwnsCompany(
            source_id=self.target_id,
            target_id=self.source_id,
            entry_date=self.entry_date,
            role=self.role,
        )


class CompanyOwnsCompany(
    Edge[CompanyOwnsCompanyID, CompanyID, CompanyID],
    id_fields=None,
    namespace=EntityNAMESPACE.COMPANY_COMPANY,
):
    entry_date: str
    role: str

    @override
    def __init__(
        self, *, source_id: CompanyID, target_id: CompanyID, entry_date: str, role: str
    ) -> None:
        super().__init__(
            source_id=source_id, target_id=target_id, entry_date=entry_date, role=role
        )

    @override
    def invert(self) -> CompanyOwnedByCompany:
        return CompanyOwnedByCompany(
            source_id=self.target_id,
            target_id=self.source_id,
            entry_date=self.entry_date,
            role=self.role,
        )


class CompanyReceivedSanction(
    Edge[CompanyReceivedSanctionID, CompanyID, SanctionID],
    id_fields=None,
    namespace=EntityNAMESPACE.COMPANY_SANCTION,
):
    @override
    def __init__(self, *, source_id: CompanyID, target_id: SanctionID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> SanctionAppliedToCompany:
        return SanctionAppliedToCompany(
            source_id=self.target_id, target_id=self.source_id
        )


class EmailBelongsToCompany(
    Edge[EmailBelongsToCompanyID, EmailID, CompanyID],
    id_fields=None,
    namespace=EntityNAMESPACE.EMAIL_COMPANY,
):
    @override
    def __init__(self, *, source_id: EmailID, target_id: CompanyID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> CompanyHasEmail:
        return CompanyHasEmail(source_id=self.target_id, target_id=self.source_id)


class EmailBelongsToPerson(
    Edge[EmailBelongsToPersonID, EmailID, PersonID],
    id_fields=None,
    namespace=EntityNAMESPACE.EMAIL_PERSON,
):
    @override
    def __init__(self, *, source_id: EmailID, target_id: PersonID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> PersonHasEmail:
        return PersonHasEmail(source_id=self.target_id, target_id=self.source_id)


class LegalProcessHasCompany(
    Edge[LegalProcessHasCompanyID, LegalProcessID, CompanyID],
    id_fields=None,
    namespace=EntityNAMESPACE.LEGAL_PROCESS_COMPANY,
):
    @override
    def __init__(self, *, source_id: LegalProcessID, target_id: CompanyID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> CompanyIsPartyInLegalProcess:
        return CompanyIsPartyInLegalProcess(
            source_id=self.target_id, target_id=self.source_id
        )


class LegalProcessHasPerson(
    Edge[LegalProcessHasPersonID, LegalProcessID, PersonID],
    id_fields=None,
    namespace=EntityNAMESPACE.LEGAL_PROCESS_PERSON,
):
    @override
    def __init__(self, *, source_id: LegalProcessID, target_id: PersonID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> PersonIsPartyInLegalProcess:
        return PersonIsPartyInLegalProcess(
            source_id=self.target_id, target_id=self.source_id
        )


class PersonHasEmail(
    Edge[PersonHasEmailID, PersonID, EmailID],
    id_fields=None,
    namespace=EntityNAMESPACE.PERSON_EMAIL,
):
    @override
    def __init__(self, *, source_id: PersonID, target_id: EmailID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> EmailBelongsToPerson:
        return EmailBelongsToPerson(source_id=self.target_id, target_id=self.source_id)


class PersonHasPhone(
    Edge[PersonHasPhoneID, PersonID, PhoneID],
    id_fields=None,
    namespace=EntityNAMESPACE.PERSON_PHONE,
):
    @override
    def __init__(self, *, source_id: PersonID, target_id: PhoneID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> PhoneBelongsToPerson:
        return PhoneBelongsToPerson(source_id=self.target_id, target_id=self.source_id)


class PersonHasPoliticalExposure(
    Edge[PersonHasPoliticalExposureID, PersonID, PoliticalExposureID],
    id_fields=None,
    namespace=EntityNAMESPACE.PERSON_POLITICAL_EXPOSURE,
):
    @override
    def __init__(self, *, source_id: PersonID, target_id: PoliticalExposureID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> PoliticalExposureOfPerson:
        return PoliticalExposureOfPerson(
            source_id=self.target_id, target_id=self.source_id
        )


class PersonIsPartyInLegalProcess(
    Edge[PersonIsPartyInLegalProcessID, PersonID, LegalProcessID],
    id_fields=None,
    namespace=EntityNAMESPACE.PERSON_LEGAL_PROCESS,
):
    @override
    def __init__(self, *, source_id: PersonID, target_id: LegalProcessID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> LegalProcessHasPerson:
        return LegalProcessHasPerson(source_id=self.target_id, target_id=self.source_id)


class PersonMentionedInText(
    Edge[PersonMentionedInTextID, PersonID, TextSourceID],
    id_fields=frozenset({"pattern_name"}),
    namespace=EntityNAMESPACE.PERSON_TEXT_SOURCE,
):
    matched_field: str
    pattern_name: TextPatternName

    @override
    def __init__(
        self,
        *,
        source_id: PersonID,
        target_id: TextSourceID,
        matched_field: str,
        pattern_name: TextPatternName,
    ) -> None:
        super().__init__(
            source_id=source_id,
            target_id=target_id,
            matched_field=matched_field,
            pattern_name=pattern_name,
        )

    @classmethod
    @override
    def _calculate_id(cls, **kwargs: object) -> PersonMentionedInTextID:
        return super()._calculate_id(**_pattern_name_as_text(kwargs))

    @override
    def invert(self) -> TextSourceMentionsPerson:
        return TextSourceMentionsPerson(
            source_id=self.target_id,
            target_id=self.source_id,
            matched_field=self.matched_field,
            pattern_name=self.pattern_name,
        )


class PersonOwnsCompany(
    Edge[PersonOwnsCompanyID, PersonID, CompanyID],
    id_fields=None,
    namespace=EntityNAMESPACE.PERSON_COMPANY,
):
    entry_date: str
    role: str

    @override
    def __init__(
        self, *, source_id: PersonID, target_id: CompanyID, entry_date: str, role: str
    ) -> None:
        super().__init__(
            source_id=source_id, target_id=target_id, entry_date=entry_date, role=role
        )

    @override
    def invert(self) -> None:
        return None


class PersonReceivedSanction(
    Edge[PersonReceivedSanctionID, PersonID, SanctionID],
    id_fields=None,
    namespace=EntityNAMESPACE.PERSON_SANCTION,
):
    @override
    def __init__(self, *, source_id: PersonID, target_id: SanctionID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> SanctionAppliedToPerson:
        return SanctionAppliedToPerson(
            source_id=self.target_id, target_id=self.source_id
        )


class PersonResideAt(
    Edge[PersonResideAtID, PersonID, AddressID],
    id_fields=None,
    namespace=EntityNAMESPACE.PERSON_ADDRESS,
):
    @override
    def __init__(self, *, source_id: PersonID, target_id: AddressID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> AddressHostsPerson:
        return AddressHostsPerson(source_id=self.target_id, target_id=self.source_id)


class PhoneBelongsToCompany(
    Edge[PhoneBelongsToCompanyID, PhoneID, CompanyID],
    id_fields=None,
    namespace=EntityNAMESPACE.PHONE_COMPANY,
):
    @override
    def __init__(self, *, source_id: PhoneID, target_id: CompanyID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> CompanyHasPhone:
        return CompanyHasPhone(source_id=self.target_id, target_id=self.source_id)


class PhoneBelongsToPerson(
    Edge[PhoneBelongsToPersonID, PhoneID, PersonID],
    id_fields=None,
    namespace=EntityNAMESPACE.PHONE_PERSON,
):
    @override
    def __init__(self, *, source_id: PhoneID, target_id: PersonID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> PersonHasPhone:
        return PersonHasPhone(source_id=self.target_id, target_id=self.source_id)


class PoliticalExposureOfPerson(
    Edge[PoliticalExposureOfPersonID, PoliticalExposureID, PersonID],
    id_fields=None,
    namespace=EntityNAMESPACE.POLITICAL_EXPOSURE_PERSON,
):
    @override
    def __init__(self, *, source_id: PoliticalExposureID, target_id: PersonID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> PersonHasPoliticalExposure:
        return PersonHasPoliticalExposure(
            source_id=self.target_id, target_id=self.source_id
        )


class PossiblyMatches[NodeID: UUID](
    Edge[PossiblyMatchesID, NodeID, NodeID],
    id_fields=None,
    namespace=EntityNAMESPACE.POSSIBLY_MATCHES,
):
    confidence: Decimal

    @override
    def __init__(
        self, *, source_id: NodeID, target_id: NodeID, confidence: Decimal
    ) -> None:
        if source_id > target_id:
            source_id, target_id = target_id, source_id

        super().__init__(
            source_id=source_id, target_id=target_id, confidence=confidence
        )

    @override
    def invert(self) -> None:
        return None


class SanctionAppliedToCompany(
    Edge[SanctionAppliedToCompanyID, SanctionID, CompanyID],
    id_fields=None,
    namespace=EntityNAMESPACE.SANCTION_COMPANY,
):
    @override
    def __init__(self, *, source_id: SanctionID, target_id: CompanyID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> CompanyReceivedSanction:
        return CompanyReceivedSanction(
            source_id=self.target_id, target_id=self.source_id
        )


class SanctionAppliedToPerson(
    Edge[SanctionAppliedToPersonID, SanctionID, PersonID],
    id_fields=None,
    namespace=EntityNAMESPACE.SANCTION_PERSON,
):
    @override
    def __init__(self, *, source_id: SanctionID, target_id: PersonID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)

    @override
    def invert(self) -> PersonReceivedSanction:
        return PersonReceivedSanction(
            source_id=self.target_id, target_id=self.source_id
        )


class TextSourceMentionsAddress(
    Edge[TextSourceMentionsAddressID, TextSourceID, AddressID],
    id_fields=frozenset({"pattern_name"}),
    namespace=EntityNAMESPACE.TEXT_SOURCE_ADDRESS,
):
    matched_field: str
    pattern_name: TextPatternName

    @override
    def __init__(
        self,
        *,
        source_id: TextSourceID,
        target_id: AddressID,
        matched_field: str,
        pattern_name: TextPatternName,
    ) -> None:
        super().__init__(
            source_id=source_id,
            target_id=target_id,
            matched_field=matched_field,
            pattern_name=pattern_name,
        )

    @classmethod
    @override
    def _calculate_id(cls, **kwargs: object) -> TextSourceMentionsAddressID:
        return super()._calculate_id(**_pattern_name_as_text(kwargs))

    @override
    def invert(self) -> AddressMentionedInText:
        return AddressMentionedInText(
            source_id=self.target_id,
            target_id=self.source_id,
            matched_field=self.matched_field,
            pattern_name=self.pattern_name,
        )


class TextSourceMentionsCompany(
    Edge[TextSourceMentionsCompanyID, TextSourceID, CompanyID],
    id_fields=frozenset({"pattern_name"}),
    namespace=EntityNAMESPACE.TEXT_SOURCE_COMPANY,
):
    matched_field: str
    pattern_name: TextPatternName

    @override
    def __init__(
        self,
        *,
        source_id: TextSourceID,
        target_id: CompanyID,
        matched_field: str,
        pattern_name: TextPatternName,
    ) -> None:
        super().__init__(
            source_id=source_id,
            target_id=target_id,
            matched_field=matched_field,
            pattern_name=pattern_name,
        )

    @classmethod
    @override
    def _calculate_id(cls, **kwargs: object) -> TextSourceMentionsCompanyID:
        return super()._calculate_id(**_pattern_name_as_text(kwargs))

    @override
    def invert(self) -> CompanyMentionedInText:
        return CompanyMentionedInText(
            source_id=self.target_id,
            target_id=self.source_id,
            matched_field=self.matched_field,
            pattern_name=self.pattern_name,
        )


class TextSourceMentionsPerson(
    Edge[TextSourceMentionsPersonID, TextSourceID, PersonID],
    id_fields=frozenset({"pattern_name"}),
    namespace=EntityNAMESPACE.TEXT_SOURCE_PERSON,
):
    matched_field: str
    pattern_name: TextPatternName

    @override
    def __init__(
        self,
        *,
        source_id: TextSourceID,
        target_id: PersonID,
        matched_field: str,
        pattern_name: TextPatternName,
    ) -> None:
        super().__init__(
            source_id=source_id,
            target_id=target_id,
            matched_field=matched_field,
            pattern_name=pattern_name,
        )

    @classmethod
    @override
    def _calculate_id(cls, **kwargs: object) -> TextSourceMentionsPersonID:
        return super()._calculate_id(**_pattern_name_as_text(kwargs))

    @override
    def invert(self) -> PersonMentionedInText:
        return PersonMentionedInText(
            source_id=self.target_id,
            target_id=self.source_id,
            matched_field=self.matched_field,
            pattern_name=self.pattern_name,
        )
