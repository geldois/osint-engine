from __future__ import annotations

from collections import defaultdict
from dataclasses import FrozenInstanceError
from typing import TYPE_CHECKING

import pytest

from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.application.auth.user import User
    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.domain.entities.bases.edge import Edge
    from osint_engine.domain.entities.bases.graph import Graph
    from osint_engine.domain.entities.bases.node import Node


class TestMemStorageInitialization:
    def test_creates_empty_dicts_when_no_storages_are_injected(self) -> None:
        mem_storage = MemStorage(edges=None, graphs=None, nodes=None, users=None)

        assert not (mem_storage.edges and mem_storage.edges is None)

        assert not (mem_storage.graphs and mem_storage.graphs is None)

        assert not (mem_storage.nodes and mem_storage.nodes is None)

        assert not (mem_storage.users and mem_storage.users is None)

    def test_references_storages_injected_during_instantiaton(self) -> None:
        edges: defaultdict[UUID, dict[UUID, EntityRevision[Edge[UUID, UUID, UUID]]]] = (
            defaultdict(dict)
        )
        graphs: defaultdict[UUID, dict[UUID, EntityRevision[Graph]]] = defaultdict(dict)
        nodes: defaultdict[UUID, dict[UUID, EntityRevision[Node[UUID]]]] = defaultdict(
            dict
        )
        users: dict[str, User] = {}

        mem_storage = MemStorage(edges=edges, graphs=graphs, nodes=nodes, users=users)

        assert mem_storage.edges is edges

        assert mem_storage.graphs is graphs

        assert mem_storage.nodes is nodes

        assert mem_storage.users is users


class TestMemStorageProperties:
    def test_rebinding_an_attribute_is_rejected(self) -> None:
        mem_storage = MemStorage()

        with pytest.raises(FrozenInstanceError):
            mem_storage.edges = mem_storage.edges

    def test_instances_are_immutable(self) -> None:
        mem_storage = MemStorage()

        with pytest.raises(FrozenInstanceError):
            del mem_storage.edges

        with pytest.raises(FrozenInstanceError):
            del mem_storage.graphs

        with pytest.raises(FrozenInstanceError):
            del mem_storage.nodes

        with pytest.raises(FrozenInstanceError):
            del mem_storage.users
