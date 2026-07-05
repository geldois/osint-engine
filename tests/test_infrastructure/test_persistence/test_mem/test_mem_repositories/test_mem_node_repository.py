from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from osint_engine.domain.errors.entity_error import NotFoundEntityError
from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage
from osint_engine.infrastructure.persistence.mem.repositories.mem_node_repository import (  # noqa: E501
    MemNodeRepository,
)

if TYPE_CHECKING:
    from tests.conftest import MakeMemStorage, MakeNode


class TestMemNodeRepositoryFind:
    @pytest.mark.asyncio
    async def test_find_returns_node_when_node_exists(
        self, make_node: MakeNode, make_mem_storage: MakeMemStorage
    ) -> None:
        node = make_node()
        mem_storage = make_mem_storage(nodes=[node])
        repo = MemNodeRepository(mem_storage=mem_storage)

        found = await repo.find(node_id=node.id)

        assert found is node

    @pytest.mark.asyncio
    async def test_find_returns_none_when_node_does_not_exist(
        self, make_node: MakeNode, make_mem_storage: MakeMemStorage
    ) -> None:
        node = make_node()
        mem_storage = make_mem_storage()
        repo = MemNodeRepository(mem_storage=mem_storage)

        found = await repo.find(node_id=node.id)

        assert found is None


class TestMemNodeRepositoryGet:
    @pytest.mark.asyncio
    async def test_get_returns_node_when_node_exists(
        self, make_node: MakeNode, make_mem_storage: MakeMemStorage
    ) -> None:
        node = make_node()
        mem_storage = make_mem_storage(nodes=[node])
        repo = MemNodeRepository(mem_storage=mem_storage)

        found = await repo.find(node_id=node.id)

        assert found is node

    @pytest.mark.asyncio
    async def test_get_raises_when_node_does_not_exist(
        self, make_node: MakeNode, make_mem_storage: MakeMemStorage
    ) -> None:
        node = make_node()
        mem_storage = make_mem_storage()
        repo = MemNodeRepository(mem_storage=mem_storage)

        with pytest.raises(NotFoundEntityError):
            await repo.get(node_id=node.id)


class TestMemNodeRepositorySave:
    @pytest.mark.asyncio
    async def test_save_persists_node_correctly(
        self, make_node: MakeNode, make_mem_storage: MakeMemStorage
    ) -> None:
        node = make_node()
        mem_storage = make_mem_storage()
        repo = MemNodeRepository(mem_storage=mem_storage)

        await repo.save(node=node)

        assert node.id in mem_storage.nodes

    @pytest.mark.asyncio
    async def test_save_is_idempotent_and_does_not_overwrite(
        self, make_node: MakeNode
    ) -> None:
        content = "test"

        node_a = make_node(content=content)
        node_b = make_node(content=content)

        assert node_a.id == node_b.id

        mem_storage = MemStorage(nodes={node_a.id: node_a})
        repo = MemNodeRepository(mem_storage=mem_storage)

        await repo.save(node=node_a)

        await repo.save(node=node_b)

        assert mem_storage.nodes[node_a.id] is node_a

        assert mem_storage.nodes[node_a.id] is not node_b

        assert mem_storage.nodes[node_b.id] is node_a

        assert mem_storage.nodes[node_b.id] is not node_b

    @pytest.mark.asyncio
    async def test_save_many_persists_all_nodes(
        self, make_node: MakeNode, make_mem_storage: MakeMemStorage
    ) -> None:
        node_a = make_node()
        node_b = make_node()
        mem_storage = make_mem_storage()
        repo = MemNodeRepository(mem_storage=mem_storage)

        await repo.save_many(nodes=frozenset({node_a, node_b}))

        assert mem_storage.nodes[node_a.id] is node_a

        assert mem_storage.nodes[node_b.id] is node_b
