from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import pytest

from tests.fakes.fetchers import (
    FakeCEISFetcher,
    FakeCNEPFetcher,
    FakeCNPJFetcher,
    FakeCPFFetcher,
)

if TYPE_CHECKING:
    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.domain.entities.bases.graph import Graph
    from osint_engine.infrastructure.persistence.mem.mem_uow import MemUoW
    from tests.conftest import MakeEntityRevision, MakeGraph, MakeMemUoW

type MakeFakeCEISFetcher = Callable[..., FakeCEISFetcher]
type MakeFakeCNEPFetcher = Callable[..., FakeCNEPFetcher]
type MakeFakeCNPJFetcher = Callable[..., FakeCNPJFetcher]
type MakeFakeCPFFetcher = Callable[..., FakeCPFFetcher]
type MakeMemUoWFactory = Callable[..., MakeMemUoW]


@pytest.fixture
def make_mem_uow_factory(make_mem_uow: MakeMemUoW) -> MakeMemUoWFactory:

    def mem_uow_factory(mem_uow: MemUoW | None = None) -> MakeMemUoW:
        mem_uow = mem_uow if mem_uow is not None else make_mem_uow()

        return lambda: mem_uow

    return mem_uow_factory


@pytest.fixture
def make_fake_cnpj_fetcher(
    make_entity_revision: MakeEntityRevision, make_graph: MakeGraph
) -> MakeFakeCNPJFetcher:

    def fake_cnpj_fetcher(
        *, revision: EntityRevision[Graph] | None = None
    ) -> FakeCNPJFetcher:
        return FakeCNPJFetcher(
            revision=revision
            if revision is not None
            else make_entity_revision(entity=make_graph())
        )

    return fake_cnpj_fetcher


@pytest.fixture
def make_fake_cpf_fetcher(
    make_entity_revision: MakeEntityRevision, make_graph: MakeGraph
) -> MakeFakeCPFFetcher:

    def fake_cpf_fetcher(
        *, revision: EntityRevision[Graph] | None = None
    ) -> FakeCPFFetcher:
        return FakeCPFFetcher(
            revision=revision
            if revision is not None
            else make_entity_revision(entity=make_graph())
        )

    return fake_cpf_fetcher


@pytest.fixture
def make_fake_ceis_fetcher(
    make_entity_revision: MakeEntityRevision, make_graph: MakeGraph
) -> MakeFakeCEISFetcher:

    def fake_ceis_fetcher(
        *, revision: EntityRevision[Graph] | None = None
    ) -> FakeCEISFetcher:
        return FakeCEISFetcher(
            revision=revision
            if revision is not None
            else make_entity_revision(entity=make_graph())
        )

    return fake_ceis_fetcher


@pytest.fixture
def make_fake_cnep_fetcher(
    make_entity_revision: MakeEntityRevision, make_graph: MakeGraph
) -> MakeFakeCNEPFetcher:

    def fake_cnep_fetcher(
        *, revision: EntityRevision[Graph] | None = None
    ) -> FakeCNEPFetcher:
        return FakeCNEPFetcher(
            revision=revision
            if revision is not None
            else make_entity_revision(entity=make_graph())
        )

    return fake_cnep_fetcher
