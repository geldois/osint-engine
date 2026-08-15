from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from osint_engine.application.errors.text_ingestion_error import (
    NoPatternMatchedError,
    UnknownPatternNameError,
)
from osint_engine.application.use_cases.text_ingestion.ingest_text import IngestText
from osint_engine.domain.entities.edges.address_mentioned_in_text import (
    AddressMentionedInText,
)
from osint_engine.domain.entities.edges.company_mentioned_in_text import (
    CompanyMentionedInText,
)
from osint_engine.domain.entities.edges.person_mentioned_in_text import (
    PersonMentionedInText,
)
from osint_engine.domain.entities.nodes.address import Address
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.entities.nodes.text_source import TextSource
from osint_engine.domain.value_objects.text_pattern import TextPatternName
from osint_engine.infrastructure.persistence.mem.default_pattern_sets import (
    BRAZILIAN_DOCUMENTS_V1,
)
from osint_engine.infrastructure.persistence.mem.repositories.mem_pattern_set_repository import (  # noqa: E501
    MemPatternSetRepository,
)

if TYPE_CHECKING:
    from tests.conftest import MakeEntityRevision, MakeMemStorage, MakeMemUoW
    from tests.test_src.test_application.conftest import MakeMemUoWFactory

_VALID_CPF_LABELED_TEXT = "Contato: CPF 11144477735"
_VALID_CPF_DIGITS = "11144477735"
_VALID_CNPJ_TEXT = "Empresa CNPJ 11.222.333/0001-81 registrada"
_VALID_CEP_AND_NUMBER_TEXT = "Endereco: CEP 01310-100, numero 500"


def _pattern_set_repository() -> MemPatternSetRepository:
    return MemPatternSetRepository(pattern_sets=(BRAZILIAN_DOCUMENTS_V1,))


class TestIngestTextCompanyAndAddressStubs:
    @pytest.mark.asyncio
    async def test_creates_a_stub_company_and_links_it_to_the_text_provider(
        self, make_mem_uow_factory: MakeMemUoWFactory
    ) -> None:
        use_case = IngestText(
            uow_factory=make_mem_uow_factory(),
            pattern_set_repository=_pattern_set_repository(),
            patterns=frozenset({"CNPJ_LOOSE"}),
            text=_VALID_CNPJ_TEXT,
        )

        graph = await use_case.execute()

        companies = [node for node in graph.nodes if isinstance(node, Company)]
        assert len(companies) == 1
        assert companies[0].cnpj == "11.222.333/0001-81"
        assert companies[0].legal_name is None

        mention_edges = [
            edge for edge in graph.edges if isinstance(edge, CompanyMentionedInText)
        ]
        assert len(mention_edges) == 1
        assert mention_edges[0].source_id == companies[0].id
        assert mention_edges[0].pattern_name is TextPatternName.CNPJ_LOOSE

    @pytest.mark.asyncio
    async def test_creates_a_stub_address_and_links_it_to_the_text_provider(
        self, make_mem_uow_factory: MakeMemUoWFactory
    ) -> None:
        use_case = IngestText(
            uow_factory=make_mem_uow_factory(),
            pattern_set_repository=_pattern_set_repository(),
            patterns=frozenset({"CEP_AND_NUMBER"}),
            text=_VALID_CEP_AND_NUMBER_TEXT,
        )

        graph = await use_case.execute()

        addresses = [node for node in graph.nodes if isinstance(node, Address)]
        assert len(addresses) == 1
        assert addresses[0].cep == "01310-100"
        assert addresses[0].number == "500"
        assert addresses[0].street is None

        mention_edges = [
            edge for edge in graph.edges if isinstance(edge, AddressMentionedInText)
        ]
        assert len(mention_edges) == 1
        assert mention_edges[0].source_id == addresses[0].id
        assert mention_edges[0].matched_field == "cep,number"


