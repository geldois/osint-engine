from uuid import UUID

from pydantic import BaseModel

from osint_engine.interface.http.schemas.edge_schema import EdgeUnion
from osint_engine.interface.http.schemas.node_schema import NodeUnion


class GraphSchema(BaseModel):
    root_id: UUID
    nodes: list[NodeUnion]
    edges: list[EdgeUnion]
