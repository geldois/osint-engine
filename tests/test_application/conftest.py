from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import pytest

from osint_engine.infrastructure.persistence.mem.mem_uow import MemUoW
from tests.fakes.fetchers import FakeCNPJFetcher

if TYPE_CHECKING:
    from osint_engine.domain.entities.bases.graph import Graph
    from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage
    from tests.conftest import MakeGraph, MakeMemStorage

type MakeFakeCNPJFetcher = Callable[..., FakeCNPJFetcher]
type MakeMemUoW = Callable[..., MemUoW]
type MakeMemUoWFactory = Callable[..., MakeMemUoW]


@pytest.fixture
def make_mem_uow(make_mem_storage: MakeMemStorage) -> MakeMemUoW:
    """
    *,
    mem_storage: MemStorage | None = None
    """

    def mem_uow(*, mem_storage: MemStorage | None = None) -> MemUoW:
        storage = mem_storage if mem_storage is not None else make_mem_storage()

        return MemUoW(mem_storage=storage)

    return mem_uow


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
def make_fake_cnpj_fetcher(make_graph: MakeGraph) -> MakeFakeCNPJFetcher:
    """
    *,
    graph: Graph | None = None
    """

    def fake_cnpj_fetcher(*, graph: Graph | None = None) -> FakeCNPJFetcher:
        return FakeCNPJFetcher(graph=graph if graph is not None else make_graph())

    return fake_cnpj_fetcher
