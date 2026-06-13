from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from osint_engine.domain.errors.entity_error import NotFoundEntityError
from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage
from osint_engine.infrastructure.persistence.mem.repositories.mem_graph_repository import (  # noqa: E501
    MemGraphRepository,
)

if TYPE_CHECKING:
    from tests.conftest import MakeEdge, MakeGraph, MakeMemStorage, MakeNode

# VALID CASES


@pytest.mark.asyncio
async def test_mem_graph_repo_find_returns_graph_when_graph_exists(
    make_graph: MakeGraph, make_mem_storage: MakeMemStorage
) -> None:
    graph = make_graph()
    mem_storage = make_mem_storage(graphs=[graph])
    repo = MemGraphRepository(mem_storage=mem_storage)

    found = await repo.find(graph_id=graph.id)

    assert found is graph


@pytest.mark.asyncio
async def test_mem_graph_repo_find_returns_none_when_graph_does_not_exist(
    make_graph: MakeGraph, make_mem_storage: MakeMemStorage
) -> None:
    graph = make_graph()
    mem_storage = make_mem_storage()
    repo = MemGraphRepository(mem_storage=mem_storage)

    found = await repo.find(graph_id=graph.id)

    assert found is None


@pytest.mark.asyncio
async def test_mem_graph_repo_get_returns_graph_when_graph_exists(
    make_graph: MakeGraph, make_mem_storage: MakeMemStorage
) -> None:
    graph = make_graph()
    mem_storage = make_mem_storage(graphs=[graph])
    repo = MemGraphRepository(mem_storage=mem_storage)

    found = await repo.find(graph_id=graph.id)

    assert found is graph


@pytest.mark.asyncio
async def test_mem_graph_repo_save_persists_graph_correctly(
    make_graph: MakeGraph, make_mem_storage: MakeMemStorage
) -> None:
    graph = make_graph()
    mem_storage = make_mem_storage()
    repo = MemGraphRepository(mem_storage=mem_storage)

    await repo.save(graph=graph)

    assert graph.id in mem_storage.graphs


@pytest.mark.asyncio
async def test_mem_graph_repo_save_is_idempotent_and_does_not_overwrite(
    make_edge: MakeEdge, make_graph: MakeGraph, make_node: MakeNode
) -> None:
    edge = make_edge()
    node = make_node()

    graph_a = make_graph(edges=[edge], nodes=[node], root_id=node.id)
    graph_b = make_graph(edges=[edge], nodes=[node], root_id=node.id)

    assert graph_a.id == graph_b.id

    mem_storage = MemStorage(graphs={graph_a.id: graph_a})
    repo = MemGraphRepository(mem_storage=mem_storage)

    await repo.save(graph=graph_a)

    await repo.save(graph=graph_b)

    assert mem_storage.graphs[graph_a.id] is graph_a

    assert mem_storage.graphs[graph_a.id] is not graph_b

    assert mem_storage.graphs[graph_b.id] is graph_a

    assert mem_storage.graphs[graph_b.id] is not graph_b


@pytest.mark.asyncio
async def test_mem_graph_repo_save_many_persists_all_graphs(
    make_graph: MakeGraph, make_mem_storage: MakeMemStorage
) -> None:
    graph_a = make_graph()
    graph_b = make_graph()
    mem_storage = make_mem_storage()
    repo = MemGraphRepository(mem_storage=mem_storage)

    await repo.save_many(graphs=frozenset({graph_a, graph_b}))

    assert mem_storage.graphs[graph_a.id] is graph_a

    assert mem_storage.graphs[graph_b.id] is graph_b


# INVALID CASES


@pytest.mark.asyncio
async def test_mem_graph_repo_get_raises_when_graph_does_not_exist(
    make_graph: MakeGraph, make_mem_storage: MakeMemStorage
) -> None:
    graph = make_graph()
    mem_storage = make_mem_storage()
    repo = MemGraphRepository(mem_storage=mem_storage)

    with pytest.raises(NotFoundEntityError):
        await repo.get(graph_id=graph.id)
