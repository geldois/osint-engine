from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.interface.http.fastapi.presenters.edge_presenter import edge_to_schema
from osint_engine.interface.http.fastapi.presenters.node_presenter import node_to_schema
from osint_engine.interface.http.fastapi.schemas.graph_schema import GraphSchema

if TYPE_CHECKING:
    from osint_engine.domain.entities.bases.graph import Graph


def graph_to_schema(graph: Graph, /) -> GraphSchema:
    return GraphSchema(
        root_id=graph.root_id,
        nodes=[node_to_schema(node) for node in graph.nodes],
        edges=[edge_to_schema(edge) for edge in graph.edges],
    )
