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


class TestMemGraphRepositoryFind:
    @pytest.mark.asyncio
    async def test_find_returns_graph_when_graph_exists(
        self, make_graph: MakeGraph, make_mem_storage: MakeMemStorage
    ) -> None:
        graph = make_graph()
        mem_storage = make_mem_storage(graphs=[graph])
        repo = MemGraphRepository(mem_storage=mem_storage)

        found = await repo.find(graph_id=graph.id)

        assert found is graph

    @pytest.mark.asyncio
    async def test_find_returns_none_when_graph_does_not_exist(
        self, make_graph: MakeGraph, make_mem_storage: MakeMemStorage
    ) -> None:
        graph = make_graph()
        mem_storage = make_mem_storage()
        repo = MemGraphRepository(mem_storage=mem_storage)

        found = await repo.find(graph_id=graph.id)

        assert found is None


class TestMemGraphRepositoryGet:
    @pytest.mark.asyncio
    async def test_get_returns_graph_when_graph_exists(
        self, make_graph: MakeGraph, make_mem_storage: MakeMemStorage
    ) -> None:
        graph = make_graph()
        mem_storage = make_mem_storage(graphs=[graph])
        repo = MemGraphRepository(mem_storage=mem_storage)

        found = await repo.find(graph_id=graph.id)

        assert found is graph

    @pytest.mark.asyncio
    async def test_get_raises_when_graph_does_not_exist(
        self, make_graph: MakeGraph, make_mem_storage: MakeMemStorage
    ) -> None:
        graph = make_graph()
        mem_storage = make_mem_storage()
        repo = MemGraphRepository(mem_storage=mem_storage)

        with pytest.raises(NotFoundEntityError):
            await repo.get(graph_id=graph.id)


class TestMemGraphRepositorySave:
    @pytest.mark.asyncio
    async def test_save_persists_graph_correctly(
        self, make_graph: MakeGraph, make_mem_storage: MakeMemStorage
    ) -> None:
        graph = make_graph()
        mem_storage = make_mem_storage()
        repo = MemGraphRepository(mem_storage=mem_storage)

        await repo.save(graph=graph)

        assert graph.id in mem_storage.graphs

    @pytest.mark.asyncio
    async def test_save_is_idempotent_and_does_not_overwrite(
        self, make_edge: MakeEdge, make_graph: MakeGraph, make_node: MakeNode
    ) -> None:
        node_a = make_node()
        node_b = make_node()
        edge = make_edge(source_id=node_a.id, target_id=node_b.id)

        graph_a = make_graph(edges=[edge], nodes=[node_a, node_b], root_id=node_a.id)
        graph_b = make_graph(edges=[edge], nodes=[node_a, node_b], root_id=node_a.id)

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
    async def test_save_many_persists_all_graphs(
        self, make_graph: MakeGraph, make_mem_storage: MakeMemStorage
    ) -> None:
        graph_a = make_graph()
        graph_b = make_graph()
        mem_storage = make_mem_storage()
        repo = MemGraphRepository(mem_storage=mem_storage)

        await repo.save_many(graphs=frozenset({graph_a, graph_b}))

        assert mem_storage.graphs[graph_a.id] is graph_a

        assert mem_storage.graphs[graph_b.id] is graph_b
