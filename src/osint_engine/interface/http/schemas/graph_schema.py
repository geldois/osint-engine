from __future__ import annotations

from uuid import UUID  # noqa: TC003

from pydantic import BaseModel

from osint_engine.interface.http.schemas.edge_schema import EdgeUnion  # noqa: TC001
from osint_engine.interface.http.schemas.node_schema import NodeUnion  # noqa: TC001
from osint_engine.interface.http.schemas.revision_schema import (  # noqa: TC001
    RevisionSchema,
)


class GraphSchema(BaseModel):
    content_id: UUID
    edges: list[EdgeUnion]
    nodes: list[NodeUnion]
    revision: RevisionSchema
    root_id: UUID
