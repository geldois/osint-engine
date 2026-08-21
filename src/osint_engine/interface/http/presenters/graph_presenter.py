from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.interface.http.presenters.edge_presenter import edge_to_schema
from osint_engine.interface.http.presenters.node_presenter import node_to_schema
from osint_engine.interface.http.schemas.graph_schema import GraphSchema
from osint_engine.interface.http.schemas.revision_schema import RevisionSchema

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.domain.entities.bases.entity import Entity
    from osint_engine.domain.entities.bases.graph import Graph


def revision_to_schema(revision: EntityRevision[Entity[UUID]], /) -> RevisionSchema:
    return RevisionSchema(
        fetched_at=revision.fetched_at,
        merged_at=revision.merged_at,
        provider=revision.provider,
    )


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
