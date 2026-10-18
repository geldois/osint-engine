from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

import pytest

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
from osint_engine.domain.entities.graphs import CompositeGraph
from osint_engine.domain.entities.nodes import (
    AddressID,
    Cnae,
    CnaeID,
    Company,
    CompanyID,
    EmailID,
    LegalProcessID,
    PersonID,
    PhoneID,
    PoliticalExposureID,
    SanctionID,
    TextSourceID,
)
from osint_engine.domain.value_objects.text_pattern import TextPatternName

_address_id = AddressID(uuid4())
_cnae_id = CnaeID(uuid4())
_company_id = CompanyID(uuid4())
_other_company_id = CompanyID(uuid4())
_email_id = EmailID(uuid4())
_legal_process_id = LegalProcessID(uuid4())
_person_id = PersonID(uuid4())
_phone_id = PhoneID(uuid4())
_political_exposure_id = PoliticalExposureID(uuid4())
_sanction_id = SanctionID(uuid4())
_text_source_id = TextSourceID(uuid4())

_Pair = tuple[Edge[UUID, UUID, UUID], type[Edge[UUID, UUID, UUID]]]

_FORWARD_AND_INVERSE: list[_Pair] = [
    (
        CompanyLocatedAt(source_id=_company_id, target_id=_address_id),
        AddressHostsCompany,
    ),
    (PersonResideAt(source_id=_person_id, target_id=_address_id), AddressHostsPerson),
    (
        CompanyHasCnae(source_id=_company_id, target_id=_cnae_id),
        CnaeClassifiesCompany,
    ),
    (
        CompanyHasEmail(source_id=_company_id, target_id=_email_id),
        EmailBelongsToCompany,
    ),
    (PersonHasEmail(source_id=_person_id, target_id=_email_id), EmailBelongsToPerson),
    (
        CompanyHasPhone(source_id=_company_id, target_id=_phone_id),
        PhoneBelongsToCompany,
    ),
    (PersonHasPhone(source_id=_person_id, target_id=_phone_id), PhoneBelongsToPerson),
    (
        CompanyIsPartyInLegalProcess(
            source_id=_company_id, target_id=_legal_process_id
        ),
        LegalProcessHasCompany,
    ),
    (
        PersonIsPartyInLegalProcess(source_id=_person_id, target_id=_legal_process_id),
        LegalProcessHasPerson,
    ),
    (
        CompanyReceivedSanction(source_id=_company_id, target_id=_sanction_id),
        SanctionAppliedToCompany,
    ),
    (
        PersonReceivedSanction(source_id=_person_id, target_id=_sanction_id),
        SanctionAppliedToPerson,
    ),
    (
        PersonHasPoliticalExposure(
            source_id=_person_id, target_id=_political_exposure_id
        ),
        PoliticalExposureOfPerson,
    ),
    (
        CompanyMentionedInText(
            source_id=_company_id,
            target_id=_text_source_id,
            matched_field="cnpj",
            pattern_name=TextPatternName.CPF_LOOSE,
        ),
        TextSourceMentionsCompany,
    ),
    (
        PersonMentionedInText(
            source_id=_person_id,
            target_id=_text_source_id,
            matched_field="cpf",
            pattern_name=TextPatternName.CPF_LOOSE,
        ),
        TextSourceMentionsPerson,
    ),
    (
        AddressMentionedInText(
            source_id=_address_id,
            target_id=_text_source_id,
            matched_field="cep,number",
            pattern_name=TextPatternName.CPF_LOOSE,
        ),
        TextSourceMentionsAddress,
    ),
    (
        CompanyOwnsCompany(
            source_id=_company_id,
            target_id=_other_company_id,
            entry_date="2021-03-15",
            role="SÓCIO",
        ),
        CompanyOwnedByCompany,
    ),
]

_IDS = [type(forward).__name__ for forward, _ in _FORWARD_AND_INVERSE]


