from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from osint_engine.infrastructure.errors.uow_error import (
    UoWAlreadyPreparedError,
    UoWNotPreparedError,
)
from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage
from osint_engine.infrastructure.persistence.mem.mem_uow import MemUoW

if TYPE_CHECKING:
    from tests.conftest import MakeFakeEdge, MakeFakeNode, MakeGraph, MakeUser


class TestMemUoWContextLifecycle:
    @pytest.mark.asyncio
    async def test_attributes_exist_inside_context_and_are_removed_on_exit(
        self,
    ) -> None:
        attributes = ("_snapshot", "edges", "graphs", "nodes", "users")
        mem_storage = MemStorage()
        uow = MemUoW(mem_storage=mem_storage)

        for attribute in attributes:
            assert not hasattr(uow, attribute)

        async with uow:
            for attribute in attributes:
                assert hasattr(uow, attribute)

        for attribute in attributes:
            assert not hasattr(uow, attribute)


class TestMemUoWCommit:
    @pytest.mark.asyncio
    async def test_changes_are_flushed_to_storage_on_exit(
        self,
        make_fake_edge: MakeFakeEdge,
        make_graph: MakeGraph,
        make_fake_node: MakeFakeNode,
        make_user: MakeUser,
    ) -> None:
        node_a = make_fake_node()
        node_b = make_fake_node()
        edge = make_fake_edge(source_id=node_a.id, target_id=node_b.id)
        graph = make_graph(edges=[edge], nodes=[node_a, node_b], root_id=node_a.id)
        user = make_user()
        mem_storage = MemStorage()
        uow = MemUoW(mem_storage=mem_storage)

        async with uow:
            await uow.edges.save(edge=edge)

            await uow.graphs.save(graph=graph)

            await uow.nodes.save(node=node_a)

            await uow.nodes.save(node=node_b)

            await uow.users.save(user=user)

        assert edge.id in mem_storage.edges

        assert graph.id in mem_storage.graphs

        assert node_a.id in mem_storage.nodes

        assert node_b.id in mem_storage.nodes

        assert user.username in mem_storage.users


class TestMemUoWRollback:
    @pytest.mark.asyncio
    async def test_changes_are_not_flushed_when_exception_propagates(
        self,
        make_fake_edge: MakeFakeEdge,
        make_graph: MakeGraph,
        make_fake_node: MakeFakeNode,
        make_user: MakeUser,
    ) -> None:
        node_a = make_fake_node()
        node_b = make_fake_node()
        edge = make_fake_edge(source_id=node_a.id, target_id=node_b.id)
        graph = make_graph(edges=[edge], nodes=[node_a, node_b], root_id=node_a.id)
        user = make_user()
        mem_storage = MemStorage()
        uow = MemUoW(mem_storage=mem_storage)

        async def run_transaction_with_error() -> None:
            async with uow:
                await uow.edges.save(edge=edge)

                await uow.graphs.save(graph=graph)

                await uow.nodes.save(node=node_a)

                await uow.nodes.save(node=node_b)

                await uow.users.save(user=user)

                raise RuntimeError

        with pytest.raises(RuntimeError):
            await run_transaction_with_error()

        assert edge.id not in mem_storage.edges

        assert graph.id not in mem_storage.graphs

        assert node_a.id not in mem_storage.nodes

        assert node_b.id not in mem_storage.nodes

        assert user.username not in mem_storage.users


class TestMemUoWValidation:
    @pytest.mark.asyncio
    async def test_raises_when_prepared_twice_or_finished_unmatched(self) -> None:
        mem_storage = MemStorage()
        uow = MemUoW(mem_storage=mem_storage)

        with pytest.raises(UoWAlreadyPreparedError):
            async with uow:
                await uow._prepare()  # pyright: ignore[reportPrivateUsage]

        with pytest.raises(UoWNotPreparedError):
            async with uow:
                await uow._finish()  # pyright: ignore[reportPrivateUsage]
