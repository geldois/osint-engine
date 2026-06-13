from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from osint_engine.infrastructure.errors.uow_error import (
    AlreadyPreparedUoWError,
    NotPreparedUoWError,
)
from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage
from osint_engine.infrastructure.persistence.mem.mem_uow import MemUoW

if TYPE_CHECKING:
    from tests.conftest import MakeEdge, MakeGraph, MakeNode

# VALID CASES


@pytest.mark.asyncio
async def test_mem_uow_creates_and_deletes_infra_attributes_in_context_lifecycle() -> (
    None
):
    attributes = ("_snapshot", "edges", "graphs", "nodes")
    mem_storage = MemStorage()
    uow = MemUoW(mem_storage=mem_storage)

    for attribute in attributes:
        assert not hasattr(uow, attribute)

    async with uow:
        for attribute in attributes:
            assert hasattr(uow, attribute)

    for attribute in attributes:
        assert not hasattr(uow, attribute)


@pytest.mark.asyncio
async def test_mem_uow_commits_diffs_to_mem_storage_when_transaction_is_over(
    make_edge: MakeEdge, make_graph: MakeGraph, make_node: MakeNode
) -> None:
    edge = make_edge()
    node = make_node()
    graph = make_graph(edges=[edge], nodes=[node], root_id=node.id)
    mem_storage = MemStorage()
    uow = MemUoW(mem_storage=mem_storage)

    async with uow:
        await uow.edges.save(edge=edge)

        await uow.graphs.save(graph=graph)

        await uow.nodes.save(node=node)

    assert edge.id in mem_storage.edges

    assert graph.id in mem_storage.graphs

    assert node.id in mem_storage.nodes


@pytest.mark.asyncio
async def test_mem_uow_rolls_back_transaction_when_error_occurs(
    make_edge: MakeEdge, make_graph: MakeGraph, make_node: MakeNode
) -> None:
    edge = make_edge()
    node = make_node()
    graph = make_graph(edges=[edge], nodes=[node], root_id=node.id)
    mem_storage = MemStorage()
    uow = MemUoW(mem_storage=mem_storage)

    async def run_transaction_with_error() -> None:
        async with uow:
            await uow.edges.save(edge=edge)

            await uow.graphs.save(graph=graph)

            await uow.nodes.save(node=node)

            raise RuntimeError

    with pytest.raises(RuntimeError):
        await run_transaction_with_error()

    assert edge.id not in mem_storage.edges

    assert graph.id not in mem_storage.graphs

    assert node.id not in mem_storage.nodes


# INVALID CASES


@pytest.mark.asyncio
async def test_mem_uow_raises_when_is_double_prepared_or_finished() -> None:
    mem_storage = MemStorage()
    uow = MemUoW(mem_storage=mem_storage)

    with pytest.raises(AlreadyPreparedUoWError):
        async with uow:
            await uow._prepare()  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]

    with pytest.raises(NotPreparedUoWError):
        async with uow:
            await uow._finish()  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