class TestInvertedEdges:
    @pytest.mark.parametrize(
        ("forward", "inverse_type"), _FORWARD_AND_INVERSE, ids=_IDS
    )
    def test_forward_edge_inverts_to_the_opposite_direction(
        self,
        forward: Edge[UUID, UUID, UUID],
        inverse_type: type[Edge[UUID, UUID, UUID]],
    ) -> None:
        inverse = forward.invert()

        assert isinstance(inverse, inverse_type)
        assert inverse.source_id == forward.target_id
        assert inverse.target_id == forward.source_id

    @pytest.mark.parametrize(
        ("forward", "inverse_type"), _FORWARD_AND_INVERSE, ids=_IDS
    )
    def test_inverse_edge_inverts_back_to_the_forward_edge(
        self,
        forward: Edge[UUID, UUID, UUID],
        inverse_type: type[Edge[UUID, UUID, UUID]],
    ) -> None:
        inverse = forward.invert()

        assert inverse is not None
        assert isinstance(inverse, inverse_type)

        back = inverse.invert()

        assert back == forward
        assert back is not None
        assert back.content_id == forward.content_id

    @pytest.mark.parametrize(
        ("forward", "inverse_type"), _FORWARD_AND_INVERSE, ids=_IDS
    )
    def test_forward_and_inverse_never_share_an_identifier(
        self,
        forward: Edge[UUID, UUID, UUID],
        inverse_type: type[Edge[UUID, UUID, UUID]],
    ) -> None:
        inverse = forward.invert()

        assert isinstance(inverse, inverse_type)
        assert inverse.id != forward.id

    def test_company_ownership_payload_travels_with_the_inverse(self) -> None:
        forward = CompanyOwnsCompany(
            source_id=_company_id,
            target_id=_other_company_id,
            entry_date="2021-03-15",
            role="SÓCIO",
        )

        inverse = forward.invert()

        assert inverse.entry_date == "2021-03-15"
        assert inverse.role == "SÓCIO"

    def test_mention_payload_travels_with_the_inverse(self) -> None:
        forward = PersonMentionedInText(
            source_id=_person_id,
            target_id=_text_source_id,
            matched_field="cpf",
            pattern_name=TextPatternName.CPF_LOOSE,
        )

        inverse = forward.invert()

        assert inverse.matched_field == "cpf"
        assert inverse.pattern_name is TextPatternName.CPF_LOOSE

    def test_edges_that_already_have_a_counterpart_or_are_symmetric_have_no_inverse(
        self,
    ) -> None:
        member = CompanyHasMember(source_id=_company_id, target_id=_person_id)
        owner = PersonOwnsCompany(
            source_id=_person_id,
            target_id=_company_id,
            entry_date="2021-03-15",
            role="SÓCIO",
        )
        match = PossiblyMatches(
            source_id=_person_id, target_id=_company_id, confidence=Decimal("0.5")
        )

        assert member.invert() is None
        assert owner.invert() is None
        assert match.invert() is None


class TestGraphInversionClosure:
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
    _CNAE = Cnae(code="0101-3/01", description="Cultivo de arroz")

    def _graph(self, *edges: Edge[UUID, UUID, UUID]) -> CompositeGraph:
        return CompositeGraph(
            nodes=frozenset({self._COMPANY, self._CNAE}),
            edges=frozenset(edges),
            root_id=self._COMPANY.id,
        )

    def test_graph_adds_the_inverse_of_every_edge_it_is_given(self) -> None:
        forward = CompanyHasCnae(source_id=self._COMPANY.id, target_id=self._CNAE.id)

        graph = self._graph(forward)

        assert graph.edges == frozenset({forward, forward.invert()})

    def test_graph_given_only_the_inverse_gains_the_forward_edge(self) -> None:
        inverse = CnaeClassifiesCompany(
            source_id=self._CNAE.id, target_id=self._COMPANY.id
        )

        graph = self._graph(inverse)

        assert graph.edges == frozenset({inverse, inverse.invert()})

    def test_graph_given_both_directions_does_not_duplicate_them(self) -> None:
        forward = CompanyHasCnae(source_id=self._COMPANY.id, target_id=self._CNAE.id)
        inverse = CnaeClassifiesCompany(
            source_id=self._CNAE.id, target_id=self._COMPANY.id
        )

        graph = self._graph(forward, inverse)

        assert len(graph.edges) == 2

    def test_graph_leaves_edges_without_an_inverse_untouched(self) -> None:
        match = PossiblyMatches(
            source_id=self._COMPANY.id,
            target_id=self._CNAE.id,
            confidence=Decimal("0.5"),
        )

        graph = self._graph(match)

        assert graph.edges == frozenset({match})

    def test_merging_two_graphs_keeps_the_closure(self) -> None:
        forward = CompanyHasCnae(source_id=self._COMPANY.id, target_id=self._CNAE.id)

        merged = self._graph(forward).merge(other=self._graph(forward))

        assert merged.edges == frozenset({forward, forward.invert()})
