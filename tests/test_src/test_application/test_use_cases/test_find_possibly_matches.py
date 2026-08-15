from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from osint_engine.application.use_cases.matching.find_possibly_matches import (
    FindPossiblyMatches,
)
from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.edges.possibly_matches import PossiblyMatches
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.person import Person

if TYPE_CHECKING:
    from tests.conftest import (
        MakeEntityRevision,
        MakeMemStorage,
        MakeMemUoW,
    )
    from tests.test_src.test_application.conftest import MakeMemUoWFactory


def _make_person(*, cpf: str, name: str = "FULANO DE TAL") -> Person:
    return Person(
        age_range="Entre 41 a 50 anos",
        birthdate=None,
        cpf=cpf,
        name=name,
        registration_date=None,
        registration_status=None,
    )


def _make_company(*, cnpj: str = "33754482000124") -> Company:
    return Company(
        activity_start_date=None,
        cnpj=cnpj,
        is_headquarters=None,
        legal_name="EMPRESA LTDA",
        legal_nature=None,
        registration_status=None,
        registration_status_date=None,
        registration_status_reason=None,
        share_capital=None,
        size_category=None,
        trade_name=None,
    )


def _make_graph(*, node: Person | Company) -> Graph:
    return Graph(edges=frozenset(), nodes=frozenset({node}), root_id=node.id)


def _find_possibly_matches(
    *,
    graph: Graph,
    make_entity_revision: MakeEntityRevision,
    make_mem_storage: MakeMemStorage,
    make_mem_uow: MakeMemUoW,
    make_mem_uow_factory: MakeMemUoWFactory,
    storage_nodes: list[Person | Company],
) -> FindPossiblyMatches:
    revisions = [make_entity_revision(entity=node) for node in storage_nodes]
    mem_storage = make_mem_storage(nodes=revisions)
    mem_uow = make_mem_uow(mem_storage=mem_storage)

    return FindPossiblyMatches(
        uow_factory=make_mem_uow_factory(mem_uow=mem_uow), graph=graph
    )