class TestIngestTextNewStub:
    @pytest.mark.asyncio
    async def test_creates_a_stub_person_and_links_it_to_the_text_provider(
        self, make_mem_uow_factory: MakeMemUoWFactory
    ) -> None:
        use_case = IngestText(
            uow_factory=make_mem_uow_factory(),
            pattern_set_repository=_pattern_set_repository(),
            patterns=frozenset({"CPF_LABELED"}),
            text=_VALID_CPF_LABELED_TEXT,
        )

        graph = await use_case.execute()

        persons = [node for node in graph.nodes if isinstance(node, Person)]
        assert len(persons) == 1
        assert persons[0].cpf == _VALID_CPF_DIGITS
        assert persons[0].name is None

        text_sources = [node for node in graph.nodes if isinstance(node, TextSource)]
        assert len(text_sources) == 1
        assert graph.root_id == text_sources[0].id

        mention_edges = [
            edge for edge in graph.edges if isinstance(edge, PersonMentionedInText)
        ]
        assert len(mention_edges) == 1
        assert mention_edges[0].source_id == persons[0].id
        assert mention_edges[0].target_id == text_sources[0].id
        assert mention_edges[0].matched_field == "cpf"
        assert mention_edges[0].pattern_name is TextPatternName.CPF_LABELED

    @pytest.mark.asyncio
    async def test_persists_the_stub_and_text_provider_individually(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        mem_storage = make_mem_storage()
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = IngestText(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            pattern_set_repository=_pattern_set_repository(),
            patterns=frozenset({"CPF_LABELED"}),
            text=_VALID_CPF_LABELED_TEXT,
        )

        graph = await use_case.execute()

        person = next(node for node in graph.nodes if isinstance(node, Person))
        text_source = next(node for node in graph.nodes if isinstance(node, TextSource))

        assert person.id in mem_storage.nodes
        assert text_source.id in mem_storage.nodes
        assert graph.id in mem_storage.graphs


class TestIngestTextExistingEntity:
    @pytest.mark.asyncio
    async def test_links_to_the_existing_node_without_mutating_it(
        self,
        make_entity_revision: MakeEntityRevision,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        existing_person = Person(
            age_range="31 a 40 anos",
            birthdate=None,
            cpf=_VALID_CPF_DIGITS,
            name="Real Enriched Name",
            registration_date=None,
            registration_status=None,
        )
        mem_storage = make_mem_storage(
            nodes=[make_entity_revision(entity=existing_person)]
        )
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = IngestText(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            pattern_set_repository=_pattern_set_repository(),
            patterns=frozenset({"CPF_LABELED"}),
            text=_VALID_CPF_LABELED_TEXT,
        )

        graph = await use_case.execute()

        person = next(node for node in graph.nodes if isinstance(node, Person))

        assert person.name == "Real Enriched Name"
        assert len(mem_storage.nodes[existing_person.id]) == 1


class TestIngestTextNoMatch:
    @pytest.mark.asyncio
    async def test_raises_when_no_pattern_matches_anything(
        self, make_mem_uow_factory: MakeMemUoWFactory
    ) -> None:
        use_case = IngestText(
            uow_factory=make_mem_uow_factory(),
            pattern_set_repository=_pattern_set_repository(),
            patterns=frozenset({"brazilian_documents_v1"}),
            text="nothing relevant in here",
        )

        with pytest.raises(NoPatternMatchedError):
            await use_case.execute()

    @pytest.mark.asyncio
    async def test_persists_nothing_when_no_pattern_matches(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        mem_storage = make_mem_storage()
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = IngestText(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            pattern_set_repository=_pattern_set_repository(),
            patterns=frozenset({"brazilian_documents_v1"}),
            text="nothing relevant in here",
        )

        with pytest.raises(NoPatternMatchedError):
            await use_case.execute()

        assert not mem_storage.nodes
        assert not mem_storage.graphs


class TestIngestTextUnknownPatternName:
    @pytest.mark.asyncio
    async def test_raises_before_extracting_anything(
        self, make_mem_uow_factory: MakeMemUoWFactory
    ) -> None:
        use_case = IngestText(
            uow_factory=make_mem_uow_factory(),
            pattern_set_repository=_pattern_set_repository(),
            patterns=frozenset({"does_not_exist"}),
            text=_VALID_CPF_LABELED_TEXT,
        )

        with pytest.raises(UnknownPatternNameError):
            await use_case.execute()


class TestIngestTextOverlappingAtomicPatterns:
    @pytest.mark.asyncio
    async def test_two_patterns_matching_the_same_person_produce_two_mention_edges(
        self, make_mem_uow_factory: MakeMemUoWFactory
    ) -> None:
        use_case = IngestText(
            uow_factory=make_mem_uow_factory(),
            pattern_set_repository=_pattern_set_repository(),
            patterns=frozenset({"CPF_LOOSE", "CPF_LABELED"}),
            text=_VALID_CPF_LABELED_TEXT,
        )

        graph = await use_case.execute()

        mention_edges = [
            edge for edge in graph.edges if isinstance(edge, PersonMentionedInText)
        ]
        assert len(mention_edges) == 2

        found_pattern_names = {edge.pattern_name for edge in mention_edges}
        assert found_pattern_names == {
            TextPatternName.CPF_LOOSE,
            TextPatternName.CPF_LABELED,
        }

        persons = [node for node in graph.nodes if isinstance(node, Person)]
        assert len(persons) == 1


class TestIngestTextLoosePatternIsOptIn:
    @pytest.mark.asyncio
    async def test_bare_unlabeled_cpf_is_captured_when_cpf_loose_is_requested(
        self, make_mem_uow_factory: MakeMemUoWFactory
    ) -> None:
        use_case = IngestText(
            uow_factory=make_mem_uow_factory(),
            pattern_set_repository=_pattern_set_repository(),
            patterns=frozenset({"CPF_LOOSE"}),
            text=_VALID_CPF_DIGITS,
        )

        graph = await use_case.execute()

        persons = [node for node in graph.nodes if isinstance(node, Person)]
        assert len(persons) == 1

    @pytest.mark.asyncio
    async def test_bare_unlabeled_cpf_is_not_captured_by_cpf_labeled_alone(
        self, make_mem_uow_factory: MakeMemUoWFactory
    ) -> None:
        use_case = IngestText(
            uow_factory=make_mem_uow_factory(),
            pattern_set_repository=_pattern_set_repository(),
            patterns=frozenset({"CPF_LABELED"}),
            text=_VALID_CPF_DIGITS,
        )

        with pytest.raises(NoPatternMatchedError):
            await use_case.execute()
