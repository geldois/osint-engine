from __future__ import annotations

from datetime import datetime  # noqa: TC003

from pydantic import BaseModel

from osint_engine.interface.http.schemas.node_schema import NodeUnion  # noqa: TC001


class GraphCatalogEntrySchema(BaseModel):
    first_fetched_at: datetime
    last_fetched_at: datetime
    providers: list[str]
    revision_count: int
    root: NodeUnion


class GraphCatalogSchema(BaseModel):
    entries: list[GraphCatalogEntrySchema]
