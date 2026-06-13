from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.entities.entity import Entity
from osint_engine.domain.errors.graph_error import (
    HasNoNodesGraphError,
    RootNotInNodesGraphError,
)

if TYPE_CHECKING:
    from tests.conftest import MakeNode

# VALID CASES


def test_graph_inherits_directly_from_entity() -> None:
    bases = Graph.__bases__

    assert Entity in bases

    assert Edge not in bases

    assert Node not in bases


def test_graph_inner_storages_are_frozenset() -> None:
    annotations = Graph.__annotations__
    contract = "frozenset"

    assert annotations["edges"].startswith(contract)

    assert annotations["nodes"].startswith(contract)


def test_graph_inner_storages_runtime_types_are_frozenset(make_node: MakeNode) -> None:
    node = make_node()

    graph = Graph(edges=frozenset(), nodes=frozenset({node}), root_id=node.id)

    assert isinstance(graph.edges, frozenset)

    assert isinstance(graph.nodes, frozenset)


# INVALID CASES


def test_graph_raises_when_does_not_have_nodes(make_node: MakeNode) -> None:
    node = make_node()

    with pytest.raises(HasNoNodesGraphError):
        Graph(edges=frozenset(), nodes=frozenset(), root_id=node.id)


def test_graph_raises_when_root_is_not_in_nodes(make_node: MakeNode) -> None:
    node = make_node()

    with pytest.raises(RootNotInNodesGraphError):
        Graph(edges=frozenset(), nodes=frozenset({node}), root_id=uuid4())
