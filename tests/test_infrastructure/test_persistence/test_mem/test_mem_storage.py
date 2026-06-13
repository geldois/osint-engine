from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import TYPE_CHECKING

import pytest

from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.domain.entities.bases.edge import Edge
    from osint_engine.domain.entities.bases.graph import Graph
    from osint_engine.domain.entities.bases.node import Node

# VALID CASES


def test_mem_storage_creates_empty_dicts_when_no_storages_are_injected() -> None:
    mem_storage = MemStorage(edges=None, graphs=None, nodes=None)

    assert not (mem_storage.edges and mem_storage.edges is None)

    assert not (mem_storage.graphs and mem_storage.graphs is None)

    assert not (mem_storage.nodes and mem_storage.nodes is None)


def test_mem_storage_references_storages_injected_during_instantiaton() -> None:
    edges: dict[UUID, Edge[UUID]] = {}
    graphs: dict[UUID, Graph] = {}
    nodes: dict[UUID, Node[UUID]] = {}

    mem_storage = MemStorage(edges=edges, graphs=graphs, nodes=nodes)

    assert mem_storage.edges is edges

    assert mem_storage.graphs is graphs

    assert mem_storage.nodes is nodes


# INVALID CASES


def test_mem_storage_instances_are_immutable() -> None:
    mem_storage = MemStorage()

    with pytest.raises(FrozenInstanceError):
        del mem_storage.edges

    with pytest.raises(FrozenInstanceError):
        del mem_storage.graphs

    with pytest.raises(FrozenInstanceError):
        del mem_storage.nodes
