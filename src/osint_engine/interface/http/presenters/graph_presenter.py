from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.interface.http.presenters.edge_presenter import edge_to_schema
from osint_engine.interface.http.presenters.node_presenter import node_to_schema
from osint_engine.interface.http.presenters.revision_presenter import (
    revision_to_schema,
)
from osint_engine.interface.http.schemas.graph_catalog_schema import (
    GraphCatalogEntrySchema,
    GraphCatalogSchema,
)
from osint_engine.interface.http.schemas.graph_schema import GraphSchema

if TYPE_CHECKING:
    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.domain.entities.bases.graph import Graph


def graph_to_schema(revision: EntityRevision[Graph], /) -> GraphSchema:
    graph = revision.entity
    revision_schema = revision_to_schema(revision)

    return GraphSchema(
        content_id=graph.content_id,
        edges=[edge_to_schema(edge, revision=revision_schema) for edge in graph.edges],
        nodes=[node_to_schema(node, revision=revision_schema) for node in graph.nodes],
        revision=revision_schema,
        root_id=graph.root_id,
    )


def graph_catalog_to_schema(
    entries: tuple[tuple[EntityRevision[Graph], ...], ...], /
) -> GraphCatalogSchema:
    return GraphCatalogSchema(
        entries=[_catalog_entry_to_schema(entry) for entry in entries]
    )


def _catalog_entry_to_schema(
    entry: tuple[EntityRevision[Graph], ...], /
) -> GraphCatalogEntrySchema:
    latest = entry[-1]
    graph = latest.entity
    root = next(node for node in graph.nodes if node.id == graph.root_id)

    return GraphCatalogEntrySchema(
        first_fetched_at=entry[0].fetched_at,
        last_fetched_at=latest.fetched_at,
        providers=sorted({revision.provider for revision in entry}),
        revision_count=len(entry),
        root=node_to_schema(root, revision=revision_to_schema(latest)),
    )
