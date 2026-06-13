from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

from osint_engine.domain.errors.entity_error import NotFoundEntityError
from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage
from osint_engine.infrastructure.persistence.mem.repositories.mem_edge_repository import (  # noqa: E501
    MemEdgeRepository,
)

if TYPE_CHECKING:
    from tests.conftest import MakeEdge, MakeMemStorage

# VALID CASES


@pytest.mark.asyncio
async def test_mem_edge_repo_find_returns_edge_when_edge_exists(
    make_edge: MakeEdge, make_mem_storage: MakeMemStorage
) -> None:
    edge = make_edge()
    mem_storage = make_mem_storage(edges=[edge])
    repo = MemEdgeRepository(mem_storage=mem_storage)

    found = await repo.find(edge_id=edge.id)

    assert found is edge


@pytest.mark.asyncio
async def test_mem_edge_repo_find_returns_none_when_edge_does_not_exist(
    make_edge: MakeEdge, make_mem_storage: MakeMemStorage
) -> None:
    edge = make_edge()
    mem_storage = make_mem_storage()
    repo = MemEdgeRepository(mem_storage=mem_storage)

    found = await repo.find(edge_id=edge.id)

    assert found is None


@pytest.mark.asyncio
async def test_mem_edge_repo_get_returns_edge_when_edge_exists(
    make_edge: MakeEdge, make_mem_storage: MakeMemStorage
) -> None:
    edge = make_edge()
    mem_storage = make_mem_storage(edges=[edge])
    repo = MemEdgeRepository(mem_storage=mem_storage)

    found = await repo.find(edge_id=edge.id)

    assert found is edge


@pytest.mark.asyncio
async def test_mem_edge_repo_save_persists_edge_correctly(
    make_edge: MakeEdge, make_mem_storage: MakeMemStorage
) -> None:
    edge = make_edge()
    mem_storage = make_mem_storage()
    repo = MemEdgeRepository(mem_storage=mem_storage)

    await repo.save(edge=edge)

    assert edge.id in mem_storage.edges


@pytest.mark.asyncio
async def test_mem_edge_repo_save_is_idempotent_and_does_not_overwrite(
    make_edge: MakeEdge,
) -> None:
    source_id = uuid4()
    target_id = uuid4()
    content = "test"

    edge_a = make_edge(source_id=source_id, target_id=target_id, content=content)
    edge_b = make_edge(source_id=source_id, target_id=target_id, content=content)

    assert edge_a.id == edge_b.id

    mem_storage = MemStorage(edges={edge_a.id: edge_a})
    repo = MemEdgeRepository(mem_storage=mem_storage)

    await repo.save(edge=edge_a)

    await repo.save(edge=edge_b)

    assert mem_storage.edges[edge_a.id] is edge_a

    assert mem_storage.edges[edge_a.id] is not edge_b

    assert mem_storage.edges[edge_b.id] is edge_a

    assert mem_storage.edges[edge_b.id] is not edge_b


@pytest.mark.asyncio
async def test_mem_edge_repo_save_many_persists_all_edges(
    make_edge: MakeEdge, make_mem_storage: MakeMemStorage
) -> None:
    edge_a = make_edge()
    edge_b = make_edge()
    mem_storage = make_mem_storage()
    repo = MemEdgeRepository(mem_storage=mem_storage)

    await repo.save_many(edges=frozenset({edge_a, edge_b}))

    assert mem_storage.edges[edge_a.id] is edge_a

    assert mem_storage.edges[edge_b.id] is edge_b


# INVALID CASES


@pytest.mark.asyncio
async def test_mem_edge_repo_get_raises_when_edge_does_not_exist(
    make_edge: MakeEdge, make_mem_storage: MakeMemStorage
) -> None:
    edge = make_edge()
    mem_storage = make_mem_storage()
    repo = MemEdgeRepository(mem_storage=mem_storage)

    with pytest.raises(NotFoundEntityError):
        await repo.get(edge_id=edge.id)
