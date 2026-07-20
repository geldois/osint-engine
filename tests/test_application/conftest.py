from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import pytest

from tests.fakes.fetchers import FakeCNEPFetcher, FakeCNPJFetcher

if TYPE_CHECKING:
    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.domain.entities.bases.graph import Graph
    from osint_engine.infrastructure.persistence.mem.mem_uow import MemUoW
    from tests.conftest import MakeEntityRevision, MakeGraph, MakeMemUoW

type MakeFakeCNEPFetcher = Callable[..., FakeCNEPFetcher]
type MakeFakeCNPJFetcher = Callable[..., FakeCNPJFetcher]
type MakeMemUoWFactory = Callable[..., MakeMemUoW]


@pytest.fixture
def make_mem_uow_factory(make_mem_uow: MakeMemUoW) -> MakeMemUoWFactory:
    """
    *,
    mem_uow: MemUoW | None = None
    """

    def mem_uow_factory(mem_uow: MemUoW | None = None) -> MakeMemUoW:
        mem_uow = mem_uow if mem_uow is not None else make_mem_uow()

        return lambda: mem_uow

    return mem_uow_factory


@pytest.fixture
def make_fake_cnpj_fetcher(
    make_entity_revision: MakeEntityRevision, make_graph: MakeGraph
) -> MakeFakeCNPJFetcher:
    """
    *,
    revision: EntityRevision[Graph] | None = None
    """

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
def make_fake_cnep_fetcher(
    make_entity_revision: MakeEntityRevision, make_graph: MakeGraph
) -> MakeFakeCNEPFetcher:
    """
    *,
    revision: EntityRevision[Graph] | None = None
    """

    def fake_cnep_fetcher(
        *, revision: EntityRevision[Graph] | None = None
    ) -> FakeCNEPFetcher:
        return FakeCNEPFetcher(
            revision=revision
            if revision is not None
            else make_entity_revision(entity=make_graph())
        )

    return fake_cnep_fetcher
