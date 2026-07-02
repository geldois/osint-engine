from __future__ import annotations

from uuid import UUID  # noqa: TC003

from pydantic import BaseModel

from osint_engine.interface.http.schemas.edge_schema import EdgeUnion  # noqa: TC001
from osint_engine.interface.http.schemas.node_schema import NodeUnion  # noqa: TC001


class GraphSchema(BaseModel):
    root_id: UUID
    nodes: list[NodeUnion]
    edges: list[EdgeUnion]