class TestFindPossiblyMatches:
    @pytest.mark.asyncio
    async def test_links_persons_whose_masked_cpf_overlaps(
        self,
        make_entity_revision: MakeEntityRevision,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        person = _make_person(cpf="***128734**")
        candidate = _make_person(cpf="1**128734**")
        use_case = _find_possibly_matches(
            graph=_make_graph(node=person),
            make_mem_storage=make_mem_storage,
            make_entity_revision=make_entity_revision,
            make_mem_uow=make_mem_uow,
            make_mem_uow_factory=make_mem_uow_factory,
            storage_nodes=[candidate],
        )

        result = await use_case.execute()

        assert result is not None
        assert len(result.edges) == 1

        match = next(iter(result.edges))

        assert isinstance(match, PossiblyMatches)
        assert {match.source_id, match.target_id} == {person.id, candidate.id}
        assert match.confidence == Decimal(6) / Decimal(11)

    @pytest.mark.asyncio
    async def test_returns_none_when_no_person_candidate_exists(
        self,
        make_entity_revision: MakeEntityRevision,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        person = _make_person(cpf="***128734**")
        use_case = _find_possibly_matches(
            graph=_make_graph(node=person),
            make_mem_storage=make_mem_storage,
            make_entity_revision=make_entity_revision,
            make_mem_uow=make_mem_uow,
            make_mem_uow_factory=make_mem_uow_factory,
            storage_nodes=[],
        )

        assert await use_case.execute() is None

    @pytest.mark.asyncio
    async def test_returns_none_for_an_insufficient_overlap(
        self,
        make_entity_revision: MakeEntityRevision,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        person = _make_person(cpf="***128734**")
        candidate = _make_person(cpf="***128*****")
        use_case = _find_possibly_matches(
            graph=_make_graph(node=person),
            make_mem_storage=make_mem_storage,
            make_entity_revision=make_entity_revision,
            make_mem_uow=make_mem_uow,
            make_mem_uow_factory=make_mem_uow_factory,
            storage_nodes=[candidate],
        )

        assert await use_case.execute() is None

    @pytest.mark.asyncio
    async def test_returns_none_for_a_diverging_document(
        self,
        make_entity_revision: MakeEntityRevision,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        person = _make_person(cpf="***128734**")
        candidate = _make_person(cpf="***999999**")
        use_case = _find_possibly_matches(
            graph=_make_graph(node=person),
            make_mem_storage=make_mem_storage,
            make_entity_revision=make_entity_revision,
            make_mem_uow=make_mem_uow,
            make_mem_uow_factory=make_mem_uow_factory,
            storage_nodes=[candidate],
        )

        assert await use_case.execute() is None

    @pytest.mark.asyncio
    async def test_never_compares_a_company(
        self,
        make_entity_revision: MakeEntityRevision,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        company = _make_company()
        person = _make_person(cpf="***128734**")
        use_case = _find_possibly_matches(
            graph=_make_graph(node=company),
            make_mem_storage=make_mem_storage,
            make_entity_revision=make_entity_revision,
            make_mem_uow=make_mem_uow,
            make_mem_uow_factory=make_mem_uow_factory,
            storage_nodes=[person],
        )

        assert await use_case.execute() is None

    @pytest.mark.asyncio
    async def test_skips_the_node_itself(
        self,
        make_entity_revision: MakeEntityRevision,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        person = _make_person(cpf="***128734**")
        use_case = _find_possibly_matches(
            graph=_make_graph(node=person),
            make_mem_storage=make_mem_storage,
            make_entity_revision=make_entity_revision,
            make_mem_uow=make_mem_uow,
            make_mem_uow_factory=make_mem_uow_factory,
            storage_nodes=[person],
        )

        assert await use_case.execute() is None

    @pytest.mark.asyncio
    async def test_root_id_is_the_smallest_matched_node_id_across_runs(
        self,
        make_entity_revision: MakeEntityRevision,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        person = _make_person(cpf="***128734**")
        first_candidate = _make_person(cpf="1**128734**")
        second_candidate = _make_person(cpf="*****8734**")
        third_candidate = _make_person(cpf="***1287**4*")
        use_case = _find_possibly_matches(
            graph=_make_graph(node=person),
            make_mem_storage=make_mem_storage,
            make_entity_revision=make_entity_revision,
            make_mem_uow=make_mem_uow,
            make_mem_uow_factory=make_mem_uow_factory,
            storage_nodes=[first_candidate, second_candidate, third_candidate],
        )

        first_run = await use_case.execute()
        second_run = await use_case.execute()

        assert first_run is not None
        assert second_run is not None
        assert len(first_run.nodes) == 4
        assert first_run.root_id == min(node.id for node in first_run.nodes)
        assert first_run.id == second_run.id

    @pytest.mark.asyncio
    async def test_persists_the_match_edges(
        self,
        make_entity_revision: MakeEntityRevision,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        person = _make_person(cpf="***128734**")
        candidate = _make_person(cpf="1**128734**")
        revisions = [
            make_entity_revision(entity=candidate),
            make_entity_revision(entity=person),
        ]
        mem_storage = make_mem_storage(nodes=revisions)
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        use_case = FindPossiblyMatches(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            graph=_make_graph(node=person),
        )

        result = await use_case.execute()

        assert result is not None

        match = next(iter(result.edges))

        assert match.id in mem_storage.edges
        assert match.content_id in mem_storage.edges[match.id]

    @pytest.mark.asyncio
    async def test_legacy_corrupted_person_in_storage_does_not_crash_or_match(
        self,
        make_entity_revision: MakeEntityRevision,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        person = _make_person(cpf="***128734**")
        legacy = _make_person(cpf="***999999**")
        object.__setattr__(legacy, "cpf", "123X45678909")
        use_case = _find_possibly_matches(
            graph=_make_graph(node=person),
            make_mem_storage=make_mem_storage,
            make_entity_revision=make_entity_revision,
            make_mem_uow=make_mem_uow,
            make_mem_uow_factory=make_mem_uow_factory,
            storage_nodes=[legacy],
        )

        assert await use_case.execute() is None
