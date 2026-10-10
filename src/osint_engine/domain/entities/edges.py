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

AddressMentionedInTextID = NewType("AddressMentionedInTextID", UUID)
CompanyHasCnaeID = NewType("CompanyHasCnaeID", UUID)
CompanyHasEmailID = NewType("CompanyHasEmailID", UUID)
CompanyHasMemberID = NewType("CompanyHasMemberID", UUID)
CompanyHasPhoneID = NewType("CompanyHasPhoneID", UUID)
CompanyIsPartyInLegalProcessID = NewType("CompanyIsPartyInLegalProcessID", UUID)
CompanyLocatedAtID = NewType("CompanyLocatedAtID", UUID)
CompanyMentionedInTextID = NewType("CompanyMentionedInTextID", UUID)
CompanyOwnsCompanyID = NewType("CompanyOwnsCompanyID", UUID)
CompanyReceivedSanctionID = NewType("CompanyReceivedSanctionID", UUID)
PersonHasEmailID = NewType("PersonHasEmailID", UUID)
PersonHasPhoneID = NewType("PersonHasPhoneID", UUID)
PersonHasPoliticalExposureID = NewType("PersonHasPoliticalExposureID", UUID)
PersonIsPartyInLegalProcessID = NewType("PersonIsPartyInLegalProcessID", UUID)
PersonMentionedInTextID = NewType("PersonMentionedInTextID", UUID)
PersonOwnsCompanyID = NewType("PersonOwnsCompanyID", UUID)
PersonReceivedSanctionID = NewType("PersonReceivedSanctionID", UUID)
PersonResideAtID = NewType("PersonResideAtID", UUID)
PossiblyMatchesID = NewType("PossiblyMatchesID", UUID)


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
        pattern_name = kwargs.get("pattern_name")

        if isinstance(pattern_name, TextPatternName):
            kwargs["pattern_name"] = pattern_name.name

        return super()._calculate_id(**kwargs)


class CompanyHasCnae(
    Edge[CompanyHasCnaeID, CompanyID, CnaeID],
    id_fields=None,
    namespace=EntityNAMESPACE.COMPANY_CNAE,
):
    @override
    def __init__(self, *, source_id: CompanyID, target_id: CnaeID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)


class CompanyHasEmail(
    Edge[CompanyHasEmailID, CompanyID, EmailID],
    id_fields=None,
    namespace=EntityNAMESPACE.COMPANY_EMAIL,
):
    @override
    def __init__(self, *, source_id: CompanyID, target_id: EmailID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)


class CompanyHasMember(
    Edge[CompanyHasMemberID, CompanyID, PersonID],
    id_fields=None,
    namespace=EntityNAMESPACE.COMPANY_PERSON,
):
    @override
    def __init__(self, *, source_id: CompanyID, target_id: PersonID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)


class CompanyHasPhone(
    Edge[CompanyHasPhoneID, CompanyID, PhoneID],
    id_fields=None,
    namespace=EntityNAMESPACE.COMPANY_PHONE,
):
    @override
    def __init__(self, *, source_id: CompanyID, target_id: PhoneID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)


class CompanyIsPartyInLegalProcess(
    Edge[CompanyIsPartyInLegalProcessID, CompanyID, LegalProcessID],
    id_fields=None,
    namespace=EntityNAMESPACE.COMPANY_LEGAL_PROCESS,
):
    @override
    def __init__(self, *, source_id: CompanyID, target_id: LegalProcessID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)


class CompanyLocatedAt(
    Edge[CompanyLocatedAtID, CompanyID, AddressID],
    id_fields=None,
    namespace=EntityNAMESPACE.COMPANY_ADDRESS,
):
    @override
    def __init__(self, *, source_id: CompanyID, target_id: AddressID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)


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
        pattern_name = kwargs.get("pattern_name")

        if isinstance(pattern_name, TextPatternName):
            kwargs["pattern_name"] = pattern_name.name

        return super()._calculate_id(**kwargs)


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


class CompanyReceivedSanction(
    Edge[CompanyReceivedSanctionID, CompanyID, SanctionID],
    id_fields=None,
    namespace=EntityNAMESPACE.COMPANY_SANCTION,
):
    @override
    def __init__(self, *, source_id: CompanyID, target_id: SanctionID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)


class PersonHasEmail(
    Edge[PersonHasEmailID, PersonID, EmailID],
    id_fields=None,
    namespace=EntityNAMESPACE.PERSON_EMAIL,
):
    @override
    def __init__(self, *, source_id: PersonID, target_id: EmailID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)


class PersonHasPhone(
    Edge[PersonHasPhoneID, PersonID, PhoneID],
    id_fields=None,
    namespace=EntityNAMESPACE.PERSON_PHONE,
):
    @override
    def __init__(self, *, source_id: PersonID, target_id: PhoneID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)


class PersonHasPoliticalExposure(
    Edge[PersonHasPoliticalExposureID, PersonID, PoliticalExposureID],
    id_fields=None,
    namespace=EntityNAMESPACE.PERSON_POLITICAL_EXPOSURE,
):
    @override
    def __init__(self, *, source_id: PersonID, target_id: PoliticalExposureID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)


class PersonIsPartyInLegalProcess(
    Edge[PersonIsPartyInLegalProcessID, PersonID, LegalProcessID],
    id_fields=None,
    namespace=EntityNAMESPACE.PERSON_LEGAL_PROCESS,
):
    @override
    def __init__(self, *, source_id: PersonID, target_id: LegalProcessID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)


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
        pattern_name = kwargs.get("pattern_name")

        if isinstance(pattern_name, TextPatternName):
            kwargs["pattern_name"] = pattern_name.name

        return super()._calculate_id(**kwargs)


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


class PersonReceivedSanction(
    Edge[PersonReceivedSanctionID, PersonID, SanctionID],
    id_fields=None,
    namespace=EntityNAMESPACE.PERSON_SANCTION,
):
    @override
    def __init__(self, *, source_id: PersonID, target_id: SanctionID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)


class PersonResideAt(
    Edge[PersonResideAtID, PersonID, AddressID],
    id_fields=None,
    namespace=EntityNAMESPACE.PERSON_ADDRESS,
):
    @override
    def __init__(self, *, source_id: PersonID, target_id: AddressID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)


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
