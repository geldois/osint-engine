from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from osint_engine.infrastructure.errors.uow_error import (
    UoWAlreadyPreparedError,
    UoWNotPreparedError,
)

if TYPE_CHECKING:
    from tests.conftest import (
        MakeEntityRevision,
        MakeFakeEdge,
        MakeFakeNode,
        MakeGraph,
        MakeMemStorage,
        MakeMemUoW,
        MakeUser,
    )

_LIFECYCLE_ATTRIBUTES = (
    "_snapshot",
    "edges",
    "external_credentials",
    "graphs",
    "nodes",
    "users",
)


class TestMemUoWContextLifecycle:
    @pytest.mark.asyncio
    async def test_attributes_exist_inside_context_and_are_removed_on_exit(
        self, make_mem_uow: MakeMemUoW
    ) -> None:
        uow = make_mem_uow()

        for attribute in _LIFECYCLE_ATTRIBUTES:
            assert not hasattr(uow, attribute)

        async with uow:
            for attribute in _LIFECYCLE_ATTRIBUTES:
                assert hasattr(uow, attribute)

        for attribute in _LIFECYCLE_ATTRIBUTES:
            assert not hasattr(uow, attribute)


class TestMemUoWCommit:
    @pytest.mark.asyncio
    async def test_changes_are_flushed_to_storage_on_exit(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_edge: MakeFakeEdge,
        make_graph: MakeGraph,
        make_fake_node: MakeFakeNode,
        make_user: MakeUser,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
    ) -> None:
        node_a = make_fake_node()
        node_b = make_fake_node()
        edge = make_fake_edge(source_id=node_a.id, target_id=node_b.id)
        graph = make_graph(edges=[edge], nodes=[node_a, node_b], root_id=node_a.id)
        user = make_user()
        mem_storage = make_mem_storage()
        uow = make_mem_uow(mem_storage=mem_storage)

        async with uow:
            await uow.edges.merge(revision=make_entity_revision(entity=edge))
            await uow.graphs.merge(revision=make_entity_revision(entity=graph))
            await uow.nodes.merge(revision=make_entity_revision(entity=node_a))
            await uow.nodes.merge(revision=make_entity_revision(entity=node_b))
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
        make_entity_revision: MakeEntityRevision,
        make_fake_edge: MakeFakeEdge,
        make_graph: MakeGraph,
        make_fake_node: MakeFakeNode,
        make_user: MakeUser,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
    ) -> None:
        node_a = make_fake_node()
        node_b = make_fake_node()
        edge = make_fake_edge(source_id=node_a.id, target_id=node_b.id)
        graph = make_graph(edges=[edge], nodes=[node_a, node_b], root_id=node_a.id)
        user = make_user()
        mem_storage = make_mem_storage()
        uow = make_mem_uow(mem_storage=mem_storage)

        async def run_transaction_with_error() -> None:
            async with uow:
                await uow.edges.merge(revision=make_entity_revision(entity=edge))
                await uow.graphs.merge(revision=make_entity_revision(entity=graph))
                await uow.nodes.merge(revision=make_entity_revision(entity=node_a))
                await uow.nodes.merge(revision=make_entity_revision(entity=node_b))
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
    async def test_raises_when_prepared_twice_or_finished_unmatched(
        self, make_mem_uow: MakeMemUoW
    ) -> None:
        uow = make_mem_uow()

        with pytest.raises(UoWAlreadyPreparedError) as already_prepared:
            async with uow:
                await uow._prepare()  # pyright: ignore[reportPrivateUsage]

        assert "MemUoW" in str(already_prepared.value)

        with pytest.raises(UoWNotPreparedError) as not_prepared:
            async with uow:
                await uow._finish()  # pyright: ignore[reportPrivateUsage]

        assert "MemUoW" in str(not_prepared.value)
